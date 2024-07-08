import json
import random
import time
import datetime
import traceback
import psycopg
from psycopg.rows import dict_row
import threading
import signal
import os
import argparse
import requests
import math

DB_CONN_STR = """
    dbname=postgres
    user=postgres
    password=postgres
    host=postgresdb
    port=5432
"""

class Evento:
    def __init__(self, name, min_duracao=0, max_duracao=0, probabilidade=0):
        self.id = None
        self.name = name
        self.min_duracao = min_duracao
        self.max_duracao = max_duracao
        self.duracao = 0
        self.probabilidade = probabilidade
        self.set_nova_duracao()
        self.data_inicio = None
        self.data_fim = None
        self.ocioso = None

    def set_nova_duracao(self, duracao=None):
        self.duracao = math.ceil(random.uniform(self.min_duracao, self.max_duracao)) if not duracao else duracao

    def set_data_inicio(self, data_inicio):
        self.data_inicio = data_inicio

    def set_data_fim(self,  data_fim):
        self.data_fim = data_fim

    def set_ociosidade(self):
        self.ocioso = math.ceil(self.duracao / 0.3)
        self.set_nova_duracao(self.duracao + self.ocioso)

class Maquina:
    def __init__(self, id):
        self.id_ = id

class Talhao:
    def __init__(self, id):
        self.id_ = id


class Ordem:
    def __init__(self, id, maquina, operador_ativo, status, data_previsao_fim):
        self.id_ = id
        self.maquina = maquina
        self.operador = operador_ativo
        self.status = status
        self.data_previsao_fim = data_previsao_fim


class Operador:
    def __init__(self, id, nome, empresa_id, grupo_id, turno):
        self.id_ = id
        self.nome = nome
        self.turno = turno
        self.fim_turno = self.get_fim_turno()
        self.empresa_id = empresa_id
        self.grupo_id = grupo_id

    def get_fim_turno(self):
        now = datetime.datetime.now()
        if self.turno == 'M':
            return datetime.datetime(now.year, now.month, now.day, 15, 59, 59)
        elif self.turno == 'T':
            return datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        else:
            return datetime.datetime(now.year, now.month, now.day, 8, 0, 0) + datetime.timedelta(days=1)


