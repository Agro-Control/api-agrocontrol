from fastapi import APIRouter, Depends
from model.unidade_model import Unidade
from service.jwt_service import verify_token
from service.unidade_service import UnidadeService
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/unidades/{unidade_id}", response_model=Unidade)
async def busca_unidade(unidade_id: int, token: str = Depends(verify_token(["G", "D"])))-> Unidade:
    
    if not unidade_id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()

    response = await unidade_service.buscar_unidade(unidade_id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Unidade não encontrada"})

    return response


@router.get("/unidades")
async def busca_unidades( grupo_id: int = Query(None, description="Grupo pertencente"),
                    empresa_id: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade"),
                    codigo: str = Query(None, description= "Nome/Codigo da Unidade"),
                    token: str = Depends(verify_token(["G", "D"]))):
    
    unidade_service = UnidadeService()

    response = await unidade_service.buscar_unidades(grupo_id=grupo_id,empresa_id=empresa_id, status=status,codigo=codigo)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Unidades não encontradas"})

    return {"unidades": response}
 
@router.post("/unidades")
async def inserir_unidade(unidade: Unidade, token: str = Depends(verify_token(["G", "D"]))):
    
    if not unidade:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    await unidade_service.inserir_unidade(unidade)
    
    return Response(status_code=201)

@router.put("/unidades")
async def atualiza_unidade(unidade: Unidade, token: str = Depends(verify_token(["G", "D"]))):

    if not unidade or not unidade.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    response = await unidade_service.altera_unidade(unidade)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar unidade."})

    return response


