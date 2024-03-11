from motor.motor_asyncio import AsyncIOMotorClient
from errors import DatabaseError

def get_conn_str():
    return "mongodb://mongodb:27017/"

class Mongo:
    def __init__(self) -> None:
        self._uri = get_conn_str()

    async def __aenter__(self):
        try:
            self.client = AsyncIOMotorClient(self._uri, )
            return self.client
        except Exception as e:
            raise DatabaseError(e)

    async def __aexit__(self, exc_type, exc, tb):
        self.client.close()
