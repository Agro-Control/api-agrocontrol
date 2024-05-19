import psycopg
from psycopg import Error
from psycopg.rows import dict_row, tuple_row
#from exception_handler import ErrorHandler
from errors import DatabaseError


def get_conn_str():
    return f"""
    dbname=postgres
    user=postgres
    password=postgres
    host=localhost
    port=5432
    """

class Database:

    def __init__(self) -> None:
        self._uri = get_conn_str()
    
    def __enter__(self):
        self.conn = self._get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, 'conn') and self.conn is not None:
            self.conn.close()

    def _get_db_connection(self, dict = False):
        try:
            return psycopg.connect(self._uri, row_factory= dict_row if dict else tuple_row)
        except (Exception, Error) as error:
            raise DatabaseError(error)

    @staticmethod
    def get_cursor_type(type="tulpe"):
        return dict_row if type == "dict" else tuple_row