class Simulator(threading.Thread):
    def __init__(self, ordem):
        threading.Thread.__init__(self)
        self.running = True
        self.abastecido = False
        self.clima_evento = random.choice([True, False])  # controle se vai ou não chover
        self.ordem = ordem

        self.events = {
            "automaticos": [
                Evento("operacao", 10, 30, 0.7),
                Evento("aguardando_transbordo_automatico", 2, 5, 0.1),
                Evento("deslocamento", 1, 3, 0.2),
            ],
            "manuais": [
                Evento("aguardando_transbordo", 2, 5, 0.3),
                Evento("manutencao", 60, 95, 0.2),
                Evento("clima", 30, 240, 0.01),
                Evento("abastecimento", 7, 10, 0.1),
                Evento("troca_turno", 10, 15),
                Evento("fim_ordem", probabilidade=0.01)
            ]
        }

    def run(self):
        print(f"Iniciando o simulador da Ordem de serviço: {self.ordem.id_}, "
              f"OPERADOR: {self.ordem.operador.id_}, "
              f"TURNO: {self.ordem.operador.turno}, "
              f"MAQUINA: {self.ordem.maquina.id_}, "
              f"TALHAO: {self.ordem.talhao}, "
              f"EMPRESA: {self.ordem.operador.empresa_id}, "
              f"GRUPO: {self.ordem.operador.grupo_id}", flush=True)

        if self.ordem.status == 'A':
            event = Evento("inicio_ordem_servico")
            event.set_data_inicio(data_inicio=datetime.datetime.now())
            event.set_data_fim(data_fim=datetime.datetime.now())
            self.envia_evento(event)
            self.ordem.status = 'E'

        id_col = self.aloca_operador_maquina()

        current_event, old_event = None, None

        while self.running:

            # gerar novo evento
            current_event = self.gera_novo_evento(old_event)

            current_event.set_nova_duracao()
            current_event.set_data_inicio(data_inicio=datetime.datetime.now())
            current_event.set_data_fim(None)

            if current_event.name in ["fim_ordem", "troca_turno"]:
                current_event.set_data_fim(data_fim=datetime.datetime.now())
                old_event.set_data_fim(data_fim=datetime.datetime.now())
                self.envia_evento(old_event, "PUT")
                self.envia_evento(current_event)

                self.desaloca_operador_maquina(id_col)
                break

            if current_event.name == "aguardando_transbordo_automatico":
                if math.ceil(current_event.duracao/0.8) > current_event.max_duracao:
                    current_event.set_ociosidade()
                else:
                    current_event.ocioso = None

            if current_event.name == "clima":
                self.clima_evento = False
            elif current_event.name == "abastecimento":
                self.abastecido = True

            # enviar esse novo evento gerado e recuperar o id dele
            current_event.id = self.envia_evento(current_event)

            if old_event and old_event.name != current_event.name:
                old_event.set_data_fim(data_fim=datetime.datetime.now())
                self.envia_evento(old_event, "PUT")

            old_event = current_event

            time.sleep(current_event.duracao)

        print(f"Ordem [{self.ordem.id_}] simulador encerrado!", flush=True)

    def gera_novo_evento(self, old_event):

        #  regras malditas para ter coerencia nos eventos

        if not old_event or old_event.name in ["manutencao", "abastecimento", "clima", "transbordo", "deslocamento"]:
            return [event for event in self.events["automaticos"] if event.name == "operacao"][0]

        if datetime.datetime.now() >= self.ordem.operador.fim_turno:
            return [event for event in self.events["manuais"] if event.name == "troca_turno"][0]

        if datetime.datetime.now() >= self.ordem.data_previsao_fim:
            return [event for event in self.events["manuais"] if event.name == "fim_ordem"][0]

        if random.random() < 0.8:
            event_list = []
            for event in self.events["automaticos"]:
                if event.name == "operacao" and old_event.name == "operacao":
                    continue

                if event.name == "aguardando_transbordo_automatico" and old_event != "aguardando_transbordo_automatico":
                    continue

                event_list.append(event)

        else:
            event_list = []
            for event in self.events["manuais"]:
                if event.name == "clima" and not self.clima_evento:
                    continue

                if event.name == "abastecimento" and self.abastecido:
                    continue

                event_list.append(event)

        return random.choices(event_list, [event.probabilidade for event in event_list])[0]

    def envia_evento(self, event, metodo='POST'):
        try:
            data = {
                "ordem_servico_id": self.ordem.id_,
                "operador_id": self.ordem.operador.id_,
                "operador_nome": self.ordem.operador.nome,
                "maquina_id": self.ordem.maquina.id_,
                "empresa_id": self.ordem.operador.empresa_id,
                "grupo_id": self.ordem.operador.grupo_id,
                "talhao_id": self.ordem.talhao.id,
                "nome": event.name,
                "data_inicio": event.data_inicio.isoformat(),
                "data_fim": event.data_fim.isoformat() if event.data_fim else None
            }

            if metodo == "PUT":
                data['id'] = event.id
                data['duracao'] = event.duracao

                if event.name == "aguardando_transbordo_automatico" and event.ocioso:
                    data['ocioso'] = event.ocioso

            elif event.name in ["fim_ordem", "troca_turno"]:
                data['duracao'] = event.duracao

            response = requests.request(metodo, 'http://api/eventos', data=json.dumps(data))

            if response:
                response = response.json()
                print(f"Evento {'atualizado 'if metodo == 'PUT' else 'salvo '}[ID] {response['id']}: {data['nome']},"
                      f" [DURACAO] {event.duracao} sec"
                      f" [ORDEM] {self.ordem.id_},"
                      f" [OPERADOR] {self.ordem.operador.id_},"
                      f" [TURNO] {self.ordem.operador.turno}, [MAQUINA] {self.ordem.maquina.id_}",
                    flush=True)

                if metodo == 'POST':
                    return response['id']

                return response

        except:
            print(traceback.format_exc(), flush=True)
            print(response.status_code)
            print(response.text)

        return

    def aloca_operador_maquina(self):
        try:
            data = {
                "operador_id": self.ordem.operador.id_,
                "maquina_id": self.ordem.maquina.id_,
                "ordem_id": self.ordem.id_,
                "data": datetime.datetime.now(),
                "empresa_id": self.ordem.operador.empresa_id,
                "grupo_id": self.ordem.operador.grupo_id
            }

            response = requests.request("POST", 'http://api/ordem/alocar_operador_maquina', data=json.dumps(data))

            if response:
                response = response.json()
                return response['id']
        except:
            pass

    def desaloca_operador_maquina(self, id_col):
        try:
            response = requests.request("DELETE", f'http://api/ordem/alocar_operador_maquina?id={id_col}')
        except:
            pass

        return


