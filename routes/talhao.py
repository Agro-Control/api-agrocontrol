from fastapi import APIRouter
from service.talhao_service import TalhaoService
from model.talhao_model import Talhao
from fastapi.responses import JSONResponse
from fastapi import Response, Query


router = APIRouter()


@router.get("/talhoes/{talhao_id}")
def busca_talhao(talhao_id:int):

    if not talhao_id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    talhao_service = TalhaoService()

    response = talhao_service.buscar_talhao(talhao_id)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return response


@router.get("/talhoes")
def busca_talhoes(unidade_id:int = Query(None, description="Empresa do talhao"),  
                 status: str = Query(None, description="Status do Talhão"),
                codigo: str = Query(None, description= "Nome/Codigo do Talhão")):


    talhao_service = TalhaoService()

    response = talhao_service.buscar_talhoes(unidade_id=unidade_id, codigo=codigo, status=status)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return {"talhoes": response}


@router.post("/talhoes")
def inserir_talhao(talhao: Talhao):
    if not talhao:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    talhao_service = TalhaoService()
    
    talhao_service.inserir_talhao(talhao)

    return Response(status_code=201)


@router.put("/talhoes")
def atualizar_talhao(talhao: Talhao):

    if not talhao or not talhao.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    talhao_service = TalhaoService()

    response = talhao_service.altera_talhao(talhao)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar talhao."})

    return response
