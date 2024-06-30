from connection.postgres import AsyncDatabase
from errors import DatabaseError
from model.grupo_model import Grupo


class GrupoService:

    async def buscar_grupo(self, grupo_id: int):
        grupo = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                    SELECT 
                        *
                    FROM Grupo e 
                    WHERE e.id = %s
                """

                await cursor.execute(sql, (grupo_id,), prepare=True)
                result = await cursor.fetchone()

                if not result:
                    return {}

                grupo = Grupo(**result)

        return grupo

    async def buscar_grupos(self):
        grupos = []

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                    SELECT 
                        *
                    FROM Grupo e
                """

                await cursor.execute(sql, prepare=True)
                result = await cursor.fetchall()

                if not result:
                    return []

                for row in result:
                    grupos.append(Grupo(**row))

        return grupos

    async def inserir_grupo(self, grupo: Grupo):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO grupo (
                        nome
                    )
                    VALUES (%(nome)s)
                """
                try:
                    await cursor.execute(insert_query, grupo.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                else:
                    await conn.commit()

    async def altera_grupo(self, grupo_update: Grupo):
        grupo = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                update_query = """
                    UPDATE Grupo
                    SET
                        nome = %(nome)s,
                        status = %(status)s
                    WHERE id = %(id)s
                """

                try:
                    await cursor.execute(update_query, grupo_update.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                else:
                    await conn.commit()

                grupo = await self.buscar_grupo(grupo_update.id)

                if not grupo:
                    return {}

        return grupo
