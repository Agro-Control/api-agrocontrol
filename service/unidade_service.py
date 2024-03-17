from connection.postgres import Database
from errors import DatabaseError
from model.unidade_model import Unidade 

class UnidadeService:
    
    def buscar_unidade(self, id_unidade: int):
        unidade = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Unidade u 
                        where u.id = %s ;
                    """
                
                cursor.execute(sql, (id_unidade, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                unidade = Unidade(**result)
 
        return unidade


    def buscar_unidades(self, codigo: str | None = None, status: str | None = None):
        unidades = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Unidade u
                        WHERE 1=1
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
                    unidades.append(Unidade(**row))

        return unidades


    def inserir_unidade(self, unidade: Unidade):
        with Database() as conn: 
            with conn.cursor() as cursor:

                # Query de insert
                insert_query = """
                    INSERT INTO unidade (
                        nome, cnpj, cep, estado, cidade, bairro, logradouro,
                        numero, complemento, gestor_id
                    )
                    VALUES (%(nome)s, %(cnpj)s, %(cep)s, %(estado)s, %(cidade)s, %(bairro)s, %(logradouro)s,
                    %(numero)s, %(complemento)s, %(gestor_id)s)
                """
                try:
                    cursor.execute(insert_query, unidade.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

                    
        return 

    def altera_unidade(self, unidade_update: Unidade):
        unidade = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
        # Query de update
                update_query = """
                    UPDATE Unidade
                    SET
                        nome = %(nome)s,
                        cnpj = %(cnpj)s,
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
                    cursor.execute(update_query, unidade_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                unidade = self.buscar_unidade(unidade_update.id)

                if not unidade:
                    return {}
    
        return unidade
