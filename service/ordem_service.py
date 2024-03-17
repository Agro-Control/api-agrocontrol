from connection.postgres import Database
from connection.mongo import Mongo
from errors import EventError
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
                        where os.id_maquina = %s 
                        and os.status = 'A';
                    """
            
                #quando model estiver pronta usar aqui
                cursor.execute(sql, (id_maquina,), prepare=True)
                
                result = cursor.fetchone()
            
                if not result:
                    return {}
                
                
                ordem = OrdemServico(**result)
 
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

