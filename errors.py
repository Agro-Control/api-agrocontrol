import logging
from fastapi import HTTPException
import traceback

class ApiExceptionHandler:
    
    @staticmethod
    
    async def handler(exception: Exception):
        if isinstance(exception, DatabaseError):
            logging.error(f"Database Error, traceback: {traceback.format_exc()}, exception: {exception}")
        elif isinstance(exception, EventError):
            logging.error(f"Event Error: traceback: {traceback.format_exc()}, exception: {exception}")

        else:
            logging.error(f"traceback: {traceback.format_exc()}, exception: {exception}")
        
        return HTTPException(status_code=500, detail="Internal server error!")


class DatabaseError(Exception):
    pass


class EventError(Exception):
    pass
