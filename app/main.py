from fastapi import FastAPI, HTTPException
from app.entities import Product, ProductStockUpdate, SystemProductList, Order
from app.db_setup import build_tables, get_db_connection
from app.utils import get_current_ms_time, getSystemsJson, getProductsJson, is_valid_products, is_valid_systems, getStockJson

con = get_db_connection()
cur = con.cursor()
build_tables(cur)
app = FastAPI()


@app.get('/product')
def get_all_products():
    try:
        cur.execute("SELECT * FROM Product;")
        result = cur.fetchall()
        return getProductsJson(result)
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. get_all_products')


@app.get('/stock')
def get_stock_status():
    try:
        cur.execute(
            """SELECT * FROM Stock 
                INNER JOIN Product ON Product.id = Stock.product_id;""")
        result = cur.fetchall()
        return getStockJson(result)

    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. get_all_products')


@app.get('/system')
def get_all_systems():
    try:
        cur.execute("""
                SELECT * FROM System 
                INNER JOIN Product ON Product.id = System.product_id;
            """)
        response = cur.fetchall()
        return getSystemsJson(response)
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. get_all_systems')


@app.put('/stock/{product_id}')
def update_product_stock(product_id: str, product: ProductStockUpdate):
    try:
        cur.execute(f"""
                UPDATE Stock
                SET remaining_amount = {product.remaining_amount}, total_amount = {product.total_amount}
                WHERE product_id = {product_id};
            """)
        con.commit()
        return HTTPException(
            status_code=200, detail='Product stock was successfully updated')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. update_product_stock')


def is_product_in_db(product_name):
    cur.execute(f"SELECT * FROM Product WHERE name = '{product_name}';")
    if cur.fetchone() is None:
        return False
    else:
        return True


@app.post('/product')
def add_new_product(product: Product):
    try:
        if is_product_in_db(product.name):
            return HTTPException(
                status_code=500, detail='Product with the same name is already in the database, you can find it in stock.')
        else:
            cur.execute(f"""INSERT INTO Product (name)
                            VALUES(%s) RETURNING id;
                        """, (product.name,))
            created_product = cur.fetchone()

            cur.execute(
                f"""INSERT INTO Stock (product_id, remaining_amount, total_amount) 
                        VALUES(%s, %s, %s);""", (created_product[0], 0, 0))
            return HTTPException(
                status_code=200, detail='New product successfully added')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. add_new_product')


def add_products_to_system(system):
    next_id = get_current_ms_time()
    for product_item in system:
        cur.execute(f"""
            INSERT INTO System (system_id, product_id, amount)
            VALUES(%s,%s,%s);
        """, (next_id, product_item.id, product_item.amount))
        con.commit()


@app.post('/system')
def add_new_system(systemItem: SystemProductList):
    try:
        if is_valid_products(systemItem.system, cur):
            add_products_to_system(systemItem.system)
            return HTTPException(
                status_code=200, detail='New system successfully added')
        else:
            return HTTPException(
                status_code=500, detail='Product ID is not valid')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. add_new_system')


def get_systems_by_id(system_id):
    cur.execute(f"""
                SELECT * FROM System 
                INNER JOIN Product ON Product.id = System.product_id
                WHERE system_id = {system_id};
            """)
    return cur.fetchall()


def get_product_stock(map):
    product_id_list = []
    for key, value in map.items():
        product_id_list.append(key)
    cur.execute(f"""
                SELECT * FROM Stock 
                WHERE product_id = ANY(ARRAY{product_id_list});
            """)
    return cur.fetchall()


def get_order_map(orderItem):
    map = {}

    for system in orderItem.systems:
        sys_res = get_systems_by_id(system.id)
        for sys in sys_res:
            if sys[2] not in map:
                map[sys[2]] = sys[3] * system.amount
            else:
                map[sys[2]] = (map[sys[2]] + sys[3]) * system.amount

    for prod in orderItem.products:
        if prod.id not in map:
            map[prod.id] = prod.amount
        else:
            map[prod.id] = map[prod.id] + prod.amount

    return map


def is_valid_products_amounts_requested(orderItem):
    is_valid = True
    order_map = get_order_map(orderItem)
    product_stock = get_product_stock(order_map)
    for stock_item in product_stock:
        prod_id = stock_item[1]
        prod_remaining_amount = stock_item[2]
        if order_map[prod_id] > prod_remaining_amount:
            is_valid = False
    return is_valid


@app.post('/order')
def make_new_order(orderItem: Order):
    try:
        if is_valid_products(orderItem.products, cur) and is_valid_systems(orderItem.systems, cur):
            if is_valid_products_amounts_requested(orderItem):
                order_id = get_current_ms_time()
                for product in orderItem.products:
                    addProductToOrder(product, order_id)
                    operateProductOrder(product)
                for system in orderItem.systems:
                    addSystemToOrder(system, order_id)
                    operateSystemOrder(system)
                return HTTPException(
                    status_code=200, detail='Order is successfully added and handled.')
            else:
                return HTTPException(
                    status_code=500, detail='Order is not valid. To many products requested.')
        else:
            return HTTPException(
                status_code=500, detail='Order is not valid. Check IDs of products and systems.')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. make_new_order')


def operateProductOrder(product):
    cur.execute(f"""
        UPDATE Stock
        SET remaining_amount = remaining_amount - {product.amount}
        WHERE product_id = {product.id};
    """)
    con.commit()


def operateSystemOrder(system):
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


def addProductToOrder(product, order_id):
    cur.execute(f"""
            INSERT INTO CustomerOrder (order_id, product_id, product_amount)
            VALUES(%s,%s,%s);
        """, (order_id, product.id, product.amount))
    con.commit()


def addSystemToOrder(system, order_id):
    cur.execute(f"""
            INSERT INTO CustomerOrder (order_id, system_id, system_amount)
            VALUES(%s,%s,%s);
        """, (order_id, system.id, system.amount))
    con.commit()
