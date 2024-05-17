from fastapi import APIRouter
from service.usuario_service import UsuarioService
from model.usuario_model import Usuario
from fastapi.responses import JSONResponse
from fastapi import Response, Query
from typing import Dict

router = APIRouter()


@router.get("/operador/{id}", response_model=Usuario)
def busca_operador(id: int) -> Usuario:
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    operador_service = UsuarioService()

    response = operador_service.buscar_operador(id)

    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Operador não encontrada"})

    return response


@router.get("/operadores")
def busca_operadores(unidade_id: int = Query(None, description="Unidade do Operador"),
                     turno: str = Query(None, description="Turno do Operador"),
                     status: str = Query(None, description="Status do Operador"),
                     codigo: str = Query(None, description="Nome/Codigo do Operador"),
                     disponibilidade_ordem: bool = Query(None, description="Operadores diponiveis para nova ordem")):
    operador_service = UsuarioService()
    print(f"Unidade ID: {unidade_id}")
    print(f"Turno: {turno}")
    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    print(f"Disponibilidade_ordem: {disponibilidade_ordem}")

    response = operador_service.buscar_operadores(unidade_id=unidade_id, turno=turno, status=status, codigo=codigo,
                                                  disp_ordem=disponibilidade_ordem)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Operadores não encontrados"})

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
        return JSONResponse(status_code=404, content={"error": "Erro ao atualizar operador."})

    return response


@router.get("/gestor/{id}", response_model=Usuario)
def busca_gestor(id: int) -> Usuario:
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    response = gestor_service.buscar_gestor(id)

    if not response or isinstance(response, Dict):
        return JSONResponse(status_code=404, content={"error": "Gestor não encontrada"})

    return response


@router.get("/gestores")
def busca_gestores(grupo_id: int = Query(None, description="Numero do grupo empresarial do Gestor"),
                   status: str = Query(None, description="Status do Gestor"),
                   codigo: str = Query(None, description="Nome/Codigo do Gestor")):
    gestor_service = UsuarioService()

    print(f"Grupo_id: {grupo_id}")
    print(f"Codigo: {codigo}")
    print(f"Status: {status}")
    response = gestor_service.buscar_gestores(grupo_id=grupo_id, status=status, codigo=codigo)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Gestores não encontrados"})

    return {"gestor": response}


@router.post("/gestores")
def inserir_gestor(gestor: Usuario):
    if not gestor:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    gestor_service.inserir_gestor(gestor)

    return Response(status_code=201)


@router.put("/gestores")
def atualiza_gestor(gestor: Usuario):
    if not gestor or not gestor.id:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    gestor_service = UsuarioService()

    response = gestor_service.altera_gestor(gestor)
    if not response:
        return JSONResponse(status_code=404, content={"error": "Erro ao atualizar gestor."})

    return response


@router.get("/usuarios")
def busca_usuarios_grupo(grupo_id: int = Query(None, description="Numero do grupo empresarial do Usuario"),
                        empresa_id: int = Query(None, description="Empresa do Usuario"),
                        unidade_id: int = Query(None, description="Unidade do Usuario"),
                        nome: str = Query(None, description="Nome do Usuario"),
                        status: str = Query(None, description="Status do Usuario"),
                        tipo: str = Query(None, description="Tipo do Usuario")):

    usuario_service = UsuarioService()

    response = usuario_service.busca_usuarios(grupo_id, empresa_id, unidade_id, nome, status, tipo)
    if not response:

        return JSONResponse(status_code=404, content={"error": "Erro ao atualizar gestor."})

    return {"usuarios": response}
