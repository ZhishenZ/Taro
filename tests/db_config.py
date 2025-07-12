import os

DB_PARAMS = {
    "host": os.environ.get("PG", "postgres"),
    "port": 5432,
    "user": "taro_user",
    "password": "taro_password",
    "dbname": "taro_stock"
} 