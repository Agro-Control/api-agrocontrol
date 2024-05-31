from datetime import datetime
import traceback
from typing import Optional, List

import bcrypt
from connection.postgres import Database
from errors import DatabaseError
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

                gestor = Usuario(**result)
 
        return gestor

    def buscar_gestores(self, grupo_id: int | None = None, empresa_id: int = None, unidade_id: int = None,
                        codigo: str | None = None, status: str | None = None):
        gestores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Usuario u
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
                    sql += " AND u.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)
                
                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    gestores.append(Usuario(**row))

        return gestores


    def inserir_gestor(self, gestor: Usuario):
        with Database() as conn: 
            with conn.cursor() as cursor:

                senha = gerar_senha_aleatoria()
                enviar_email(gestor.email, senha)
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
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

                    
        return 

    def altera_gestor(self, gestor_update: Usuario):
        gestor = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
                # Query de update
                senha = gestor_update.senha
                gestor_update.senha = criptografar_senha(senha)
                update_query = """
                    UPDATE Usuario
                    SET
                        nome = %(nome)s,
                        email = %(email)s,
                        telefone = %(telefone)s,
                        status = %(status)s,
                        empresa_id = %(empresa_id)s,
                        senha = %(senha)s
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
                    return {}
    
        return gestor


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

                operador = Usuario(**result)

        return operador

    def buscar_operadores(self, unidade_id: int | None = None, turno: str | None = None, codigo: str | None = None, status: str | None = None, 
                          disp_ordem: bool | None = None):
        operadores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Usuario u
                        WHERE 1=1 and tipo = 'O'
                    """

                if unidade_id:
                    sql += "AND u.unidade_id = %s"
                    params.append(unidade_id)

                if turno:
                    sql += " AND u.turno LIKE %s"
                    params.append(f"%{turno}%")
                
                if codigo:
                    sql += " AND u.nome LIKE %s"
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
                    operadores.append(Usuario(**row))

        return operadores

    def inserir_operador(self, operador: Usuario):
        with Database() as conn: 
            with conn.cursor() as cursor:

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
                   
        return 


    def altera_operador(self, operador_update: Usuario):
        operador = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
        # Query de update
        #         senha = operador_update.senha
        #         operador_update.senha = criptografar_senha(senha)
                update_query = """
                    UPDATE Usuario
                    SET
                        nome = %(nome)s,
                        turno = %(turno)s,
                        email = %(email)s,
                        gestor_id = %(gestor_id)s,
                        unidade_id = %(unidade_id)s,
                        status = %(status)s,
                        matricula = %(matricula)s
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
                    return {}
    
        return operador

    # temporario
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

    def busca_usuarios(self, grupo_id: int = None, empresa_id: int = None, unidade_id: int = None, nome: str = None,
                       status: str = None, tipo: str = None):
        usuarios = []
        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                params = []
                sql = """
                           SELECT *
                           FROM Usuario u
                           WHERE 1=1
                           AND u.tipo != 'A'
                         """

                if grupo_id:
                    sql += " AND u.grupo_id = %s "
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND u.empresa_id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)

                if tipo:
                    sql += " AND u.tipo = %s"

                    params.append(tipo)

                if nome:
                    sql += " AND u.nome LIKE %s"
                    params.append(f"%{nome}%")

                # print(sql, flush=True)
                try:
                    cursor.execute(sql, params, prepare=True)
                except:
                    print(traceback.format_exc())

                result = cursor.fetchall()

                if not result:
                    return usuarios

                for row in result:
                    usuarios.append(Usuario(**row))

        return usuarios
    
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