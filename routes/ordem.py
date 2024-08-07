from fastapi import APIRouter, Depends

from service.jwt_service import verify_token
from service.ordem_service import OrdemService
from model.ordem_de_servico_model import OrdemServico
from model.ordem_alocacao import OrdemAlocacao
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello word 2"}

@router.get("/ordem/maquina/ativa")
async def ordem_maquina_ativa(maquina: str, usuario: int, ):

    if not maquina or not usuario:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()
    response = await ordem_service.busca_ordem_ativa_maquina(maquina, usuario)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})
    
    return response


@router.post("/ordem/alocar_operador_maquina")
async def ordem_alocar_operador_maquina(ordem_alocacao: OrdemAlocacao):

    if not ordem_alocacao:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()
    response = await ordem_service.alocar_recurso(ordem_alocacao)

    return JSONResponse(status_code=201, content={"id": str(response)})


@router.delete("/ordem/alocar_operador_maquina")
async def ordem_desalocar_operador_maquina(id: str):

    if not id:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()

    await ordem_service.desalocar_recurso(id)

    return JSONResponse(status_code=200, content={"detail": "ok"})


@router.get("/ordens/{id_ordem}")
async def busca_ordem(id_ordem:int, token: str = Depends(verify_token(["A", "G"]))):
    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = await ordem_service.busca_ordem_servico(id_ordem)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})

    return response


@router.get("/ordens")
async def buscar_ordens(empresa_id: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade"),
                  token: str = Depends(verify_token(["G", "D"]))):

    ordem_service = OrdemService()

    response = await ordem_service.busca_ordens_servicos(empresa_id=empresa_id, status=status)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Ordens não encontradas"})

    return {"ordens_servico": response}


@router.post("/ordens")
async def inserir_ordem(ordem: OrdemServico, token: str = Depends(verify_token(["G"]))):

    if not ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = await ordem_service.inserir_ordem_servico(ordem)

    return Response(status_code=response)


@router.put("/ordens")
async def atualizar_ordem(ordem: OrdemServico, token: str = Depends(verify_token(["G"]))):

    if not ordem or not ordem.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = await ordem_service.altera_ordem_servico(ordem)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar ordem servico."})

    return response


