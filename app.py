from typing import Dict, List, Optional
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse
from model.ordem_de_servico_model import OrdemServico
from model.unidade_model import Unidade
from service.ordem_service import OrdemService
from errors import ApiExceptionHandler
from service.unidade_service import UnidadeService
from pydantic import BaseModel

app = FastAPI()

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return await ApiExceptionHandler.handler(exc)

@app.get("/")
async def root():
    return {"message": "Hello word"}

@app.get("/ordem/maquina/{id_maquina}/ativa")
def ordem_maquina_ativa(id_maquina: int):
    
    if not id_maquina:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()
    response = ordem_service.busca_ordem_ativa_maquina(id_maquina)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})
    
    return JSONResponse(status_code=200, content=response.dict())


@app.get("/eventos/{id_ordem}")
async def eventos_por_ordem(id_ordem: int):

    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    eventos = await ordem_service.busca_eventos_ordem(id_ordem)
        
    return JSONResponse(status_code=200, content=eventos)


@app.get("/unidades/{id_unidade}", response_model=Unidade)
def busca_unidade(id_unidade: int)-> Unidade:
    
    if not id_unidade:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()

    response = unidade_service.buscar_unidade(id_unidade)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Unidade não encontrada"})

    return response


@app.get("/unidades")
def busca_unidades(status: str = Query(None, description="Status da Unidade"),
                   codigo: str = Query(None, description= "Nome/Codigo da Unidade")):

    unidade_service = UnidadeService()

    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    response = unidade_service.buscar_unidades(status=status,codigo=codigo)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Unidades não encontradas"})

    return {"unidades": response}
 
@app.post("/unidades")
def inserir_unidade(unidade: Unidade):
    
    if not unidade:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    
    unidade_service.inserir_unidade(unidade)
    
    return Response(status_code=201)

@app.put("/unidades")
def atualiza_unidade(unidade: Unidade):

    if not unidade or not unidade.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    unidade_service = UnidadeService()
    
    response = unidade_service.altera_unidade(unidade)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar unidade."})

    return response


@app.post("/eventos")
async def eventos(request: Request):
    data = await request.json()
    
    if not data:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})
    
    ordem_service = OrdemService()
    await ordem_service.insere_evento(data)
    return Response(status_code=204)

