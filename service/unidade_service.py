from connection.postgres import AsyncDatabase
from errors import DatabaseError
from model.unidade_model import Unidade


class UnidadeService:

    async def buscar_unidade(self, unidade_id: int):
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                        SELECT 
                            *
                        FROM Unidade u 
                        WHERE u.id = %s ;
                    """

                await cursor.execute(sql, (unidade_id,), prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                unidade = Unidade(**result)

        return unidade

    async def buscar_unidades(self, empresa_id: int | None = None, grupo_id: int | None = None,
                              codigo: str | None = None, status: str | None = None):
        unidades = []

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:

                params = []

                sql = """SELECT 
                            *
                        FROM Unidade u
                        WHERE 1=1
                    """

                if empresa_id:
                    sql += " AND u.empresa_id = %s"
                    params.append(empresa_id)

                if grupo_id:
                    sql += " AND u.empresa_id in (select e.id from empresa e where e.grupo_id = %s)"
                    params.append(grupo_id)

                if codigo:
                    sql += " AND u.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)

                await cursor.execute(sql, params, prepare=True)

                result = await cursor.fetchall()

                if not result:
                    return []

                for row in result:
                    unidades.append(Unidade(**row))

        return unidades

    async def inserir_unidade(self, unidade: Unidade):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                # Query de insert
                insert_query = """
                    INSERT INTO unidade (
                        nome, cep, estado, cidade, bairro, logradouro,
                        numero, complemento, gestor_id, empresa_id
                    )
                    VALUES (%(nome)s, %(cep)s, %(estado)s, %(cidade)s, %(bairro)s, %(logradouro)s,
                    %(numero)s, %(complemento)s, %(gestor_id)s, %(empresa_id)s)
                """
                try:
                    await cursor.execute(insert_query, unidade.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        return

    async def altera_unidade(self, unidade_update: Unidade):
        unidade = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                # Query de update
                update_query = """
                    UPDATE Unidade
                    SET
                        nome = %(nome)s,
                        cep = %(cep)s,
                        estado = %(estado)s,
                        cidade = %(cidade)s,
                        bairro = %(bairro)s,
                        logradouro = %(logradouro)s,
                        numero = %(numero)s,
                        complemento = %(complemento)s,
                        status = %(status)s
                    WHERE id = %(id)s
                """

                try:
                    await cursor.execute(update_query, unidade_update.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

                unidade = await self.buscar_unidade(unidade_update.id)

                if not unidade:
                    return {}

        return unidade
