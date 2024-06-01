from fastapi import APIRouter, Depends
from service.empresa_service import EmpresaService
from model.empresa_model import Empresa
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query
from service.jwt_service import verify_token

router = APIRouter()



@router.get("/empresas/{empresa_id}", response_model=Empresa)
def busca_empresa(empresa_id: int, token: str = Depends(verify_token(["D", "G"]))) -> Empresa:
    
    if not empresa_id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()

    response = empresa_service.buscar_empresa(empresa_id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 403, content={"error": "Empresa não encontrada"})

    return response


@router.get("/empresas")
def busca_empresas(status: str = Query(None, description="Status da Empresa"),
                   codigo: str = Query(None, description="Nome/Codigo da Empresa"),
                   estado: str = Query(None, description="Nome do Estado da Empresa"),
                   grupo_id: int = Query(None, description="Grupo da Empresa"),
                    disp_gestor:bool = Query(None, description="Empresas sem gestor"),
                   token: str = Depends(verify_token(["D"]))
                   ):

    empresa_service = EmpresaService()

    response = empresa_service.buscar_empresas(status=status, codigo=codigo, estado=estado, disp=disp_gestor,
                                               grupo_id=grupo_id)

    if not response:
        return JSONResponse(status_code=403, content={"error": "Empresas não encontradas"})

    return {"empresas": response}
 
@router.post("/empresas")
def inserir_empresa(empresa: Empresa, token: str = Depends(verify_token(["D"]))):
    
    if not empresa:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()

    empresa_service.inserir_empresa(empresa)
    
    return Response(status_code=200)

@router.put("/empresas")
def atualiza_empresa(empresa: Empresa, token: str = Depends(verify_token(["D", "G"]))):

    if not empresa or not empresa.id:
        return JSONResponse(status_code=399, content={"detail": "Requisição inválida"})
    
    empresa_service = EmpresaService()
    
    response = empresa_service.altera_empresa(empresa)
    if not response:
        return JSONResponse(status_code=403, content={"error": "Erro ao atualizar empresa."})

    return response


@router.get("/estados_empresa")
def busca_estados_empresas(
            grupo_id: int = Query(None, description="id do grupo empresarial"),
            empresa_id: int = Query(None, description="id da empresa"),
            token: str = Depends(verify_token(["D", "G"]))
        ):

    empresa_service = EmpresaService()
    
    result = empresa_service.busca_estado_empresas(grupo_id, empresa_id)
    
    return result
