from fastapi import APIRouter, Depends
from service.dashboard_service import DashBoardsService
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import Response, Query
from service.jwt_service import verify_token

router = APIRouter()


@router.get("/dashboards/operadores_operando")
def operadores_alocados(grupo_id: int = Query(None, description="Pato"),
                        empresa_id: int = Query(None, description="Deus no comando"),
                        unidade_id: int = Query(None, description="Unidade da Empresa")):

    dash_service = DashBoardsService()

    response = dash_service.dash_operadores_operantes_por_totais(grupo_id=grupo_id, empresa_id=empresa_id, unidade_id=unidade_id)

    if not response:

        return JSONResponse(status_code=403, content={"error": "Dash não construido"})

    return response


@router.get("/dashboards/maquinas_operando")
def maquinas_alocados(
            grupo_id: int = Query(None, description="Deus no comando"),
            empresa_id: int = Query(None, description="Deus no comando"),
            unidade_id: int = Query(None, description="Unidade da Empresa")):

    dash_service = DashBoardsService()

    response = dash_service.dash_maquinas_operantes_por_totais(grupo_id=grupo_id, empresa_id=empresa_id,
                                                               unidade_id=unidade_id)

    if not response:

        return JSONResponse(status_code=403, content={"error": "Dash não construido"})

    return response


@router.get("/dashboards/ordem_ativas")
def ordem_ativas(
            grupo_id: int = Query(None, description="Deus no comando"),
            empresa_id: int = Query(None, description="Deus no comando"),
            unidade_id: int = Query(None, description="Unidade da Empresa")):

    dash_service = DashBoardsService()

    response = dash_service.dash_ordem_ativas(grupo_id=grupo_id, empresa_id=empresa_id, unidade_id=unidade_id)

    if not response:

        return JSONResponse(status_code=403, content={"error": "Dash não construido"})

    return response


@router.get("/dashboards/ordem_status")
def ordem_status(
            grupo_id: int = Query(None, description="Deus no comando"),
            empresa_id: int = Query(None, description="Deus no comando"),
            unidade_id: int = Query(None, description="Unidade da Empresa")):

    dash_service = DashBoardsService()

    response = dash_service.dash_ordem_status(grupo_id=grupo_id, empresa_id=empresa_id, unidade_id=unidade_id)

    if not response:
        return JSONResponse(status_code=403, content={"error": "Dash não construido"})

    return response