from datetime import timedelta
from fastapi import HTTPException, Depends
from fastapi import FastAPI
from model.login_model import Login
from service.jwt_service import token_24horas, verify_token
from errors import ApiExceptionHandler
from service.usuario_service import UsuarioService
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.ordem import router as ordem_router
from routes.unidade import router as unidade_router
from routes.empresa import router as empresa_router
from routes.maquina import router as maquina_router
from routes.talhao import router as talhao_router
from routes.usuario import router as usuario_router
from routes.evento import router as evento_router
from routes.grupo import router as grupo_router
from routes.dashboard import router as dash_router

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
app.include_router(usuario_router)
app.include_router(evento_router)
app.include_router(grupo_router)
app.include_router(dash_router)

@app.get("/")
async def root():
    return {"message": "Hello word"}


@app.post("/login")
def login(login: Login):
    
    usuario_service = UsuarioService()
    usuario = usuario_service.validar_credenciais(login.login, login.senha)
    
    if usuario:
        # Remover a senha do objeto de usuário
        usuario.senha = None  # ou "" ou qualquer outro valor que você preferir

        # Gerar token JWT
        tempo_token = timedelta(minutes=1440)
        token = token_24horas(data={"sub": usuario.email, "tipo": usuario.tipo, "id": usuario.id}, expires_delta=tempo_token)
        
        # Retorna o usuário junto com o token JWT
        return {"token": token}
    else:
        # Retornar manualmente o erro 401
        raise HTTPException(status_code=401, detail="Credenciais inválidas")


# rota para revalidar usuario logado, deve morrer dps
@app.get("/usersession/{id}")
def user_logado(id: int, token: str = Depends(verify_token(["D", "G", "O"]))):

    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    usuario_service = UsuarioService()
    usuario = usuario_service.busca_usuario(id)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    usuario.senha = None

    return usuario
