from logging import exception
from connection.postgres import Database
from errors import DatabaseError
from model.grupo_model import Grupo

class GrupoService:
    
    def buscar_grupo(self, grupo_id: int):
        grupo = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Grupo e 
                        where e.id = %s ;
                    """
                
                cursor.execute(sql, (grupo_id, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                grupo = Grupo(**result)
 
        return grupo

    def buscar_grupos(self):
        grupos = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Grupo e
                        WHERE 1=1
                    """
                
                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    grupos.append(Grupo(**row))

        return grupos


    def inserir_grupo(self, grupo: Grupo):
        with Database() as conn: 
            with conn.cursor() as cursor:

                insert_query = """
                    INSERT INTO grupo (
                        nome
                    )
                    VALUES (%(nome)s)
                """
                try:
                    cursor.execute(insert_query, grupo.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                    
        return 

    def altera_grupo(self, grupo_update: Grupo):
        grupo = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
        # Query de update
                update_query = """
                    UPDATE Grupo
                    SET
                        nome = %(nome)s,
                        status = %(status)s
                    WHERE id = %(id)s
                """
                
                try:
                    cursor.execute(update_query, grupo_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                grupo = self.buscar_grupo(grupo_update.id)

                if not grupo:
                    return {}
    
        return grupo

