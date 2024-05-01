from fastapi import APIRouter
from service.ordem_service import OrdemService
from model.ordem_de_servico_model import OrdemServico
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query


router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello word 2"}

@router.get("/ordem/maquina/{id_maquina}/ativa")
def ordem_maquina_ativa(id_maquina: int):
    
    if not id_maquina:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()
    response = ordem_service.busca_ordem_ativa_maquina(id_maquina)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})
    
    return JSONResponse(status_code=200, content=response.dict())

@router.get("/ordens/{id_ordem}")
def busca_ordem(id_ordem:int):
    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = ordem_service.busca_ordem_servico(id_ordem)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})

    return response


@router.get("/ordens")
def buscar_ordens(id_empresa: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade")):

    ordem_service = OrdemService()

    response = ordem_service.busca_ordens_servicos(id_empresa=id_empresa, status=status)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Ordens não encontradas"})

    return {"ordens_servico": response}


@router.post("/ordens")
def inserir_ordem(ordem: OrdemServico):

    if not ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    ordem_service.inserir_ordem_servico(ordem)
    
    return Response(status_code=201)


@router.put("/ordens")
def atualizar_ordem(ordem: OrdemServico):
    if not ordem or not ordem.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = ordem_service.altera_ordem_servico(ordem)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar ordem servico."})

    return response


