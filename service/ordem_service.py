from connection.postgres import Database
from connection.mongo import Mongo
from errors import EventError

class OrdemService:
    
    def busca_ordem_maquina(self, id_maquina: int): 
        ordem = {}

        with Database() as conn: 
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                sql = """select 
                            os.id_ordem_servico,
                            os.data_inicio,
                            os.status,
                            os.velocidade_minima,
                            os.velocidade_maxima,
                            os.rpm_minimo,
                            os.rpm_maximo 
                        from ordem_servico as os where os.id_maquina_pk = %s and os.status='A';
                    """
            
                #quando model estiver pronta usar aqui
                cursor.execute(sql, (id_maquina,), prepare=True)
            
                ordem = cursor.fetchone()
            
                if not ordem:
                    return ordem

                # {'id_ordem_servico': 1, 'data_inicio': datetime.datetime(2023, 11, 11, 8, 0), 'data_fim': None, 'status': 'A', 'velocidade_minima': 10.5, 
                # 'velocidade_maxima': 20.5, 'rpm_minimo': 1000.0, 'rpm_maximo': 2000.0, 'id_maquina_pk': 1}
                
                #gambiarra temporaria para mostrar os campos
                ordem["data_inicio"] = ordem["data_inicio"].strftime("%Y-%m-%d %H:%M:%S")
 
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

