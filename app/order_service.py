from app.mail_service import send_email


def operate_product_order(product, cur, con):
    cur.execute(f"""
        UPDATE Stock
        SET remaining_amount = remaining_amount - {product.amount}
        WHERE product_id = {product.id};
    """)
    con.commit()


def operate_system_order(system, cur, con):
    cur.execute(f"""
            SELECT * FROM System 
            INNER JOIN Product ON Product.id = System.product_id
            WHERE system_id = {system.id};
        """)
    res = cur.fetchall()

    for system_item in res:
        cur.execute(f"""
            UPDATE Stock
            SET remaining_amount = remaining_amount - {system_item[3] * system.amount}
            WHERE product_id = {system_item[2]};
        """)
        con.commit()


def add_product_to_order(product, order_id, cur, con):
    cur.execute(f"""
            INSERT INTO CustomerOrder (order_id, product_id, product_amount)
            VALUES(%s,%s,%s);
        """, (order_id, product.id, product.amount))
    con.commit()


def add_system_to_order(system, order_id, cur, con):
    cur.execute(f"""
            INSERT INTO CustomerOrder (order_id, system_id, system_amount)
            VALUES(%s,%s,%s);
        """, (order_id, system.id, system.amount))
    con.commit()


def handle_stock_status_notification(cur, con):
    cur.execute(f"""
            SELECT * FROM Stock 
            INNER JOIN Product ON Product.id = Stock.product_id;
        """)
    stock_list = cur.fetchall()
    for stock_item in stock_list:
        remaining_amount = stock_item[2]
        total_amount = stock_item[3]
        product_id = stock_item[1]
        product_name = stock_item[6]
        if total_amount > 0:
            is_low_stock = (100 * remaining_amount)/total_amount < 20
            if is_low_stock and get_low_stock_reported(product_id, cur) == False:
                send_email(product_name, cur)
                update_stock_report_status(product_id, cur, con)


def get_low_stock_reported(product_id, cur):
    cur.execute(f"""
            SELECT low_stock_reported FROM Stock 
            WHERE product_id = {product_id};
        """)
    res = cur.fetchone()
    return res[0]


def update_stock_report_status(product_id, cur, con):
    cur.execute(f"""
      UPDATE Stock
      SET low_stock_reported = True
      WHERE product_id = {product_id};
  """)
    con.commit()
