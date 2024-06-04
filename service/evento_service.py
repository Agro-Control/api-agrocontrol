from connection.mongo import Mongo
from model.evento_model import Evento
from errors import EventError
from bson import ObjectId
from datetime import timezone


class EventoService:
    def __init__(self):
        pass

    async def busca_eventos_ordem(self, id_ordem: int, nome: str = None):

        eventos = []
        async with Mongo() as client:
            query = {"ordem_servico_id": int(id_ordem)}

            if nome:
                query['nome'] = str(nome)

            async for documento in client.agro_control.eventos.find(query):
                evento = Evento()
                evento.id = str(documento['_id'])
                evento.nome = documento.get('nome', None)
                evento.data_inicio = documento.get('data_inicio', None)
                evento.data_fim = documento.get('data_fim', None)
                evento.duracao = documento.get('duracao', None)
                evento.ordem_servico_id = documento.get('ordem_servico_id', None)
                evento.maquina_id = documento.get('maquina_id', None)
                evento.operador_id = documento.get('operador_id', None)
                evento.empresa_id = documento.get('empresa_id', None)
                evento.grupo_id = documento.get('grupo_id', None)
                eventos.append(evento)

        return eventos

    async def insere_evento(self, evento: Evento):
        async with Mongo() as client:
            try:
                evento_insert = evento.dict()
                evento_insert.pop('id', None)
                result = await client.agro_control.eventos.insert_one(evento_insert)
                if not result:
                    return

                if not result:
                    return

                return result.inserted_id
            except Exception as ex:
                raise EventError(ex)

        return

    async def finaliza_evento(self, evento: Evento):
        async with Mongo() as client:
            try:
                query = {"_id": ObjectId(evento.id)}
                update = {"$set": {"data_fim": evento.data_fim, "duracao": evento.duracao}}

                result = await client.agro_control.eventos.find_one_and_update(query, update, return_document=True)

                if not result:
                    return

                evento = Evento(**result)
                evento._id = str(result['_id'])

                return evento
            except Exception as ex:
                raise EventError(ex)
        return

    async def dash_eventos_ordem(self, ordem_id: int):

        qtd_eventos = {}

        async with Mongo() as client:
            try:

                pipeline = [
                    {
                        '$match': {
                            'ordem_servico_id': ordem_id
                        }
                    },
                    {
                        '$group': {
                            '_id': '$nome',
                            'count': {'$sum': 1},
                            'duracao': {'$sum': {'$ifNull': ['$duracao', 0]}}
                        }
                    }

                ]

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    qtd_eventos[result['_id']] = result['count']
                    qtd_eventos['duracao_total'] = qtd_eventos.get('duracao_total', 0) + result['duracao']
                    qtd_eventos['total'] = qtd_eventos.get('total', 0) + result['count']

            except Exception as ex:
                raise EventError(ex)

        return qtd_eventos
