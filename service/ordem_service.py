from connection.postgres import Database, AsyncDatabase
from connection.mongo import Mongo
from errors import EventError
from errors import DatabaseError
from model.ordem_de_servico_model import OrdemServico
from model.operador_model import Operador

class OrdemService:
    
    def busca_ordem_ativa_maquina(self, maquina_id: int): 
        ordem = {}

        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = f"""select 
                            os.id,
                            os.data_inicio,
                            os.status,
                            os.velocidade_minima,
                            os.velocidade_maxima,
                            os.rpm 
                        from ordem_servico as os 
                        where os.maquina_id = %s 
                        and os.status = 'A';
                    """
            
                #quando model estiver pronta usar aqui
                cursor.execute(sql, (maquina_id,), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}
                
                ordem = OrdemServico(**result)
 
        return ordem

    def busca_ordem_servico(self, id_ordem: int):
        ordem = {}
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                sql = f"""
                    SELECT os.* ,STRING_AGG(oso.operador_id::text, ',') operadores FROM ordem_servico os 
                    INNER JOIN ordem_servico_operador oso ON (oso.ordem_servico_id = os.id)
                    WHERE os.id = %s
                    GROUP BY os.id
                """
                
                cursor.execute(sql, (id_ordem,), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}
                
                ordem = OrdemServico(**result)
        return ordem


    async def busca_ordem_servico_async(self, id_ordem:int):
        async with AsyncDatabase() as conn:
            async with conn.cursor(row_factory=await AsyncDatabase.get_cursor_type("dict")) as cursor:
                sql = f"""
                           SELECT os.* ,STRING_AGG(oso.operador_id::text, ',') operadores FROM ordem_servico os 
                           INNER JOIN ordem_servico_operador oso ON (oso.ordem_servico_id = os.id)
                           WHERE os.id = %s
                           GROUP BY os.id
                       """

                await cursor.execute(sql, (id_ordem,), prepare=True)

                result = await cursor.fetchone()

                if not result:
                    return {}
                # print(**result)

                ordem = OrdemServico(**result)
        return ordem




    
    def busca_ordens_servicos(self, empresa_id: int | None = None, status: str | None = None):
        ordens = []
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                params = []
                sql = f"""
                    SELECT 
                        os.*, 
                        m.nome AS nome_maquina, 
                        json_agg(json_build_object('id', u.id, 'nome', u.nome, 'turno', u.turno)) AS operadores
                    FROM ordem_servico os
                    INNER JOIN ordem_servico_operador oso ON oso.ordem_servico_id = os.id
                    INNER JOIN usuario u ON u.id = oso.operador_id
                    INNER JOIN maquina m ON m.id = os.maquina_id
                    WHERE 1=1
                """
                
                if empresa_id:
                    sql += " AND os.empresa_id = %s"
                    params.append(empresa_id)

                if status:
                    sql += " AND os.status = %s"
                    params.append(status)
                
                sql += " GROUP BY os.id, m.nome"

                cursor.execute(sql, params, prepare=True)
                result = cursor.fetchall()
            
                if not result:
                    return []

                for row in result:
                    operadores = [
                        Operador(**op).dict(exclude_none=True) for op in row['operadores']
                    ]
                    ordem = OrdemServico(**row)
                    ordem.operadores = operadores
                    ordens.append(ordem)

        return ordens
   
    def inserir_ordem_servico(self, ordem_servico: OrdemServico):
        with Database() as conn: 
            with conn.cursor() as cursor:
                # Query de insert
                insert_query = """
                    INSERT INTO Ordem_Servico (data_inicio, velocidade_minima, velocidade_maxima, rpm, gestor_id, empresa_id, unidade_id, talhao_id, maquina_id)
                    VALUES (%(data_inicio)s, %(velocidade_minima)s, %(velocidade_maxima)s, %(rpm)s, %(gestor_id)s, %(empresa_id)s, %(unidade_id)s, %(talhao_id)s, %(maquina_id)s)
                    RETURNING id
                """
                try:
                    cursor.execute(insert_query, ordem_servico.dict(), prepare=True)
                    id_ultimo_registro = cursor.fetchone()[0]
                
                    values = [f"({id_ultimo_registro}, {id})" for id in ordem_servico.operadores_ids]

                    insert_query = f"""
                        INSERT INTO Ordem_Servico_Operador (ordem_servico_id, operador_id)
                        VALUES { ", ".join(values)};
                    """
                    # print(insert_query)
                    cursor.execute(insert_query,prepare=True)

                except Exception as e:
                    print("Deu erro no insert")
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
                    # conn.rollback()

        return

    def altera_ordem_servico(self, ordem_update: OrdemServico):
        ordem = {}
        
        with Database() as conn: 
            with conn.cursor() as cursor: 
                # Query de update
                update_query = """
                    UPDATE Ordem_Servico
                    SET 
                        status = %(status)s,
                        velocidade_minima = %(velocidade_minima)s,
                        velocidade_maxima = %(velocidade_maxima)s,
                        rpm = %(rpm)s
                    WHERE id = %(id)s;
                """

                try:
                    cursor.execute(update_query, ordem_update.dict(), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)

                sql = """
                    DELETE FROM ordem_servico_operador oso WHERE oso.ordem_servico_id = %s;
                """
                try:
                    cursor.execute(sql, ordem_update.id, prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)

                values = [f"({ordem_update.id}, {id})" for id in ordem_update.operadores]

                insert_query = f"""
                                INSERT INTO Ordem_Servico_Operador (ordem_servico_id, operador_id)
                                VALUES {", ".join(values)};
                            """
                try:
                    cursor.execute(insert_query, prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)

                conn.commit()
                
                ordem = self.busca_ordem_servico(ordem_update.id)

                if not ordem:
                    return {}
    
        return ordem

    def altera_status_ordem_servico(self, id_ordem: int, status:str):
        with Database() as conn:
            with conn.cursor() as cursor:
                update_query = """
                    UPDATE Ordem_Servico
                    SET 
                        status = %s
                    WHERE id = %s;
                """

                try:
                    cursor.execute(update_query, (status, id_ordem,), prepare=True)
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(e)
                finally:
                    conn.commit()
