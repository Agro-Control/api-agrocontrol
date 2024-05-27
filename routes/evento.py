from fastapi import APIRouter, Depends

from service.jwt_service import verify_token
from service.ordem_service import OrdemService
from service.evento_service import EventoService
from fastapi.responses import JSONResponse
from fastapi import Response
from model.evento_model import Evento

router = APIRouter()

@router.get("/eventos/{id_ordem}")
async def eventos_por_ordem(id_ordem: int):

    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    ordem = await ordem_service.busca_ordem_servico_async(id_ordem)

    if not ordem:
        return JSONResponse(status_code=404, content={"detail": "Ordem inválida"})

    evento_service = EventoService()

    eventos = await evento_service.busca_eventos_ordem(id_ordem)

    if not eventos:
        return JSONResponse(status_code=404, content={"error": "Eventos não encontrados"})

    return {"eventos": eventos}


@router.post("/eventos")
async def insere_evento(evento: Evento) -> JSONResponse:
    # return "OK"
    if not evento:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    evento_service = EventoService()
    evento_inserido_id = await evento_service.insere_evento(evento)

    if evento.nome == "fim de ordem":
        ordem_service = OrdemService()
        ordem_service.altera_status_ordem_servico(evento.ordem_servico_id, 'F')

    elif evento.nome == "inicio ordem de servico":
        ordem_service = OrdemService()
        ordem_service.altera_status_ordem_servico(evento.ordem_servico_id, 'E')

    return JSONResponse(status_code=201, content={"id": str(evento_inserido_id)})


@router.put("/eventos")
async def finaliza_evento(evento: Evento):

    if not evento:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    evento_service = EventoService()
    evento = await evento_service.finaliza_evento(evento)

    return evento
