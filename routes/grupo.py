from fastapi import APIRouter
from service.grupo_service import GrupoService
from model.grupo_model import Grupo
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query

router = APIRouter()

@router.get("/grupos/{grupo_id}", response_model=Grupo)
def busca_grupo(grupo_id: int)-> Grupo:
    
    if not grupo_id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()

    response = grupo_service.buscar_grupo(grupo_id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 403, content={"error": "Grupo não encontrada"})

    return response


@router.get("/grupos")
def busca_grupos():

    grupo_service = GrupoService()

    response = grupo_service.buscar_grupos()

    if not response:
        return JSONResponse(status_code= 403, content={"error": "Grupos não encontradas"})

    return {"grupos": response}
 
@router.post("/grupos")
def inserir_grupo(grupo: Grupo):
    
    if not grupo:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()
    
    grupo_service.inserir_grupo(grupo)
    
    return Response(status_code=200)

@router.put("/grupo")
def atualiza_grupo(grupo: Grupo):

    if not grupo or not grupo.id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()
    
    response = grupo_service.altera_grupo(grupo)
    if not response:
        return JSONResponse(status_code= 403, content={"error": "Erro ao atualizar grupo."})

    return response
