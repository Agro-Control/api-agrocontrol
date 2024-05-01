from fastapi import APIRouter
from service.usuario_service import UsuarioService
from model.usuario_model import Usuario
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict

router = APIRouter()

@router.get("/operador/{id}", response_model=Usuario)
def busca_operador(id: int)-> Usuario:
    
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    operador_service = UsuarioService()

    response = operador_service.buscar_operador(id)
    
    if not response or isinstance(response, Dict):
        return JSONResponse(status_code= 404, content={"error": "Operador não encontrada"})

    return response


@router.get("/operadores")
def busca_operadores(id_empresa: int  = Query(None, description="Empresa do Operador"),
                    turno: str  = Query(None, description="Turno do Operador"),
                    status: str = Query(None, description="Status do Operador"),
                    codigo: str = Query(None, description= "Nome/Codigo do Operador"),
                    disponibilidade_ordem: bool = Query(None, description="Operadores diponiveis para nova ordem")):
    
    
    operador_service = UsuarioService()
    print(f"Empresa ID: {id_empresa}")
    print(f"Turno: {turno}")
    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    print(f"Disponibilidade_ordem: {disponibilidade_ordem}")
    
    response = operador_service.buscar_operadores(empresa_id=id_empresa, turno=turno, status=status,codigo=codigo, disp_ordem=disponibilidade_ordem)

    if not response:
        return JSONResponse(status_code= 404, content={"error": "Operadores não encontrados"})

    return {"operador": response}
 
@router.post("/operadores")
def inserir_operador(operador: Usuario):
    
    if not operador:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    operador_service = UsuarioService()
    
    operador_service.inserir_operador(operador)
    
    return Response(status_code=201)

@router.put("/operadores")
def atualiza_operador(operador: Usuario):

    if not operador or not operador.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    operador_service = UsuarioService()
    
    response = operador_service.altera_operador(operador)
    if not response:
        return JSONResponse(status_code= 404, content={"error": "Erro ao atualizar operador."})

    return response


