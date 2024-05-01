from fastapi import APIRouter
from service.usuario_service import UsuarioService
from model.usuario_model import Usuario
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict

router = APIRouter()

@router.get("/gestor/{id}", response_model=Usuario)
def busca_gestor(id: int)-> Usuario:
    
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    gestor_service = UsuarioService()

    response = gestor_service.buscar_gestor(id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Gestor não encontrada"})

    return response


@router.get("/gestores")
def busca_gestores(status: str = Query(None, description="Status do Gestor"),
                   codigo: str = Query(None, description= "Nome/Codigo do Gestor")):

    gestor_service = UsuarioService()

    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    response = gestor_service.buscar_gestores(status=status,codigo=codigo)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Gestores não encontrados"})

    return {"gestor": response}
 
@router.post("/gestores")
def inserir_gestor(gestor: Usuario):
    
    if not gestor:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    gestor_service = UsuarioService()
    
    gestor_service.inserir_gestor(gestor)
    
    return Response(status_code=201)

@router.put("/gestores")
def atualiza_gestor(gestor: Usuario):

    if not gestor or not gestor.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    gestor_service = UsuarioService()
    
    response = gestor_service.altera_gestor(gestor)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar gestor."})

    return response

