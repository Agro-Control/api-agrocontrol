from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from service.ordem_service import OrdemService
from errors import ApiExceptionHandler

app = FastAPI()

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return await ApiExceptionHandler.handler(exc)


@app.get("/")
async def root():
    return {"message": "Hello word"}


@app.get("/ordem/{id_maquina}")
def maquina(id_maquina: int):
    
    if not id_maquina:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})

    ordem_service = OrdemService()
    response = ordem_service.busca_ordem_maquina(id_maquina)

    if not response:
        return JSONResponse(status_code=404, content={"error": "Ordem de servico não encontrada"})
    
    return JSONResponse(status_code=200, content=response)


@app.get("/eventos/{id_ordem}")
async def eventos_por_ordem(id_ordem: int):

    if not id_ordem:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})
    
    ordem_service = OrdemService()

    eventos = await ordem_service.busca_eventos_ordem(id_ordem)
        
    return JSONResponse(status_code=200, content=eventos)


@app.post("/eventos")
async def eventos(request: Request):
    data = await request.json()
    
    if not data:
        return JSONResponse(status_code=400, content={"error": "Requisição inválida"})
    
    ordem_service = OrdemService()
    await ordem_service.insere_evento(data)
    return Response(status_code=204)


