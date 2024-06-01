from logging import exception
from connection.postgres import Database
from errors import DatabaseError
from model.empresa_model import Empresa 

class EmpresaService:
    
    def buscar_empresa(self, empresa_id: int):
        empresa = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Empresa e 
                        where e.id = %s ;
                    """
                
                cursor.execute(sql, (empresa_id, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                empresa = Empresa(**result)
 
        return empresa

##################################################
    def buscar_empresas(self, codigo: str | None = None, grupo_id: int | None = None, status: str | None = None,
                        disp: bool | None = None, estado: str | None = None):
        empresas = []
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
    
                params = []

                sql = f"""SELECT 
                            *
                        FROM Empresa e
                        WHERE 1=1
                    """

                if codigo:
                    sql += " AND LOWER(e.nome) LIKE LOWER(%s)"
                    params.append(f"%{codigo.lower()}%")

                if status:
                    sql += " AND e.status = %s"
                    params.append(status)

                if estado:
                    sql += " AND e.estado = %s"
                    params.append(estado)
                
                if grupo_id:
                    sql += " AND grupo_id = %s"
                    params.append(grupo_id)

                    if disp:
                        sql += (" AND e.id not in ( select distinct u.empresa_id from usuario u where u.status= 'A' and "
                                "u.tipo= 'G')")
                        params.append(grupo_id)
                
                cursor.execute(sql, params, prepare=True)
                
                result = cursor.fetchall()

                if not result:
                    return []
                
                for row in result:
                    empresas.append(Empresa(**row))

        return empresas


    def inserir_empresa(self, empresa: Empresa):
        with Database() as conn: 
            with conn.cursor() as cursor:

                # Query de insert#############################################
                insert_query = """
                    INSERT INTO empresa (
                        nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro,
                        numero, complemento, grupo_id
                    )
                    VALUES (%(nome)s, %(cnpj)s, %(telefone)s, %(cep)s, %(estado)s, %(cidade)s, %(bairro)s, %(logradouro)s,
                    %(numero)s, %(complemento)s, %(grupo_id)s)
                """
                try:
                    cursor.execute(insert_query, empresa.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

                    
        return 

    def altera_empresa(self, empresa_update: Empresa):
        empresa = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
        # Query de update
                update_query = """
                    UPDATE Empresa
                    SET
                        nome = %(nome)s,
                        cnpj = %(cnpj)s,
                        telefone = %(telefone)s,
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
                    cursor.execute(update_query, empresa_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                
                empresa = self.buscar_empresa(empresa_update.id)

                if not empresa:
                    return {}
    
        return empresa


    def busca_estado_empresas(self, grupo_id: int | None = None, empresa_id: int | None = None):
        estados = {}

        with Database() as conn: 
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        estado
                    FROM empresa
                    WHERE 1=1
                """

                if grupo_id:
                    sql += " AND grupo_id = %s"

                if empresa_id:
                    sql += " AND id = %s"

                
                sql += " GROUP BY estado";
                
                try:
                    cursor.execute(sql, (grupo_id, ), prepare= True)
                except Exception as e:
                     raise DatabaseError(e)
                

                result = cursor.fetchall()

                if not result:
                    return {}
                
                estados = {
                    "estados": result
                }
                
        return estados



