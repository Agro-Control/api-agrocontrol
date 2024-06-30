import datetime

from connection.mongo import Mongo
from connection.postgres import Database, AsyncDatabase
from errors import DatabaseError, EventError


class DashBoardsService:

    async def dash_operadores_operantes_por_totais(self, grupo_id: int = None, empresa_id: int = None, unidade_id:int = None):
        dash = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:

                params = []

                sql_sub = """
                    SELECT 
                        COUNT(*)
                    FROM usuario u
                    INNER JOIN unidade un ON u.unidade_id  = un.id 
                    INNER JOIN empresa e ON e.id = un.empresa_id 
                    WHERE u.tipo = 'O'
                """

                if grupo_id:
                    sql_sub += " AND u.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql_sub += " AND u.empresa_id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql_sub += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                sql = f"""
                    SELECT 
                        COUNT(*) AS operadores_ativos,
                        ({sql_sub}) operadores_totais
                    FROM usuario u
                    LEFT JOIN ordem_servico_operador oso ON oso.operador_id = u.id
                    LEFT JOIN ordem_servico os ON os.id = oso.ordem_servico_id
                    INNER JOIN unidade un ON u.unidade_id  = un.id 
                    INNER JOIN empresa e ON  e.id = un.empresa_id 
                    WHERE os.status in ('A', 'E') 
                    AND u.tipo = 'O'
                """

                if grupo_id:
                    sql += " AND u.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND u.empresa_id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                await cursor.execute(sql, params, prepare=True)
                result = await cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    async def dash_maquinas_operantes_por_totais(self,grupo_id:int = None,
                                           unidade_id: int = None,
                                           empresa_id: int = None):
        dash = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:

                params = []

                sql_sub = """
                            SELECT 
                                COUNT(*)
                            FROM maquina m
                            INNER JOIN unidade u ON m.unidade_id  = u.id
                            INNER JOIN empresa e ON u.empresa_id = e.id
                            WHERE m.status = 'A'
                        """

                if grupo_id:
                    sql_sub += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql_sub += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql_sub += " AND m.unidade_id = %s"
                    params.append(unidade_id)

                sql = f"""
                        SELECT 
                            COUNT(*) AS maquina_operando,
                            ({sql_sub}) maquinas_total
                        FROM maquina m
                        LEFT JOIN ordem_servico os ON os.maquina_id = m.id
                        INNER JOIN unidade u ON m.unidade_id  = u.id
                        INNER JOIN empresa e ON u.empresa_id = e.id
                        WHERE m.status = 'A'
                        AND os.status in ('A', 'E')
                """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND m.unidade_id = %s"
                    params.append(unidade_id)

                await cursor.execute(sql, params, prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    async def dash_ordem_ativas(self, grupo_id:int = None,
                               unidade_id: int = None,
                               empresa_id: int = None):

        dash = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:

                params = []

                sql = """
                        SELECT 
                            count(*) ordens_ativas
                        FROM ordem_servico os
                        INNER JOIN unidade u ON os.unidade_id = u.id 
                        INNER JOIN empresa e ON e.id  = os.empresa_id 
                        WHERE os.status in ('A', 'E')
                    """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND U.ID = %s"
                    params.append(unidade_id)

                await cursor.execute(sql, params, prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    async def dash_ordem_status(self,
                          grupo_id: int = None,
                          unidade_id: int = None,
                          empresa_id: int = None
                          ):

        dash = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                params_total = []
                params = []

                sql_total = """
                    select 
                        COUNT(os.*) total 
                    from ordem_servico os
                    inner join empresa e ON e.id  = os.empresa_id 
                    join unidade u ON os.unidade_id = u.id 
                    WHERE 1=1
                """

                if grupo_id:
                    sql_total += " AND e.grupo_id = %s"
                    params_total.append(grupo_id)

                if empresa_id:
                    sql_total += " AND e.id = %s"
                    params_total.append(empresa_id)

                if unidade_id:
                    sql_total += " AND u.id = %s"
                    params_total.append(unidade_id)

                await cursor.execute(sql_total, params_total, prepare=True)

                result = await cursor.fetchone()

                if not result:
                    dash['total_de_ordens'] = 0
                    return dash

                dash['total_de_ordens'] = result['total']

                sql = """
                    SELECT 
                        CASE
                            WHEN os.status = 'A' THEN 'Ativa'
                            WHEN os.status = 'E' THEN 'Em andamento'
                            WHEN os.status = 'F' THEN 'Finalizado'
                            WHEN os.status = 'C' THEN 'Cancelado'
                            WHEN os.status = 'I' THEN 'Inativo'
                        ELSE
                            'Fez merda'
                        END as "STATUS",
                        COUNT(os.id) total
                    FROM ordem_servico os
                    INNER JOIN unidade u ON os.unidade_id = u.id 
                    INNER JOIN empresa e ON e.id  = os.empresa_id 
                    WHERE 1 = 1
                """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.id = %s"
                    params.append(unidade_id)

                sql += " GROUP BY os.status"

                await cursor.execute(sql, params, prepare=True)

                result = await cursor.fetchall()

                if not result:
                    return dash

                for row in result:
                    dash[row['STATUS']] = row['total']

        return dash

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

                qtd_eventos = {"eventos": [], "duracao_total": 0, "total": 0}

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    qtd_eventos['eventos'].append({
                        "evento": result['_id'], "quantidade": result['count'], "duracao": result['duracao']
                    })
                    qtd_eventos['duracao_total'] = qtd_eventos.get('duracao_total', 0) + result['duracao']
                    qtd_eventos['total'] = qtd_eventos.get('total', 0) + result['count']

            except Exception as ex:
                raise EventError(ex)

        return qtd_eventos

    async def dash_manutencao_maquina(self, grupo_id: int, empresa_id: int):
        manutencao_maquinas = {}

        async with Mongo() as client:
            try:

                now = datetime.datetime.now().date()
                now = datetime.datetime.combine(now, datetime.time.min)

                criterio = {"grupo_id": grupo_id}

                if empresa_id:
                    criterio["empresa_id"] = empresa_id

                pipeline = [
                    {
                        "$match": {
                            **criterio,
                            "data_inicio": {
                                "$gte": datetime.datetime(year=now.year, month=now.month, day=1),
                                "$lt": datetime.datetime(year=2024, month=(now.month + 1 if now.month <= 12 else 1),
                                                         day=now.day)
                            },
                            "nome": "manutencao"
                        }
                    },
                    {
                        "$group": {
                            "_id": '$nome',
                            'count': {'$sum': 1},  # Contar o número de eventos de cada tipo
                            "duracao_total": {"$sum": "$duracao"}
                        }
                    }
                ]

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    manutencao_maquinas.update({
                        "evento": result['_id'],
                        "qtd_eventos_mes": result['count'],
                        "tempo_total_manutencao": result['duracao_total']
                    })

                pipeline = [
                    {
                        "$match": {
                            **criterio,
                            "data_inicio": {
                                "$gte": datetime.datetime(year=now.year, month=now.month, day=now.day)},
                            "data_fim": {
                                "$lte": datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23,
                                                          minute=59, second=59)},
                            "nome": "manutencao"
                        }
                    },
                    {
                        "$count": "eventos_manutencao_dia_atual"
                    }

                ]

                async for result in client.agro_control.eventos.aggregate(pipeline):
                    manutencao_maquinas.update(result)

                pipeline = [
                    {
                        "$match": {
                            **criterio,
                            "data_inicio": {
                                "$gte": datetime.datetime(year=now.year, month=now.month, day=now.day)},
                            "data_fim": {
                                "$lte": datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23,
                                                          minute=59, second=59)},
                            "nome": "manutencao"
                        }
                    },
                    {
                        "$group": {
                            "_id": "$maquina_id",
                            "count": {'$sum': 1}
                        }
                    },
                    {
                        "$count": "qtd_maquinas_manutencao_dia"
                    }
                ]
                async for result in client.agro_control.eventos.aggregate(pipeline):
                    manutencao_maquinas.update(result)

            except Exception as ex:
                raise EventError(ex)

        return manutencao_maquinas

    async def dash_tempo_operacao_producao(self, grupo_id: int, empresa_id: int):
        operacional = {}
        async with Mongo() as client:
            try:

                now = datetime.datetime.now().date()
                now = datetime.datetime.combine(now, datetime.time.min)

                criterio = {"grupo_id": grupo_id}

                if empresa_id:
                    criterio["empresa_id"] = empresa_id

                pipeline = [
                    {
                        "$match": {
                            **criterio,
                            "data_inicio": {"$gte": datetime.datetime(year=now.year, month=now.month, day=now.day)},
                            "data_fim": {"$lte": datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23,
                                                                   minute=59, second=59)},
                        }
                    },
                    {
                        "$group": {
                            "_id": '$nome',
                            'count': {'$sum': 1},  # Contar o número de eventos de cada tipo
                            "duracao_total": {'$sum': {'$ifNull': ['$duracao', 0]}}
                        }
                    }
                ]

                operacional = {
                    "operacionais": 0,
                    "improdutivos": 0,
                    "manutencao": 0,
                    "tempo_jornada_total": 0
                }

                async for result in client.agro_control.eventos.aggregate(pipeline):

                    if result['_id'] in ["operacao", "transbordo", "deslocamento"]:
                        operacional['operacionais'] = operacional.get('operacionais', 0) + result['duracao_total']
                    elif result['_id'] == 'manutencao':
                        operacional['manutencao'] = operacional.get('manutencao', 0) + result['duracao_total']
                    else:
                        operacional['improdutivos'] = operacional.get('improdutivos', 0) + result['duracao_total']

                    operacional['tempo_jornada_total'] = operacional.get('tempo_jornada_total', 0) + result[
                        'duracao_total']
            except Exception as ex:
                raise EventError(ex)

        return operacional
