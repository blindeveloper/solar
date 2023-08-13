import psycopg2
import os


def build_tables(cur):
    cur.execute(
        """CREATE TABLE IF NOT EXISTS Product(
          id SERIAL PRIMARY KEY NOT NULL,
          name VARCHAR(50) NOT NULL,
          amount INT NOT NULL);
        """)

    cur.execute(
        """CREATE TABLE IF NOT EXISTS System(
          id SERIAL PRIMARY KEY NOT NULL,
          system_id BIGINT NOT NULL,
          product_id INT NOT NULL,
          amount INT NOT NULL,
          FOREIGN KEY (product_id) REFERENCES Product (id));
        """)

    cur.execute(
        """CREATE TABLE IF NOT EXISTS CustomerOrder(
          id SERIAL PRIMARY KEY NOT NULL,
          order_id BIGINT NOT NULL,
          product_id INT,
          system_id BIGINT,
          system_amount INT,
          product_amount INT);
        """)


def get_db_connection():
    con = psycopg2.connect(user=os.environ["POSTGRES_USER"],
                           password=os.environ["POSTGRES_PASSWORD"],
                           host=os.environ["POSTGRES_HOST"],
                           port=os.environ["POSTGRES_PORT"],
                           database=os.environ["POSTGRES_DB"])
    return con
