from typing import Dict, List, Optional
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse
from model.maquina_model import Maquina
from model.ordem_de_servico_model import OrdemServico
from model.talhao_model import Talhao
from model.unidade_model import Unidade
from service.maquina_service import MaquinaService
from service.ordem_service import OrdemService
from errors import ApiExceptionHandler
from service.talhao_service import TalhaoService
from service.unidade_service import UnidadeService
from pydantic import BaseModel
from model.empresa_model import Empresa
from service.empresa_service import EmpresaService

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

@app.get("/ordens/{id_ordem}")
def busca_ordem(id_ordem:int):
    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = ordem_service.busca_ordem_servico(id_ordem)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})

    return response


@app.get("/ordens")
def buscar_ordens(id_empresa: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade")):

    
    ordem_service = OrdemService()

    response = ordem_service.busca_ordens_servicos(id_empresa=id_empresa, status=status)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Ordens não encontradas"})

    return {"ordens_servico": response}


@app.post("/ordens")
def inserir_ordem(ordem: OrdemServico):

    if not ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    ordem_service.inserir_ordem_servico(ordem)
    
    return Response(status_code=201)


@app.put("/ordens")
def atualizar_ordem(ordem: OrdemServico):
    if not ordem or not ordem.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    response = ordem_service.altera_ordem_servico(ordem)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar ordem servico."})

    return response

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
def busca_unidades(id_empresa: int = Query(None, description="Empresa pertencente"),
                    status: str = Query(None, description="Status da Unidade"),
                    codigo: str = Query(None, description= "Nome/Codigo da Unidade")):
    
    unidade_service = UnidadeService()

    response = unidade_service.buscar_unidades(id_empresa=id_empresa, status=status,codigo=codigo)

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

@app.get("/empresas/{id_empresa}", response_model=Empresa)
def busca_empresa(id_empresa: int)-> Empresa:
    
    if not id_empresa:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()

    response = empresa_service.buscar_empresa(id_empresa)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Empresa não encontrada"})

    return response


@app.get("/empresas")
def busca_empresas(status: str = Query(None, description="Status da Empresa"),
                   codigo: str = Query(None, description= "Nome/Codigo da Empresa")):

    empresa_service = EmpresaService()

    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    response = empresa_service.buscar_empresas(status=status,codigo=codigo)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Empresas não encontradas"})

    return {"empresas": response}
 
@app.post("/empresas")
def inserir_empresa(empresa: Empresa):
    
    if not empresa:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()
    
    
    empresa_service.inserir_empresa(empresa)
    
    return Response(status_code=201)

@app.put("/empresas")
def atualiza_empresa(empresa: Empresa):

    if not empresa or not empresa.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()
    
    response = empresa_service.altera_empresa(empresa)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return response



@app.get("/maquinas/{id_maquina}")
def busca_maquina(id_maquina: int):

    if not id_maquina:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquina(id_maquina)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Maquina não encontrada"})

    return response


@app.get("/maquinas")
def busca_maquinas(id_empresa: int = Query(None, description="Empresa da Maquina"), 
                   status: str = Query(None, description="Status da Maquina"),
                   codigo: str = Query(None, description= "Nome/Codigo da Maquina")):

    maquina_service = MaquinaService()

    response = maquina_service.buscar_maquinas(id_empresa=id_empresa, status= status, codigo=codigo)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Maquina não encontrada"})

    return {"maquinas": response}



@app.post("/maquinas")
def inserir_maquinas(maquina: Maquina):

    if not maquina or not maquina.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    

    maquina_service = MaquinaService()

    maquina_service.inserir_maquina(maquina)
    
    return Response(status_code=201)
    


@app.put("/maquinas")
def atualizar_maquina(maquina: Maquina):

    if not maquina or not maquina.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    maquina_service = MaquinaService()

    response = maquina_service.altera_maquina(maquina)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return response


@app.get("/talhoes/{id_talhao}")
def busca_talhao(id_talhao:int):

    if not id_talhao:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    talhao_service = TalhaoService()

    response = talhao_service.buscar_talhao(id_talhao)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return response


@app.get("/talhoes")
def busca_talhoes(id_empresa:int = Query(None, description="Empresa do talhao"),  
                 status: str = Query(None, description="Status da Maquina"),
                codigo: str = Query(None, description= "Nome/Codigo da Maquina")):


    talhao_service = TalhaoService()

    response = talhao_service.buscar_talhoes(id_empresa=id_empresa, codigo=codigo, status=status)
    
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar empresa."})

    return {"talhoes": response}


@app.post("/talhoes")
def inserir_talhao(talhao: Talhao):
    if not talhao:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    talhao_service = TalhaoService()
    
    talhao_service.inserir_talhao(talhao)

    return Response(status_code=201)


@app.put("/talhoes")
def atualizar_talhao(talhao: Talhao):

    if not talhao or not talhao.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    talhao_service = TalhaoService()

    response = talhao_service.altera_talhao(talhao)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar talhao."})

    return response

