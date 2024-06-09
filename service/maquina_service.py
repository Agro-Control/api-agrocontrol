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

    def buscar_maquinas(self, empresa_id:int,  unidade_id:int | None, codigo: str | None = None, status: str | None = None,
                        diponibilidade_ordem: bool | None = None):

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

                if empresa_id:
                    sql += " AND m.unidade_id in (select u.id from unidade u where u.empresa_id = %s and u.status = 'A')"
                    params.append(empresa_id)

                    if diponibilidade_ordem:
                        sql += " AND m.id NOT IN (select os.maquina_id from ordem_servico os where os.status in ('A', 'E') and os.empresa_id = %s)"
                        params.append(empresa_id)

                elif unidade_id:
                    sql += " AND m.unidade_id = %s"
                    params.append(unidade_id)

                if codigo:
                    sql += " AND m.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND m.status = %s"
                    params.append(status)

                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

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
                        nome, fabricante, modelo, capacidade_operacional, unidade_id
                        )
                    VALUES (%(nome)s, %(fabricante)s, %(modelo)s, %(capacidade_operacional)s,  %(unidade_id)s)
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


