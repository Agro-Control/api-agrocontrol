from datetime import datetime
import traceback
from typing import Optional, List

import bcrypt
from connection.postgres import Database
from errors import DatabaseError
from model.gestor_model import Gestor
from model.operador_model import Operador
from model.usuario_model import Usuario
from service.jwt_service import criptografar_senha, enviar_email, gerar_senha_aleatoria 

class UsuarioService:
    
    def buscar_gestor(self, id: int):
        gestor = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Usuario u 
                        where u.id = %s and tipo = 'G';
                    """
                
                cursor.execute(sql, (id, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                gestor = Gestor(**result)
 
        return gestor

    def buscar_gestores(self, grupo_id: int | None = None, empresa_id: int = None, unidade_id: int = None,
                        codigo: str | None = None, status: str | None = None):
        gestores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
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

                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    gestores.append(Gestor(**row))

        return gestores

    def inserir_gestor(self, gestor: Usuario):
        with Database() as conn: 
            with conn.cursor() as cursor:

                if not self.verifica_email_existente(cursor, gestor.id, gestor.email):
                    return 409, "Email já existe"
                if not self.verifica_cpf_existente(cursor, gestor.id, gestor.cpf):
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
                    cursor.execute(insert_query, gestor.dict(), prepare=True)
                    enviar_email(gestor.email, senha)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

        return 200, ""

    def altera_gestor(self, gestor_update: Gestor):
        gestor = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor:

                if not self.verifica_email_existente(cursor, gestor_update.id, gestor_update.email):
                    return 409, "Email já existe"
                if not self.verifica_cpf_existente(cursor, gestor_update.id, gestor_update.cpf):
                    return 409, "CPF já existente"

                # Query de update
                # senha = gestor_update.senha
                # gestor_update.senha = criptografar_senha(senha)
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
                    cursor.execute(update_query, gestor_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
        gestor = self.buscar_gestor(gestor_update.id)

        if not gestor:
            return 404, "Erro atualizar Gestor"
    
        return 200, gestor


    def buscar_operador(self, id: int):
        operador = {}
            
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Usuario u 
                        where u.id = %s and tipo = 'O';
                    """
                
                cursor.execute(sql, (id, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                operador = Operador(**result)

        return operador

    def buscar_operadores(self, empresa_id: int | None = None, unidade_id: int | None = None, turno: str | None = None,
                          codigo: str | None = None, status: str | None = None, disp_ordem: bool | None = None):
        operadores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
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

                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    operadores.append(Operador(**row))

        return operadores

    def inserir_operador(self, operador: Usuario):
        with Database() as conn: 
            with conn.cursor() as cursor:

                if not self.verifica_email_existente(cursor, operador.id, operador.email):
                    return 409, "Email já existe"
                if not self.verifica_cpf_existente(cursor, operador.id, operador.cpf):
                    return 409, "CPF já existente"

                queyr_qtd_op = "SELECT COUNT(*) FROM Usuario WHERE tipo = 'O'"
                cursor.execute(queyr_qtd_op)
                qtd_op = cursor.fetchone()[0]
                ano_atual = datetime.now().year
                novo_op = qtd_op + 1
                matricula = f"{ano_atual}00{novo_op:03d}"
                operador.matricula = matricula

                senha = gerar_senha_aleatoria()
                #enviar_email(operador.email, senha)
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
                    cursor.execute(insert_query, operador.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                   
        return 201, ""


    def altera_operador(self, operador_update: Operador):
        operador = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor:

                if not self.verifica_email_existente(cursor, operador_update.id, operador_update.email):
                    return 409, "Email já existe"
                if not self.verifica_cpf_existente(cursor, operador_update.id, operador_update.cpf):
                    return 409, "CPF já existente"

                # Query de update
                # senha = operador_update.senha
                # operador_update.senha = criptografar_senha(senha)
                update_query = """
                    UPDATE Usuario
                    SET
                        nome = %(nome)s,
                        turno = %(turno)s,
                        email = %(email)s,
                        cpf = %(cpf)s,
                        gestor_id = %(gestor_id)s,
                        unidade_id = %(unidade_id)s,
                        status = %(status)s
                    WHERE id = %(id)s and tipo = 'O'
                """  
                try:
                    cursor.execute(update_query, operador_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

        operador = self.buscar_operador(operador_update.id)

        if not operador:
            return 404, "Erro alteração do Operador"
    
        return 200, operador

    def busca_usuario(self, id:int):
        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = """
                           SELECT *
                           FROM Usuario
                           WHERE id = %s;
                         """
                cursor.execute(sql, (id,), prepare=True)

                result = cursor.fetchone()

                if result:
                    return Usuario(**result)
                else:
                    return None


    def verifica_email_existente(self, db, user, email):
        sql = f"""
                SELECT 
                    u.id id ,
                    u.email email
                FROM Usuario u
                WHERE u.email = %s;
            """
        db.execute(sql, (email,), prepare=True)
        result = db.fetchone()

        if result:
            id, email = result
            if id != user:
                return False
        return True


    def verifica_cpf_existente(self, db, user, cpf):
        sql = f"""
                SELECT
                    u.id id,
                    u.cpf cpf
                FROM Usuario u
                WHERE u.cpf = %s;
            """
        db.execute(sql, (cpf,), prepare=True)
        result = db.fetchone()

        if result:
            id, cpf = result
            if id != user:
                return False
        return True


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


    def validar_credenciais(self, login: str, senha: str) -> Optional[Usuario]:
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                login_tipo = "email" if '@' in login and '.' in login else "matricula"

                sql = f"""
                        SELECT *
                        FROM Usuario
                        WHERE {login_tipo} = %s;
                """

                cursor.execute(sql, (login,), prepare=True)
                result = cursor.fetchone()

                if result and bcrypt.checkpw(senha.encode('utf-8'), result['senha'].encode('utf-8')):
                    return Usuario(**result)
                else:
                    return None