import time
import psycopg2
from fastapi import HTTPException
from datetime import datetime, timedelta
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
    if len(product_list):
        for product in product_list:
            cur.execute(f"SELECT * FROM Product WHERE id = {product.id};")
            rs = cur.fetchone()
            if not rs:
                is_valid = False
    return is_valid


def is_valid_systems(system_list, cur):
    is_valid = True
    if len(system_list):
        for system in system_list:
            cur.execute(f"SELECT * FROM System WHERE system_id = {system.id};")
            rs = cur.fetchone()
            if not rs:
                is_valid = False
    return is_valid
