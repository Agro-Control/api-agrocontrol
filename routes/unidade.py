from fastapi import APIRouter
from model.unidade_model import Unidade
from service.unidade_service import UnidadeService
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/unidades/{id_unidade}", response_model=Unidade)
def busca_unidade(id_unidade: int)-> Unidade:
    
    if not id_unidade:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()

    response = unidade_service.buscar_unidade(id_unidade)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Unidade não encontrada"})

    return response


@router.get("/unidades")
def busca_unidades(id_empresa: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade"),
                    codigo: str = Query(None, description= "Nome/Codigo da Unidade")):
    
    unidade_service = UnidadeService()

    response = unidade_service.buscar_unidades(id_empresa=id_empresa, status=status,codigo=codigo)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Unidades não encontradas"})

    return {"unidades": response}
 
@router.post("/unidades")
def inserir_unidade(unidade: Unidade):
    
    if not unidade:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    unidade_service.inserir_unidade(unidade)
    
    return Response(status_code=201)

@router.put("/unidades")
def atualiza_unidade(unidade: Unidade):

    if not unidade or not unidade.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    response = unidade_service.altera_unidade(unidade)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar unidade."})

    return response

