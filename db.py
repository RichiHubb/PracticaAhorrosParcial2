import mysql.connector
from mysql.connector import pooling, errors
from config import Config

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    host=Config.DB_HOST,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)

def get_db_connection():
    try:
        return pool.get_connection()
    except errors.PoolError as e:
        print("Warning: connection pool exhausted, opening direct connection:", e)
        return mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
