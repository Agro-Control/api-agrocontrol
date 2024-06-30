from fastapi import APIRouter, Depends

from model.gestor_model import Gestor
from model.operador_model import Operador
from service.jwt_service import verify_token
from service.usuario_service import UsuarioService
from model.usuario_model import Usuario
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict, List

router = APIRouter()


@router.get("/operador/{id}", response_model=Operador)
async def busca_operador(id: int, token: str = Depends(verify_token(["G"]))) -> Operador:
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    operador_service = UsuarioService()

    response = await operador_service.buscar_operador(id)

    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Operador não encontrada"})

    return response


@router.get("/operadores")
async def busca_operadores(empresa_id: int = Query(None, description="Empresa do Operador"),
                    unidade_id: int = Query(None, description="Unidade do Operador"),
                     turno: str = Query(None, description="Turno do Operador"),
                     status: str = Query(None, description="Status do Operador"),
                     codigo: str = Query(None, description="Nome/Codigo do Operador"),
                     disponibilidade_ordem: bool = Query(None, description="Operadores diponiveis para nova ordem"),
                     token: str = Depends(verify_token(["G"]))):
    operador_service = UsuarioService()

    response = await operador_service.buscar_operadores(empresa_id=empresa_id,unidade_id=unidade_id, turno=turno, status=status, codigo=codigo,
                                                  disp_ordem=disponibilidade_ordem)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Operadores não encontrados"})

    return {"operador": response}


@router.post("/operadores")
async def inserir_operador(operador: Usuario, token: str = Depends(verify_token(["G"]))):
    if not operador:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    if not operador.email or not operador.cpf:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    operador_service = UsuarioService()

    operador.cpf = operador.cpf.replace('.', '').replace('-', '')
    if not UsuarioService.valida_cpf(operador.cpf):
        return JSONResponse(status_code=400, content={"error": "CPF Inválido"})

    status, response = await operador_service.inserir_operador(operador)

    if status == 409:
        return JSONResponse(status_code=status, content={"error": response})

    return Response(status_code=201)


@router.put("/operadores")
async def atualiza_operador(operador: Operador, token: str = Depends(verify_token(["G"]))):
    if not operador or not operador.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    if not operador.email or not operador.cpf:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    operador_service = UsuarioService()

    operador.cpf = operador.cpf.replace('.', '').replace('-', '')
    if not UsuarioService.valida_cpf(operador.cpf):
        return JSONResponse(status_code=400, content={"error": "CPF Inválido"})

    status, response = await operador_service.altera_operador(operador)

    if status in [404, 409]:
        return JSONResponse(status_code=status, content={"error": response})

    return status, response


@router.get("/gestor/{id}", response_model=Usuario)
async def busca_gestor(id: int, token: str = Depends(verify_token(["D"]))) -> Usuario:
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    response = await gestor_service.buscar_gestor(id)

    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Gestor não encontrada"})

    return response


@router.get("/gestores")
async def busca_gestores(grupo_id: int = Query(None, description="Numero do grupo empresarial do Gestor"),
                    empresa_id: int = Query(None, description="Empresa do Gestor"),
                    unidade_id: int = Query(None, description="Unidade do Gestor"),
                   status: str = Query(None, description="Status do Gestor"),
                   codigo: str = Query(None, description="Nome/Codigo do Gestor"),
                   token: str = Depends(verify_token(["D"]))):

    gestor_service = UsuarioService()

    response = await gestor_service.buscar_gestores(grupo_id=grupo_id, empresa_id=empresa_id, unidade_id=unidade_id,
                                              status=status, codigo=codigo)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Gestores não encontrados"})

    return {"gestor": response}


@router.post("/gestores")
async def inserir_gestor(gestor: Usuario, token: str = Depends(verify_token(["D"]))):
    if not gestor:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    if not gestor.email or not gestor.cpf:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    gestor.cpf = gestor.cpf.replace('.', '').replace('-', '')

    if not UsuarioService.valida_cpf(gestor.cpf):
        return JSONResponse(status_code=400, content={"error": "CPF Inválido"})

    status, response = await gestor_service.inserir_gestor(gestor)

    if status == 409:
        return JSONResponse(status_code=409, content={"error": response})

    return Response(status_code=status)



@router.put("/gestores")
async def atualiza_gestor(gestor: Gestor, token: str = Depends(verify_token(["D"]))):
    if not gestor or not gestor.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    if not gestor.email or not gestor.cpf:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    gestor.cpf = gestor.cpf.replace('.', '').replace('-', '')
    if not UsuarioService.valida_cpf(gestor.cpf):
        return JSONResponse(status_code=400, content={"error": "CPF Inválido"})

    status, response = await gestor_service.altera_gestor(gestor)

    if status in [404, 409]:
        return JSONResponse(status_code=status, content={"error": response})

    return status, response
