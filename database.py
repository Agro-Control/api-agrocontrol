# database.py
import psycopg
from psycopg import Error

def get_conn_str():
    return f"""
    dbname=postgres
    user=postgres
    password=postgres
    host=localhost
    port=5432
    """

def get_db_connection():
    try:
        connection = psycopg.connect(get_conn_str())
        return connection
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

