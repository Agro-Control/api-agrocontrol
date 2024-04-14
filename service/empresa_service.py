from connection.postgres import Database
from errors import DatabaseError
from model.empresa_model import Empresa 

class EmpresaService:
    
    def buscar_empresa(self, id_empresa: int):
        empresa = {}
        
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""
                        SELECT 
                            *
                        FROM Empresa e 
                        where e.id = %s ;
                    """
                
                cursor.execute(sql, (id_empresa, ), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}

                empresa = Empresa(**result)
 
        return empresa

##################################################
    def buscar_empresas(self, codigo: str | None = None, status: str | None = None, estado: str | None = None, cidade: str | None = None):
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
                    sql += " AND e.nome LIKE %s"
                    params.append(f"%{codigo}%")

                if status:
                    sql += " AND e.status = %s"
                    params.append(status)
                
                if estado:
                    sql += " AND e.estado LIKE %s"
                    params.append(estado)
                
                if cidade:
                    sql += " AND e.cidade LIKE %s"
                    params.append(f"%{cidade}%")
    
                print(sql)
                
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
                        numero, complemento, data_criacao, telefone_responsavel, email_responsavel, nome_responsavel, gestor_id
                    )
                    VALUES (%(nome)s, %(cnpj)s, %(telefone)s, %(cep)s, %(estado)s, %(cidade)s, %(bairro)s, %(logradouro)s,
                    %(numero)s, %(complemento)s, %(data_criacao)s, %(telefone_responsavel)s, %(email_responsavel)s, %(nome_responsavel)s, %(gestor_id)s)
                """
                try:
                    cursor.execute(insert_query, empresa.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()

                    
        return empresa

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
                        status = %(status)s,
                        telefone_responsavel = %(telefone_responsavel)s,
                        email_responsavel = %(email_responsavel)s,
                        nome_responsavel = %(nome_responsavel)s
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
