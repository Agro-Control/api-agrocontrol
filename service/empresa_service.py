from connection.postgres import AsyncDatabase
from errors import DatabaseError
from model.empresa_model import Empresa


class EmpresaService:

    async def buscar_empresa(self, empresa_id: int):
        empresa = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                    SELECT 
                        *
                    FROM Empresa e 
                    WHERE e.id = %s
                """

                await cursor.execute(sql, (empresa_id,), prepare=True)
                result = await cursor.fetchone()

                if not result:
                    return {}

                empresa = Empresa(**result)

        return empresa

    async def buscar_empresas(self, codigo: str | None = None, grupo_id: int | None = None, status: str | None = None,
                              disp: bool | None = None, estado: str | None = None):
        empresas = []

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                params = []

                sql = """
                    SELECT 
                        *
                    FROM Empresa e
                    WHERE 1=1
                """

                if codigo:
                    sql += " AND LOWER(e.nome) LIKE LOWER(%s)"
                    params.append(f"%{codigo.lower()}%")

                if status:
                    sql += " AND e.status = %s"
                    params.append(status)

                if estado:
                    sql += " AND e.estado = %s"
                    params.append(estado)

                if grupo_id:
                    sql += " AND grupo_id = %s"
                    params.append(grupo_id)

                    if disp:
                        sql += (
                            " AND e.id NOT IN (SELECT DISTINCT u.empresa_id FROM usuario u WHERE u.status = 'A' AND "
                            "u.tipo = 'G')")

                await cursor.execute(sql, params, prepare=True)
                result = await cursor.fetchall()

                if not result:
                    return []

                for row in result:
                    empresas.append(Empresa(**row))

        return empresas

    async def inserir_empresa(self, empresa: Empresa):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO empresa (
                        nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro,
                        numero, complemento, grupo_id
                    )
                    VALUES (%(nome)s, %(cnpj)s, %(telefone)s, %(cep)s, %(estado)s, %(cidade)s, %(bairro)s, %(logradouro)s,
                    %(numero)s, %(complemento)s, %(grupo_id)s)
                """
                try:
                    await cursor.execute(insert_query, empresa.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                else:
                    await conn.commit()

    async def altera_empresa(self, empresa_update: Empresa):
        empresa = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                update_query = """
                    UPDATE Empresa
                    SET
                        nome = %(nome)s,
                        cnpj = %(cnpj)s,
                        telefone = %(telefone)s,
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
                    await cursor.execute(update_query, empresa_update.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                else:
                    await conn.commit()

                empresa = await self.buscar_empresa(empresa_update.id)

                if not empresa:
                    return {}

        return empresa

    async def busca_estado_empresas(self, grupo_id: int | None = None, empresa_id: int | None = None):
        estados = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        estado
                    FROM empresa
                    WHERE 1=1
                """

                if grupo_id:
                    sql += " AND grupo_id = %s"

                if empresa_id:
                    sql += " AND id = %s"

                sql += " GROUP BY estado"

                try:
                    await cursor.execute(sql, (grupo_id,), prepare=True)
                except Exception as e:
                    raise DatabaseError(e)

                result = await cursor.fetchall()

                if not result:
                    return {}

                estados = {
                    "estados": result
                }

        return estados
