from connection.postgres import Database
from connection.mongo import Mongo
from errors import EventError
from errors import DatabaseError
from model.ordem_de_servico_model import OrdemServico

class OrdemService:
    
    def busca_ordem_ativa_maquina(self, id_maquina: int): 
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
                cursor.execute(sql, (id_maquina,), prepare=True)
                
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
    
    def busca_ordens_servicos(self, id_empresa: int | None = None, status: str | None = None):
        ordens = []
        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                params = []
                sql = f"""
                    SELECT os.* , STRING_AGG(oso.operador_id::text, ',') operadores FROM ordem_servico os 
                    INNER JOIN ordem_servico_operador oso ON (oso.ordem_servico_id = os.id)
                    WHERE 1=1 
                """
                
                if id_empresa:
                    sql += " AND os.id_empresa = %s"
                    params.append(id_empresa)

                if status:
                    sql += " AND os.status = %s"
                    params.append(status)
                
                sql += " GROUP BY os.id"

                cursor.execute(sql, params, prepare=True)
                result = cursor.fetchall()
            
                if not result:
                    return []

                for row in result:
                    print(row)
                    ordem = OrdemServico(**row)
                    
                    ids_operadores = list(map(int, row['operadores'].split(',')))
                    ordem.operadores_ids = ids_operadores
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
                
                    values = [f"({id_ultimo_registro},{id})" for id in ordem_servico.operadores_ids]


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

    def altera_ordem_servico(self, ordem_update:OrdemServico):
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
                finally:
                    conn.commit()
                
                ordem = self.busca_ordem_servico(ordem_update.id)

                if not ordem:
                    return {}
    
        return ordem
    
    async def busca_eventos_ordem(self,id_ordem: int):
        
        eventos = []
        async with Mongo() as client:
            query = {"ordem_servico": int(id_ordem)}
            
            async for doc in client.tcc.eventos.find(query):
                # esperar o modelo
                # del, é gambiara só pra ter o que mostrar
                del doc["_id"]
                
                eventos.append(doc)
                print(doc)

            return eventos

    async def insere_evento(self, evento):
        async with Mongo() as client:
            try:
                return await client.tcc.eventos.insert_one(evento)
            except Exception as ex:
                raise EventError(ex)

