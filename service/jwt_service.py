from typing import List
import secrets
import string
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import smtplib
from email.message import EmailMessage
import bcrypt

class AuthValidation(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl)
        self.request_form_class = OAuth2PasswordRequestForm

oauth2_scheme = AuthValidation(tokenUrl="login")

def gerar_senha_aleatoria(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def enviar_email(destinatario, senha):
    msg = EmailMessage()
    msg['Subject'] = "AgroControl - Sua nova senha"
    msg['From'] = "vinie.antuness@gmail.com"
    msg['To'] = destinatario
    msg.set_content(f"Sua senha temporária é: {senha}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('vinie.antuness@gmail.com', 'ahkgbjikxyxzcscm')
        smtp.send_message(msg)

def criptografar_senha(senha):
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return senha_hash

def token_24horas(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "segredo", algorithm="HS256")
    return encoded_jwt

def verify_token(required_type: List[str]):
    def verify(token: str = Depends(oauth2_scheme)):
        try:
            # Decodificar e validar o token JWT (substituir pela lógica de validação real)
            payload = jwt.decode(token, "segredo", algorithms=["HS256"])
            user_tipo: str = payload.get("tipo")
            if user_tipo is None or user_tipo not in required_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Acesso não autorizado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            expire_time = datetime.fromtimestamp(payload["exp"])
            if expire_time < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Acesso não autorizado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user_tipo

        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return verify




