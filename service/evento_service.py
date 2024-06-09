import datetime

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
                evento.ocioso = documento.get('ocioso', None)
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


    async def info_maquina(self, maquina_id):
        info_maquina = {
            "ultimos_eventos": [],
            "qtd_manutencao_mes": 0,
            "tempo_total_manutencao_mes": 0,
            "qtd_manutencao_dia": 0,
            "tempo_total_manutencao_dia": 0
        }

        async with Mongo() as client:
            try:
                now = datetime.datetime.now().date()
                now = datetime.datetime.combine(now, datetime.time.min)

                eventos_ignorar = ["aguardando_transbordo", "clima", "troca_turno", "fim_ordem"]

                pipeline = [
                    {'$match': {'maquina_id': maquina_id, 'nome': {'$nin': eventos_ignorar}}},
                    {'$sort': {'data_inicio': -1}},
                    {'$limit': 5}
                ]

                async for documento in client.agro_control.eventos.aggregate(pipeline):
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
                    evento.ocioso = documento.get('ocioso', None)
                    info_maquina['ultimos_eventos'].append(evento)

                pipeline = [
                    {
                        "$match": {
                            "maquina_id": maquina_id,
                            "data_inicio": {
                                "$gte": datetime.datetime(year=now.year, month=now.month, day=1),
                                "$lt": datetime.datetime(year=2024,
                                                         month=(now.month + 1 if now.month <= 12 else 1),
                                                         day=now.day)
                            },
                            "nome": "manutencao"
                        }
                    },
                    {
                        "$group": {
                            "_id": '$nome',
                            'count': {'$sum': 1},
                            "duracao_total": {"$sum": "$duracao"}
                        }
                    }
                ]

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    info_maquina.update({
                        "qtd_manutencao_mes": result['count'],
                        "tempo_total_manutencao_mes": result['duracao_total']
                    })

                pipeline = [
                    {
                        "$match": {
                            "maquina_id": maquina_id,
                            "data_inicio": {
                                "$gte": datetime.datetime(year=now.year, month=now.month, day=now.day)},
                            "data_fim": {
                                "$lte": datetime.datetime(year=now.year, month=now.month, day=now.day,
                                                          hour=23,
                                                          minute=59, second=59)},
                            "nome": "manutencao"
                        }
                    },
                    {
                        "$group": {
                            "_id": '$nome',
                            'count': {'$sum': 1},
                            "duracao_total": {"$sum": "$duracao"}
                        }
                    }
                ]

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    info_maquina["qtd_manutencao_dia"] = result['count']
                    info_maquina["tempo_total_manutencao_dia"] = result['duracao_total']

            except Exception as ex:
                raise EventError(ex)

        return info_maquina
