from connection.postgres import Database
from errors import DatabaseError
from model.talhao_model import Talhao 

class TalhaoService:
    
    def buscar_talhao(self, id_talhao: int):
        talhao = {}
    
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Talhao t
                        WHERE t.id = %s;
                    """
                
                cursor.execute(sql, (id_talhao, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                talhao = Talhao(**result)
 
        return talhao

    def buscar_talhoes(self, id_empresa:int | None = None, codigo: str | None = None, status: str | None = None):

        talhoes = []

        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                params = []

                sql = f"""
                        SELECT 
                            *
                        FROM Talhao t
                        WHERE 1=1
                    """

                if id_empresa:
                    sql += "AND t.empresa_id = %s"

                if codigo:
                    sql += " AND t.codigo LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND t.status = %s"
                    params.append(status)
                
                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()
                
                if not result:
                    return []

                for row in result:
                    talhoes.append(Talhao(**row))

 
        return talhoes

    def inserir_talhao(self, talhao: Talhao):
        with Database() as conn: 
            with conn.cursor() as cursor:
            
                # Query de insert
                insert_query = """
                    INSERT INTO talhao (
                        codigo, tamanho, gestor_id, empresa_id
                        )
                    VALUES (%(codigo)s, %(tamanho)s, %(gestor_id)s, %(empresa_id)s)
                """
                try:
                    cursor.execute(insert_query, talhao.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

        return talhao


    def altera_talhao(self, talhao_update: Talhao):
        
        talhao = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
                # Query de update
                update_query = """
                    UPDATE talhao
                    SET
                        codigo = %(codigo)s,
                        tamanho = %(tamanho)s,
                        status = %(status)s
                    WHERE id = %(id)s
                    and empresa_id = %(empresa_id)s
                """
                
                try:
                    cursor.execute(update_query, talhao_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                talhao = self.buscar_talhao(talhao_update.id)

                if not talhao:
                    return {}
    
        return talhao


