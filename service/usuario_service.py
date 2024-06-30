from datetime import datetime
import traceback
from typing import Optional, List

import bcrypt
from connection.postgres import Database, AsyncDatabase
from errors import DatabaseError
from model.gestor_model import Gestor
from model.operador_model import Operador
from model.usuario_model import Usuario
from service.jwt_service import criptografar_senha, enviar_email, gerar_senha_aleatoria 

class UsuarioService:
    
    async def buscar_gestor(self, id: int):
        gestor = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Usuario u 
                        where u.id = %s and tipo = 'G';
                    """
                
                await cursor.execute(sql, (id, ), prepare=True)
                
                result = await cursor.fetchone()
            
                if not result:
                    return {}

                gestor = Gestor(**result)
 
        return gestor

    async def buscar_gestores(self, grupo_id: int | None = None, empresa_id: int = None, unidade_id: int = None,
                        codigo: str | None = None, status: str | None = None):
        gestores = []

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            u.*,
                            e.nome empresa,
                            un.nome unidade
                        FROM Usuario u
                        LEFT JOIN empresa e on e.id = u.empresa_id  
                        LEFT JOIN unidade un on un.id = u.unidade_id
                        WHERE 1=1 and tipo = 'G'
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

                if codigo:
                    sql += " AND LOWER(u.nome) LIKE LOWER(%s)"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)

                await cursor.execute(sql, params, prepare=True)
                
                result = await cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    gestores.append(Gestor(**row))

        return gestores

    async def inserir_gestor(self, gestor: Usuario):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                if not await self.verifica_email_existente(cursor, gestor.id, gestor.email):
                    return 409, "Email já existe"
                if not await self.verifica_cpf_existente(cursor, gestor.id, gestor.cpf):
                    return 409, "CPF já existente"

                senha = gerar_senha_aleatoria()
                senha_criptografada = criptografar_senha(senha)
                gestor.senha = senha_criptografada
                # Query de insert
                insert_query = """
                    INSERT INTO Usuario (
                        cpf, nome, telefone, email, empresa_id, grupo_id, tipo, senha
                    )
                    VALUES (%(cpf)s, %(nome)s, %(telefone)s, %(email)s, %(empresa_id)s, %(grupo_id)s , 'G', %(senha)s)
                """
                try:
                    await cursor.execute(insert_query, gestor.dict(), prepare=True)
                    enviar_email(gestor.email, senha)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        return 200, ""

    async def altera_gestor(self, gestor_update: Gestor):
        gestor = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                if not await self.verifica_email_existente(cursor, gestor_update.id, gestor_update.email):
                    return 409, "Email já existe"
                if not await self.verifica_cpf_existente(cursor, gestor_update.id, gestor_update.cpf):
                    return 409, "CPF já existente"

                if gestor_update.status == 'I':
                    self.mascara_campos(gestor_update)

                update_query = """
                    UPDATE Usuario
                    SET
                        nome = %(nome)s,
                        email = %(email)s,
                        cpf = %(cpf)s,
                        telefone = %(telefone)s,
                        status = %(status)s,
                        empresa_id = %(empresa_id)s
                    WHERE id = %(id)s and tipo = 'G'
                """
                try:
                    await cursor.execute(update_query, gestor_update.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        gestor = await self.buscar_gestor(gestor_update.id)

        if not gestor:
            return 404, "Erro atualizar Gestor"

        return 200, gestor

    async def buscar_operador(self, id: int):
        operador = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = f"""
                           SELECT 
                               *
                           FROM Usuario u 
                           where u.id = %s and tipo = 'O';
                       """

                await cursor.execute(sql, (id,), prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}

                operador = Operador(**result)

        return operador



    async def buscar_operadores(self, empresa_id: int | None = None, unidade_id: int | None = None,
                                turno: str | None = None,
                                codigo: str | None = None, status: str | None = None,
                                disp_ordem: bool | None = None):
        operadores = []

        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:

                params = []

                sql = f"""SELECT 
                            u.*,
                            e.nome empresa,
                            un.nome unidade
                        FROM Usuario u
                        LEFT JOIN empresa e on e.id = u.empresa_id  
                        LEFT JOIN unidade un on un.id = u.unidade_id 
                        WHERE 1=1 and tipo = 'O'
                    """

                if empresa_id:
                    sql += " AND u.empresa_id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                if turno:
                    sql += " AND u.turno LIKE %s"
                    params.append(f"%{turno}%")

                if codigo:
                    sql += " AND LOWER(u.nome) LIKE LOWER(%s)"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)

                if disp_ordem:
                    sql += """ AND u.id not in (
                        SELECT oso.operador_id from ordem_servico_operador oso 
                        INNER JOIN ordem_servico os ON os.id = oso.ordem_servico_id 
                        WHERE os.status IN ('A', 'E')
                    ) """

                await cursor.execute(sql, params, prepare=True)

                result = await cursor.fetchall()

                if not result:
                    return []

                for row in result:
                    operadores.append(Operador(**row))

        return operadores

    async def inserir_operador(self, operador: Usuario):
        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                if not await self.verifica_email_existente(cursor, operador.id, operador.email):
                    return 409, "Email já existe"
                if not await self.verifica_cpf_existente(cursor, operador.id, operador.cpf):
                    return 409, "CPF já existente"

                query_qtd_op = "SELECT COUNT(*) FROM Usuario WHERE tipo = 'O'"
                await cursor.execute(query_qtd_op)
                qtd_op = (await cursor.fetchone())[0]
                ano_atual = datetime.now().year
                novo_op = qtd_op + 1
                matricula = f"{ano_atual}00{novo_op:03d}"
                operador.matricula = matricula

                senha = gerar_senha_aleatoria()
                enviar_email(operador.email, senha)
                senha_criptografada = criptografar_senha(senha)

                operador.senha = senha_criptografada

                # Query de insert
                insert_query = """
                    INSERT INTO Usuario (
                        cpf, nome, email, telefone, matricula, turno, gestor_id, grupo_id, empresa_id, unidade_id, tipo, senha
                    )
                    VALUES (%(cpf)s, %(nome)s, %(email)s, %(telefone)s, %(matricula)s, %(turno)s, %(gestor_id)s,
                     %(grupo_id)s, %(empresa_id)s, %(unidade_id)s, 'O', %(senha)s)
                """
                try:
                    await cursor.execute(insert_query, operador.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        return 201, ""

    async def altera_operador(self, operador_update: Operador):
        operador = {}

        async with AsyncDatabase() as conn:
            async with conn.cursor() as cursor:

                if not await self.verifica_email_existente(cursor, operador_update.id, operador_update.email):
                    return 409, "Email já existe"
                if not await self.verifica_cpf_existente(cursor, operador_update.id, operador_update.cpf):
                    return 409, "CPF já existente"

                if operador_update.status == 'I':
                    self.mascara_campos(operador_update)

                update_query = """
                       UPDATE Usuario
                       SET
                           nome = %(nome)s,
                           email = %(email)s,
                           cpf = %(cpf)s,
                           telefone = %(telefone)s,
                           status = %(status)s,
                           turno = %(turno)s,
                           unidade_id = %(unidade_id)s
                       WHERE id = %(id)s and tipo = 'O'
                   """
                try:
                    await cursor.execute(update_query, operador_update.dict(), prepare=True)
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError(e)
                finally:
                    await conn.commit()

        operador = await self.buscar_operador(operador_update.id)

        if not operador:
            return 404, "Erro atualizar Operador"

        return 200, operador

    async def busca_usuario(self, id: int):
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = """
                           SELECT *
                           FROM Usuario
                           WHERE id = %s;
                         """
                await cursor.execute(sql, (id,), prepare=True)

                result = await cursor.fetchone()

                if result:
                    return Usuario(**result)
                else:
                    return None


    async def verifica_email_existente(self, db, user, email):
        sql = f"""
                SELECT 
                    u.id id ,
                    u.email email
                FROM Usuario u
                WHERE u.email = %s;
            """
        await db.execute(sql, (email,), prepare=True)
        result = await db.fetchone()

        if result:
            id, email = result
            if id != user:
                return False
        return True

    async def verifica_cpf_existente(self, db, user, cpf):
        sql = f"""
                SELECT
                    u.id id,
                    u.cpf cpf
                FROM Usuario u
                WHERE u.cpf = %s;
            """
        await db.execute(sql, (cpf,), prepare=True)
        result = await db.fetchone()

        if result:
            id, cpf = result
            if id != user:
                return False
        return True


    def mascara_campos(self, usuario):
        usuario.cpf = '***'
        usuario.telefone = '***'
        usuario.email = '***'
        usuario.data_contratacao = None

        if usuario.tipo == 'O':
            usuario.matricula = '***'


    @staticmethod
    def valida_cpf(cpf):
        cpf = cpf.replace('.', '').replace('-', '')

        if len(cpf) == 11:
            digitos_verificadores = cpf[9:]
        else:
            return False

        cpf = cpf[:9]

        try:
            dig_1 = int(cpf[0]) * 1
            dig_2 = int(cpf[1]) * 2
            dig_3 = int(cpf[2]) * 3
            dig_4 = int(cpf[3]) * 4
            dig_5 = int(cpf[4]) * 5
            dig_6 = int(cpf[5]) * 6
            dig_7 = int(cpf[6]) * 7
            dig_8 = int(cpf[7]) * 8
            dig_9 = int(cpf[8]) * 9
        except IndexError:
            return False

        dig_1_ao_9_somados = (dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9)

        dig_10 = dig_1_ao_9_somados % 11

        if dig_10 > 9:
            dig_10 = 0

        cpf += str(dig_10)

        dig_1 = int(cpf[0]) * 0
        dig_2 = int(cpf[1]) * 1
        dig_3 = int(cpf[2]) * 2
        dig_4 = int(cpf[3]) * 3
        dig_5 = int(cpf[4]) * 4
        dig_6 = int(cpf[5]) * 5
        dig_7 = int(cpf[6]) * 6
        dig_8 = int(cpf[7]) * 7
        dig_9 = int(cpf[8]) * 8
        dig_10 = int(cpf[9]) * 9

        dig_1_ao_10_somados = (dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9 + dig_10)

        dig_11 = dig_1_ao_10_somados % 11

        if dig_11 > 9:
            dig_11 = 0

        cpf_validado = cpf + str(dig_11)

        if digitos_verificadores == cpf_validado[9:]:
            return True
        else:
            return False

    async def validar_credenciais(self, login: str, senha: str) -> Optional[Usuario]:
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                login_tipo = "email" if '@' in login and '.' in login else "matricula"

                sql = f"""
                        SELECT *
                        FROM Usuario
                        WHERE {login_tipo} = %s
                        AND status = 'A';
                """

                await cursor.execute(sql, (login,), prepare=True)
                result = await cursor.fetchone()

                if result and bcrypt.checkpw(senha.encode('utf-8'), result['senha'].encode('utf-8')):
                    return Usuario(**result)
                else:
                    return None
