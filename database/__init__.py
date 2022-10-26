import os
import psycopg2
from utilities import get_abs_path, CONFIG

QUERY_PATH = get_abs_path("database", "queries")


def connect():
    connection = psycopg2.connect(database=CONFIG["DATABASE"]["database"],
                                  port=CONFIG["DATABASE"]["port"],
                                  host=CONFIG["DATABASE"]["host"],
                                  user=CONFIG["DATABASE"]["user"],
                                  password=CONFIG["DATABASE"]["password"]
                                  )
    return connection


def read_query(name, **kwargs):
    with open(os.path.join(QUERY_PATH, name.replace(".sql", "") + ".sql")) as q:
        sql = q.read().format(**kwargs)

    return sql


def execute_read_query(sql):
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                res = cur.fetchall()
                return res

    except Exception as e:
        print("I am unable to connect to the database")
        raise e


def execute_write_query(sql):
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()

    except Exception as e:
        print("I am unable to connect to the database")
        raise e


def run_query(name, mode="r", **kwargs):
    sql = read_query(name, **kwargs)
    if mode == "w":
        execute_write_query(sql)
    if mode == "r":
        res = execute_read_query(sql)
        return res


if __name__ == "__main__":
    res = execute_read_query("select version()")
    print(res)
