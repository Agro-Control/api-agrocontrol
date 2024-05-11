from fastapi import APIRouter
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
    
    evento_service = EventoService()

    eventos = await evento_service.busca_eventos_ordem(id_ordem)

    return JSONResponse(status_code=200, content={"eventos": eventos})


@router.post("/eventos")
async def insere_eventos(evento: Evento) -> Response:

    if not evento:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    evento_service = EventoService()
    evento = await evento_service.insere_evento(evento)

    if evento.nome == "fim de ordem":
        ordem_service = OrdemService()
        ordem_service.finaliza_ordem_servico(evento.ordem_servico_id)

    print(evento, flush=True)
    return Response(status_code=204, content={"id": evento._id})


@router.put("/eventos")
async def atualiza_eventos(evento: Evento) -> Evento:
    data = await evento

    if not data:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    evento_service = EventoService()
    evento = await evento_service.finaliza_evento(evento)

    return evento
