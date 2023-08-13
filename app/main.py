from fastapi import FastAPI, HTTPException
from app.entities import Product, ProductAmountUpdate, SystemProductList, Order
from app.db_setup import build_tables, get_db_connection
from app.utils import get_current_ms_time, getSystemsJson, getProductsJson, is_valid_products, is_valid_systems

con = get_db_connection()
cur = con.cursor()
build_tables(cur)
app = FastAPI()


@app.get('/product')
def get_all_products_from_db():
    try:
        cur.execute("SELECT * FROM Product;")
        result = cur.fetchall()
        return getProductsJson(result)
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. get_all_products_from_db')


@app.get('/system')
def get_all_systems_from_db():
    try:
        cur.execute("""
                SELECT * FROM System 
                INNER JOIN Product ON Product.id = System.product_id;
            """)
        response = cur.fetchall()
        return getSystemsJson(response)
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. get_all_systems_from_db')


@app.put('/product/{product_id}')
def update_product_amount(product_id: str, product: ProductAmountUpdate):
    try:
        cur.execute(f"""
                UPDATE Product
                SET amount = {product.amount}
                WHERE id = {product_id};
            """)
        con.commit()
        return HTTPException(
            status_code=200, detail='Product stock was successfully updated')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. update_product_amount')


@app.post('/product')
def add_new_product(product: Product):
    try:
        # TODO check is product with same name is already in DB
        cur.execute(f"""
                    INSERT INTO Product (name, amount)
                    VALUES(%s,%s);
                """, (product.name, product.amount))
        con.commit()
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


@app.post('/order')
def make_new_order(orderItem: Order):
    try:
        if is_valid_products(orderItem.products, cur) and is_valid_systems(orderItem.systems, cur):
            order_id = get_current_ms_time()
            for product in orderItem.products:
                addProductToOrder(product, order_id)
                operateProductOrder(product)
            for system in orderItem.systems:
                addSystemToOrder(system, order_id)
                operateSystemOrder(system)
        else:
            return HTTPException(
                status_code=500, detail='Order is not valid. Check IDs of products and systems.')
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error. make_new_order')


def operateProductOrder(product):
    cur.execute(f"""
        UPDATE Product
        SET amount = amount - {product.amount}
        WHERE id = {product.id};
    """)
    con.commit()


def operateSystemOrder(system):
    cur.execute(f"""
            SELECT * FROM System 
            INNER JOIN Product ON Product.id = System.product_id
            WHERE system_id = {system.id};
        """)
    res = cur.fetchone()

    cur.execute(f"""
        UPDATE Product
        SET amount = amount - {res[3] * system.amount}
        WHERE id = {res[2]};
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
