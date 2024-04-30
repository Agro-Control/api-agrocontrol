import jwt
from datetime import datetime, timedelta

def token_24horas(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "segredo", algorithm="HS256")
    return encoded_jwt
