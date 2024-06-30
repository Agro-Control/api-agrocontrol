from connection.postgres import AsyncDatabase
from connection.mongo import Mongo
from errors import EventError
from errors import DatabaseError
from model.ordem_de_servico_model import OrdemServico
from model.operador_model import Operador


class OrdemService:

    async def busca_ordem_ativa_maquina(self, maquina: str, usuario: int):
        ordem = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                    SELECT 
                        os.*
                    FROM ordem_servico as os 
                    INNER JOIN ordem_servico_operador oso ON os.id = oso.ordem_servico_id 
                    INNER JOIN maquina m ON os.maquina_id = m.id
                    WHERE m.nome = %s
                    AND os.status IN ('A', 'E')
                    AND oso.operador_id = %s;
                """

                await cursor.execute(sql, (maquina, usuario,), prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                ordem = OrdemServico(**result)

        return ordem

    async def busca_ordem_servico(self, id_ordem: int):
        ordem = {}
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                    SELECT os.* ,STRING_AGG(oso.operador_id::text, ',') operadores 
                    FROM ordem_servico os 
                    INNER JOIN ordem_servico_operador oso ON oso.ordem_servico_id = os.id
                    WHERE os.id = %s
                    GROUP BY os.id
                """

                await cursor.execute(sql, (id_ordem,), prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                ordem = OrdemServico(**result)
        return ordem

    async def busca_ordens_servicos(self, empresa_id: int | None = None, status: str | None = None):
        ordens = []
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                params = []
                sql = """
                    SELECT 
                        os.*, 
                        m.nome AS nome_maquina, 
                        json_agg(json_build_object('id', u.id, 'nome', u.nome, 'turno', u.turno)) AS operadores
                    FROM ordem_servico os
                    INNER JOIN ordem_servico_operador oso ON oso.ordem_servico_id = os.id
                    INNER JOIN usuario u ON u.id = oso.operador_id
                    INNER JOIN maquina m ON m.id = os.maquina_id
                    WHERE 1=1
                """

                if empresa_id:
                    sql += " AND os.empresa_id = %s"
                    params.append(empresa_id)

                if status:
                    sql += " AND os.status = %s"
                    params.append(status)

                sql += " GROUP BY os.id, m.nome"

                await cursor.execute(sql, params, prepare=True)
                result = await cursor.fetchall()

                if not result:
                    return []

                for row in result:
                    operadores = [
                        Operador(**op).dict(exclude_none=True) for op in row['operadores']
                    ]
                    ordem = OrdemServico(**row)
                    ordem.operadores = operadores
                    ordens.append(ordem)

        return ordens

    async def inserir_ordem_servico(self, ordem_servico: OrdemServico):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO Ordem_Servico (data_inicio, data_previsao_fim, velocidade_minima, velocidade_maxima, rpm,
                     gestor_id, empresa_id, unidade_id, talhao_id, maquina_id)
                    VALUES (%(data_inicio)s, %(data_previsao_fim)s, %(velocidade_minima)s, %(velocidade_maxima)s, %(rpm)s,
                     %(gestor_id)s, %(empresa_id)s, %(unidade_id)s, %(talhao_id)s, %(maquina_id)s)
                    RETURNING id
                """
                try:
                    await cursor.execute(insert_query, ordem_servico.dict(), prepare=True)
                    id_ultimo_registro = (await cursor.fetchone())[0]

                    for id in ordem_servico.operadores:
                        if not id:
                            await conn.rollback()
                            return 404

                    values = [f"({id_ultimo_registro}, {id})" for id in ordem_servico.operadores]

                    insert_query = f"""
                        INSERT INTO Ordem_Servico_Operador (ordem_servico_id, operador_id)
                        VALUES {", ".join(values)};
                    """
                    await cursor.execute(insert_query, prepare=True)

                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        return 200

    async def altera_ordem_servico(self, ordem_update: OrdemServico):
        ordem = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                params = None
                if ordem_update.status == 'F':
                    update_query = """
                        UPDATE Ordem_Servico
                        SET 
                            status = %s,
                            data_fim = CASE
                                WHEN %s = 'F' THEN NOW()
                                ELSE NULL
                            END
                        WHERE id = %s;
                    """
                    params = [ordem_update.status, ordem_update.status, ordem_update.id]
                else:
                    update_query = """
                        UPDATE Ordem_Servico
                        SET 
                            status = %(status)s,
                            velocidade_minima = %(velocidade_minima)s,
                            velocidade_maxima = %(velocidade_maxima)s,
                            rpm = %(rpm)s
                        WHERE id = %(id)s;
                    """
                    params = ordem_update.dict()

                try:
                    await cursor.execute(update_query, params, prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)

                for id in ordem_update.operadores:
                    if not id:
                        await conn.rollback()
                        return {}

                sql = """
                    DELETE FROM ordem_servico_operador oso WHERE oso.ordem_servico_id = %s;
                """
                try:
                    await cursor.execute(sql, (ordem_update.id,), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)

                values = [f"({ordem_update.id}, {id})" for id in ordem_update.operadores]

                insert_query = f"""
                    INSERT INTO Ordem_Servico_Operador (ordem_servico_id, operador_id)
                    VALUES {", ".join(values)};
                """
                try:
                    await cursor.execute(insert_query, prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)

                await conn.commit()

                ordem = await self.busca_ordem_servico(ordem_update.id)

                if not ordem:
                    return {}

        return ordem

    async def altera_status_ordem_servico(self, id_ordem: int, status: str):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                update_query = """
                    UPDATE Ordem_Servico
                    SET 
                        status = %s,
                        data_fim = CASE
                            WHEN %s = 'F' THEN NOW()
                            ELSE NULL
                        END
                    WHERE id = %s;
                """

                try:
                    await cursor.execute(update_query, (status, status, id_ordem,), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()
