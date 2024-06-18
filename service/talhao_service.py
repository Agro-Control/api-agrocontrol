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

    def buscar_talhoes(self, empresa_id: int | None= None, unidade_id:int | None = None, codigo: str | None = None, status: str | None = None):

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

                if empresa_id:
                    sql += " AND t.unidade_id in (select u.id from unidade u where u.empresa_id = %s and u.status = 'A')"
                    params.append(empresa_id)


                if unidade_id:
                    sql += "AND t.unidade_id = %s"
                    params.append(unidade_id)
                    
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
                        codigo, tamanho, unidade_id
                        )
                    VALUES (%(codigo)s, %(tamanho)s, %(unidade_id)s)
                """
                try:
                    cursor.execute(insert_query, talhao.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

        return  


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
                    and unidade_id = %(unidade_id)s
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


