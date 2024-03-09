import psycopg
from psycopg import Error
from psycopg.rows import dict_row, tuple_row

def get_conn_str():
    return f"""
    dbname=postgres
    user=postgres
    password=postgres
    host=localhost
    port=5432
    """

class Database:
    
    def __enter__(self):
        self.conn = get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, 'conn') and self.conn is not None:
            print("Fechou conn postgres")
            self.conn.close()

    @staticmethod
    def get_cursor_type(type="tulpe"):
        return dict_row if type == "dict" else tuple_row

def get_db_connection(dict = False):
    try:
        return psycopg.connect(get_conn_str(), row_factory= dict_row if dict else tuple_row)
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

