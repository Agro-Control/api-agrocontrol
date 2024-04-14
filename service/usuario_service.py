from connection.postgres import Database
from errors import DatabaseError
from model.usuario_model import Usuario 

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

    def buscar_gestores(self, codigo: str | None = None, status: str | None = None):
        gestores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Usuario u
                        WHERE 1=1 and tipo = 'G'
                    """

                if codigo:
                    sql += " AND u.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)
    
                print(sql)
                
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

                # Query de insert
                insert_query = """
                    INSERT INTO Usuario (
                        cpf, nome, telefone, email, gestor_id, unidade_id, tipo
                    )
                    VALUES (%(cpf)s, %(nome)s, %(telefone)s, %(email)s, %(gestor_id)s, %(unidade_id)s, 'G')
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
                update_query = """
                    UPDATE Usuario
                    SET
                        cpf = %(nome)s,
                        nome = %(cnpj)s,
                        telefone = %(cep)s,
                        status = %(estado)s,
                        email = %(cidade)s,
                        gestor_id = %(bairro)s,
                        unidade_id = %(logradouro)s
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

    def buscar_operadores(self, codigo: str | None = None, status: str | None = None):
        operadores = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Usuario u
                        WHERE 1=1 and tipo = 'O'
                    """

                if codigo:
                    sql += " AND u.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND u.status = %s"
                    params.append(status)
    
                print(sql)
                
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

                # Query de insert
                insert_query = """
                    INSERT INTO Usuario (
                        cpf, nome, email, matricula, turno, gestor_id, empresa_id, tipo
                    )
                    VALUES (%(cpf)s, %(nome)s, %(email)s, %(matricula)s, %(turno)s, %(gestor_id)s, %(empresa_id)s, 'O')
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
                update_query = """
                    UPDATE Usuario
                    SET
                        cpf = %(nome)s,
                        nome = %(cnpj)s,
                        status = %(estado)s,
                        email = %(cidade)s,
                        matricula = %(matricula)s,
                        turno = %(turno)s,
                        gestor_id = %(bairro)s,
                        empresa_id = %(logradouro)s
                    WHERE id = %(id)s and tipo = 'O'
                """
                
                try:
                    cursor.execute(update_query, operador_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                operador = self.buscar_gestor(operador_update.id)

                if not operador:
                    return {}
    
        return operador