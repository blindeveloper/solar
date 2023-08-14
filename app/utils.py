import time
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_current_ms_time():
    return round(time.time() * 1000)


def getSystemsJson(response):
    list = {}
    for system in response:
        if system[1] not in list:
            list[system[1]] = []

        list[system[1]].append({
            'name': system[5],
            'amount': system[3]
        })
    return list


def getStockJson(response):
    list = {}
    for stock_item in response:
        list[stock_item[0]] = {
            'product_id': stock_item[1],
            'product_name': stock_item[5],
            'remaining_amount': stock_item[2],
            'total_amount': stock_item[3],
        }
    return list


def getProductsJson(response):
    list = {}
    for product in response:
        list[product[0]] = {
            'name': product[1],
            'amount': product[2]
        }
    return list


def is_valid_products(product_list, cur):
    is_valid = True
    list_of_ids = []
    if len(product_list):
        for product in product_list:
            list_of_ids.append(product.id)

        cur.execute(
            f"SELECT * FROM Product WHERE id = ANY(ARRAY{list_of_ids});")

        rs = cur.fetchall()
        if len(rs) != len(product_list):
            is_valid = False
    return is_valid


def is_valid_systems(system_list, cur):
    is_valid = True
    list_of_ids = []

    if len(system_list):
        for system in system_list:
            list_of_ids.append(system.id)

        cur.execute(
            f"SELECT * FROM System WHERE system_id = ANY(ARRAY{list_of_ids});")
        rs = cur.fetchall()
        if len(rs) != len(system_list):
            is_valid = False
    return is_valid
