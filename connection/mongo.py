from motor.motor_asyncio import AsyncIOMotorClient

class Mongo:
    def __init__(self) -> None:
        self.uri = "mongodb://localhost:27017/"

    async def __aenter__(self):
        self.client = AsyncIOMotorClient(self.uri, )
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        print("Fechou conn")
        self.client.close()
