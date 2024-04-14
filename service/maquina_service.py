from connection.postgres import Database
from errors import DatabaseError
from model.maquina_model import Maquina 

class MaquinaService:
    
    def buscar_maquina(self, id_maquina: int):
        maquina = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Maquina m
                        WHERE m.id = %s;
                    """
                
                cursor.execute(sql, (id_maquina,), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                maquina = Maquina(**result)
 
        return maquina

    def buscar_maquinas(self, id_empresa:int | None, codigo: str | None = None, status: str | None = None):

        maquinas = []
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                params = []

                sql = f"""
                        SELECT 
                            *
                        FROM Maquina m
                        WHERE 1=1
                    """
                
                if id_empresa:
                    sql += "AND m.empresa_id = %s"
                    params.append(id_empresa)

                if codigo:
                    sql += " AND m.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND m.status = %s"
                    params.append(status)

                
                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()
                print(result) 
                if not result:
                    return []

                for row in result:
                    maquinas.append(Maquina(**row))

 
        return maquinas

    def inserir_maquina(self, maquina: Maquina):
        with Database() as conn: 
            with conn.cursor() as cursor:
            
                # Query de insert
                insert_query = """
                    INSERT INTO maquina (
                        nome, fabricante, modelo, capacidade_operacional, gestor_id, empresa_id
                        )
                    VALUES (%(nome)s, %(fabricante)s, %(modelo)s, %(capacidade_operacional)s, %(gestor_id)s, %(empresa_id)s)
                """
                try:
                    cursor.execute(insert_query, maquina.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

                

        return  


    def altera_maquina(self, maquina_update: Maquina):
        
        maquina = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
                # Query de update
                update_query = """
                    UPDATE maquina
                    SET
                        nome = %(nome)s,
                        fabricante = %(fabricante)s,
                        modelo = %(modelo)s,
                        capacidade_operacional = %(capacidade_operacional)s,
                        status = %(status)s
                    WHERE id = %(id)s
                """
                
                try:
                    cursor.execute(update_query, maquina_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                maquina = self.buscar_maquina(maquina_update.id)

                if not maquina:
                    return {}
    
        return maquina


