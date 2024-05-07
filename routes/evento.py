from fastapi import APIRouter, Request
from service.ordem_service import OrdemService
from fastapi.responses import JSONResponse
from fastapi import Response


router = APIRouter()



@router.get("/eventos/{id_ordem}")
async def eventos_por_ordem(id_ordem: int):

    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    eventos = await ordem_service.busca_eventos_ordem(id_ordem)
        
    return JSONResponse(status_code=200, content=eventos)


@router.post("/eventos")
async def eventos(request: Request):
    data = await request.json()
    
    if not data:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})
    
    # ordem_service = OrdemService()
    # await ordem_service.insere_evento(data)
    print(data, flush=True)
    return Response(status_code=204)


