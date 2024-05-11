from connection.mongo import Mongo
from model.evento_model import Evento
from errors import EventError
from bson import ObjectId

class EventoService:
    def __init__(self):
        pass

    async def busca_eventos_ordem(self, id_ordem: int):

        eventos = []
        async with Mongo() as client:
            query = {"ordem_servico": int(id_ordem)}

            async for doc in client.agro_control.eventos.find(query):

                # esperar o modelo
                # del, é gambiara só pra ter o que mostrar
                # del doc["_id"]
                eventos.append(Evento(**doc))

        return eventos


    async def insere_evento(self, evento: Evento):
        async with Mongo() as client:
            try:
                result = await client.agro_control.eventos.insert_one(evento)
                if not result:
                    return

                return Evento(**result)

            except Exception as ex:
                raise EventError(ex)

        return


    async def finaliza_evento(self, evento: Evento):
        async with Mongo() as client:
            try:
                query = {"_id": ObjectId(evento._id)}
                update = {"$set": {"data_fim": evento.data_fim}}

                result = await client.agro_control.eventos.update_one(query, update)
                if not result:
                    return

                return Evento(**result)
            except Exception as ex:
                raise EventError(ex)
        return

