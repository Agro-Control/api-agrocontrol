from datetime import timedelta
from fastapi import HTTPException
from fastapi import FastAPI
from model.login_model import Login
from service.jwt_service import token_24horas
from errors import ApiExceptionHandler
from service.usuario_service import UsuarioService
from fastapi.middleware.cors import CORSMiddleware

from routes.ordem import router as ordem_router
from routes.unidade import router as unidade_router
from routes.empresa import router as empresa_router
from routes.maquina import router as maquina_router
from routes.talhao import router as talhao_router
from routes.gestor import router as gestor_router
from routes.operador import router as operador_router
from routes.evento import router as evento_router
from routes.grupo import router as grupo_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return await ApiExceptionHandler.handler(exc)

app.include_router(ordem_router)
app.include_router(unidade_router)
app.include_router(empresa_router)
app.include_router(maquina_router)
app.include_router(talhao_router)
app.include_router(gestor_router)
app.include_router(operador_router)
app.include_router(evento_router)
app.include_router(grupo_router)


@app.get("/")
async def root():
    return {"message": "Hello word"}


@app.post("/login")
def login(login: Login):
    
    usuario_service = UsuarioService()
    usuario = usuario_service.validar_credenciais(login.email, login.senha)
    
    if usuario:
        # Remover a senha do objeto de usuário
        usuario.senha = None  # ou "" ou qualquer outro valor que você preferir

        # Gerar token JWT
        tempo_token = timedelta(minutes=60)
        token = token_24horas(data={"sub": usuario.email}, expires_delta=tempo_token)
        
        # Retorna o usuário junto com o token JWT
        return {"usuario": usuario, "token": token}
    else:
        # Retornar manualmente o erro 401
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
