from fastapi import APIRouter
from service.maquina_service import MaquinaService
from model.maquina_model import Maquina
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query


router = APIRouter()

@router.get("/maquinas/{maquina_id}")
def busca_maquina(maquina_id: int):

    if not maquina_id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquina(maquina_id)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Maquina não encontrada"})

    return response


@router.get("/maquinas")
def busca_maquinas(unidade_id: int = Query(None, description="Unidade da Maquina"), 
                   status: str = Query(None, description="Status da Maquina"),
                   codigo: str = Query(None, description= "Nome/Codigo da Maquina")):

    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquinas(unidade_id=unidade_id, status= status, codigo=codigo)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Maquina não encontrada"})

    return {"maquinas": response}



@router.post("/maquinas")
def inserir_maquinas(maquina: Maquina):

    if not maquina:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    

    maquina_service = MaquinaService()

    maquina_service.inserir_maquina(maquina)
    
    return Response(status_code=201)
    


@router.put("/maquinas")
def atualizar_maquina(maquina: Maquina):

    if not maquina or not maquina.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    maquina_service = MaquinaService()

    response = maquina_service.altera_maquina(maquina)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return response




