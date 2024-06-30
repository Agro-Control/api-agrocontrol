from fastapi import APIRouter, Depends
from service.grupo_service import GrupoService
from model.grupo_model import Grupo
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query
from service.jwt_service import verify_token

router = APIRouter()


@router.get("/grupos/{grupo_id}", response_model=Grupo)
async def busca_grupo(grupo_id: int, token: str = Depends(verify_token(["G", "D"])))-> Grupo:
    
    if not grupo_id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()

    response = await grupo_service.buscar_grupo(grupo_id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 403, content={"error": "Grupo não encontrada"})

    return response


@router.get("/grupos")
async def busca_grupos(token: str = Depends(verify_token(["D"]))):

    grupo_service = GrupoService()

    response = await grupo_service.buscar_grupos()

    if not response:
        return JSONResponse(status_code= 403, content={"error": "Grupos não encontradas"})

    return {"grupos": response}
 
@router.post("/grupos")
async def inserir_grupo(grupo: Grupo, token: str = Depends(verify_token(["D"]))):
    
    if not grupo:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()
    
    await grupo_service.inserir_grupo(grupo)
    
    return Response(status_code=200)

@router.put("/grupo")
async def atualiza_grupo(grupo: Grupo, token: str = Depends(verify_token(["D"]))):

    if not grupo or not grupo.id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    grupo_service = GrupoService()
    
    response = await grupo_service.altera_grupo(grupo)
    if not response:
        return JSONResponse(status_code=403, content={"error": "Erro ao atualizar grupo."})

    return response
