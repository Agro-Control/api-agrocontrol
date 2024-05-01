from fastapi import APIRouter
from service.empresa_service import EmpresaService
from model.empresa_model import Empresa
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query

router = APIRouter()



@router.get("/empresas/{id_empresa}", response_model=Empresa)
def busca_empresa(id_empresa: int)-> Empresa:
    
    if not id_empresa:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()

    response = empresa_service.buscar_empresa(id_empresa)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 403, content={"error": "Empresa não encontrada"})

    return response


@router.get("/empresas")
def busca_empresas(status: str = Query(None, description="Status da Empresa"),
                   codigo: str = Query(None, description= "Nome/Codigo da Empresa"),
                   estado: str = Query(None, description= "Nome do Estado da Empresa"),
                   ):

    empresa_service = EmpresaService()

    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    response = empresa_service.buscar_empresas(status=status,codigo=codigo, estado=estado)

    if not response:
        return JSONResponse(status_code= 403, content={"error": "Empresas não encontradas"})

    return {"empresas": response}
 
@router.post("/empresas")
def inserir_empresa(empresa: Empresa):
    
    if not empresa:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()
    
    
    empresa_service.inserir_empresa(empresa)
    
    return Response(status_code=200)

@router.put("/empresas")
def atualiza_empresa(empresa: Empresa):

    if not empresa or not empresa.id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()
    
    response = empresa_service.altera_empresa(empresa)
    if not response:
        return JSONResponse(status_code= 403, content={"error": "Erro ao atualizar empresa."})

    return response


@router.get("/estados_empresa")
def busca_estados_empresas(
            id_grupo: int = Query(None, description="id do grupo empresarial"),
            id_empresa: int = Query(None, description= "id da empresa")
        ):

    empresa_service = EmpresaService()
    
    result = empresa_service.busca_estado_empresas(id_grupo, id_empresa)
    
    return result
