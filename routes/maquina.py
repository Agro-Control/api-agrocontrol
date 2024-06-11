from fastapi import APIRouter, Depends

from service.jwt_service import verify_token
from service.maquina_service import MaquinaService
from service.evento_service import EventoService
from model.maquina_model import Maquina
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query


router = APIRouter()

@router.get("/maquinas/{maquina_id}")
def busca_maquina(maquina_id: int, token: str = Depends(verify_token(["G"]))):

    if not maquina_id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquina(maquina_id)
    
    if not response:
        return JSONResponse(status_code=404, content={"error": "Maquina não encontrada"})

    return response


@router.get("/maquinas")
def busca_maquinas(unidade_id: int = Query(None, description="Unidade da Maquina"),
                   empresa_id: int = Query(None, description="Empresa da Maquina"),
                   status: str = Query(None, description="Status da Maquina"),
                   codigo: str = Query(None, description="Nome/Codigo da Maquina"),
                   diponibilidade_ordem: bool = Query(None, description="Maquinas livres para ordem"),
                   ):

    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquinas(unidade_id=unidade_id, empresa_id=empresa_id,
                                               status=status, codigo=codigo, diponibilidade_ordem= diponibilidade_ordem)
    
    if not response:
        return JSONResponse(status_code=404, content={"error": "Maquina não encontrada"})

    return {"maquinas": response}



@router.post("/maquinas")
def inserir_maquinas(maquina: Maquina, token: str = Depends(verify_token(["G"]))):

    if not maquina:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    

    maquina_service = MaquinaService()

    maquina_service.inserir_maquina(maquina)
    
    return Response(status_code=201)
    

@router.put("/maquinas")
def atualizar_maquina(maquina: Maquina, token: str = Depends(verify_token(["G"]))):

    if not maquina or not maquina.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    maquina_service = MaquinaService()

    response = maquina_service.altera_maquina(maquina)
    
    if not response:
        return JSONResponse(status_code=404, content={"error": "Erro ao atualizar empresa."})

    return response


@router.get("/maquinas/info/{maquina_id}")
async def busca_info_maquina(maquina_id: int, token: str = Depends(verify_token(["G"]))):
    if not maquina_id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    evento_service = EventoService()

    response = evento_service.info_maquina(maquina_id)

    return response