class Main:
    def __init__(self):
        self.running = False
        self.ordens_ativas = {}
        signal.signal(signal.SIGINT, self.down)
        signal.signal(signal.SIGTERM, self.down)

    def start(self):
        self.running = True
        time.sleep(5)  # sleep de segurança

        while self.running:
            print("Running all time...")
            # consultar as ordem ativas junto com os operadores, buscar maquina, etc
            try:
                with psycopg.connect(DB_CONN_STR, row_factory=dict_row) as db:
                    with db.cursor() as cursor:
                        sql = f"""
                             SELECT
                                os.id as id,
                                os.maquina_id as maquina_id,
                                os.talhao_id as talhao_id,
                                oso.operador_id as operador_id,
                                os.status status,
                                u.nome as nome,
                                u.turno as turno,
                                u.empresa_id empresa_id,
                                u.grupo_id grupo_id,
                                os.data_previsao_fim data_previsao_fim
                            FROM ordem_servico os
                            INNER JOIN ordem_servico_operador oso ON (oso.ordem_servico_id = os.id)
                            INNER JOIN usuario u ON u.id = oso.operador_id
                            WHERE os.status in ('A', 'E')
                            AND u.tipo = 'O'
                            AND u.turno = '{self.get_turno()}'
                            AND os.data_inicio <= NOW()
                            AND u.nome LIKE '%-SML';
                        """
                        cursor.execute(sql)
                        result = cursor.fetchall()

                        ordens = []
                        for row in result:
                            ordens.append(row['id'])
                            if row['id'] not in self.ordens_ativas.copy():
                                operador = Operador(row['operador_id'], row['nome'], row['empresa_id'],
                                                    row['grupo_id'], row['turno'])

                                maquina = Maquina(row['maquina_id'])
                                talhao = Talhao(row['talhao_id'])
                                ordem = Ordem(row['id'], maquina, talhao, operador, row['status'], row['data_previsao_fim'])

                                simulador_eventos = Simulator(ordem)
                                simulador_eventos.start()
                                self.ordens_ativas[row['id']] = simulador_eventos

                        for _id, simulador in self.ordens_ativas.copy().items():
                            if _id not in ordens:
                                print(f"Removendo Ordem {_id} do simulador", flush=True)
                                simulador.runnig = False
                                del self.ordens_ativas[_id]

            except:
                print("Erro consulta ordem simulador", flush=True)

            for _id, ordem in self.ordens_ativas.copy().items():
                if not ordem.is_alive():
                    print(f"Removendo Ordem {_id} do simulador", flush=True)
                    del self.ordens_ativas[_id]

            time.sleep(60)

    def down(self, signumber=None, stackframe=None):
        print('Sinal de interrupção recebido. Encerrando threads...', flush=True)
        self.running = False
        for _id, ordem in self.ordens_ativas.items():
            print(f'Ordem de serviço [{_id}] encerrando...', flush=True)
            ordem.runnig = False

        os._exit(0)

    def get_turno(self):
        now = datetime.datetime.now()
        print(now)
        if 8 <= now.hour < 16:
            return 'M'
        elif 16 <= now.hour < 24:
            return 'T'
        else:
            return 'N'


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simulador de Evento Agro-control")
    parser.add_argument('--start', action="store_true", help="start")
    parsed_args = vars(parser.parse_args())

    if parsed_args['start'] is True:
        main = Main()
        main.start()
    else:
        print("Use: python3/python main.py --start", flush=True)
