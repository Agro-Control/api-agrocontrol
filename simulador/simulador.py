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
    host=localhost
    port=5432
"""


class Event:
    def __init__(self, name, min_duration=0, max_duration=0, probability=0):
        self.id = None
        self.name = name
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.duration = 0
        self.probability = probability
        self.set_new_duration()
        self.data_inicio = None
        self.data_fim = None

    def set_new_duration(self):
        self.duration = math.ceil(random.uniform(self.min_duration, self.max_duration))

    def set_data_inicio(self, data_inicio):
        self.data_inicio = data_inicio

    def set_data_fim(self,  data_fim):
        self.data_fim = data_fim


class Maquina:
    def __init__(self, id):
        self.id_ = id


class Ordem:
    def __init__(self, id, maquina, operador_ativo, status):
        self.id_ = id
        self.maquina = maquina
        self.operador = operador_ativo
        self.status = status


class Operador:
    def __init__(self, id, empresa_id, grupo_id, turno):
        self.id_ = id
        self.turno = turno
        self.fim_turno = self.get_fim_turno()
        self.empresa_id = empresa_id
        self.grupo_id = grupo_id

    def get_fim_turno(self):
        now = datetime.datetime.now()
        if self.turno == 'M':
            return datetime.datetime(now.year, now.month, now.day, 16, 0, 0)
        elif self.turno == 'T':
            return datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        else:
            return datetime.datetime(now.year, now.month, now.day, 8, 0, 0) + datetime.timedelta(days=1)


class EventSimulator(threading.Thread):
    def __init__(self, ordem):
        threading.Thread.__init__(self)
        self.runnig = True
        self.abastecido = False
        self.clima_event = random.choice([True, False])  # controle se vai ou não chover
        self.ordem = ordem

        self.events = {
            "automaticos": [
                Event("operacao", 5, 10, 0.7),
                Event("transbordo", 1, 5, 0.1),
                Event("deslocamento", 1, 5, 0.2),
            ],
            "manuais": [
                Event("aguardando_transbordo", 1, 2, 0.3),
                Event("manutencao", 1, 2, 0.2),
                Event("clima", 1, 2, 0.01),
                Event("abastecimento", 1, 2, 0.1),
                Event("troca_turno", 1, 2),
                Event("fim_ordem", probability=0.01)
            ]
        }

    def run(self):
        print(f"Iniciando o simulador da Ordem de serviço: {self.ordem.id_}, "
              f"OPERADOR: {self.ordem.operador.id_}, "
              f"TURNO: {self.ordem.operador.turno}, "
              f"MAQUINA: {self.ordem.maquina.id_}, "
              f"EMPRESA: {self.ordem.operador.empresa_id}, "
              f"GRUPO: {self.ordem.operador.grupo_id}", flush=True)

        if self.ordem.status == 'A':
            event = Event("inicio_ordem_servico")
            event.set_data_inicio(data_inicio=datetime.datetime.now())
            event.set_data_fim(data_fim=datetime.datetime.now())
            self.send_event(event)
            self.ordem.status = 'E'

        current_event, old_event = None, None

        while self.runnig:

            # gerar novo evento
            current_event = self.get_next_event(old_event)
            current_event.set_new_duration()
            current_event.set_data_inicio(data_inicio=datetime.datetime.now())

            if current_event.name in ["fim_ordem", "troca_turno"]:
                current_event.set_data_fim(data_fim=datetime.datetime.now())
                self.send_event(current_event)
                break

            if current_event.name == "clima":
                self.clima_event = False
            elif current_event.name == "abastecimento":
                self.abastecido = True

            # enviar esse novo evento gerado e recuperar o id dele
            current_event.id = self.send_event(current_event)

            if old_event and old_event.name != current_event.name:
                old_event.set_data_fim(data_fim=datetime.datetime.now())
                self.send_event(old_event, "PUT")

            old_event = current_event
            time.sleep(current_event.duration)

        print(f"Ordem [{self.ordem.id_}] simulador encerrado!", flush=True)

    def get_next_event(self, old_event):

        #  regras malditas para ter coerencia nos eventos

        if not old_event or old_event.name in ["manutencao", "abastecimento", "clima", "transbordo", "deslocamento"]:
            return [event for event in self.events["automaticos"] if event.name == "operacao"][0]

        if old_event.name == "aguardando_transbordo":
            return [event for event in self.events["automaticos"] if event.name == "transbordo"][0]

        if datetime.datetime.now() >= self.ordem.operador.fim_turno:
            return [event for event in self.events["manuais"] if event.name == "troca_turno"][0]

        if random.random() < 0.8:
            event_list = []
            for event in self.events["automaticos"]:
                if event.name == "transbordo" and old_event.name != "aguardando_transbordo":
                    continue

                if event.name == "operacao" and old_event.name == "operacao":
                    continue

                event_list.append(event)

        else:
            event_list = []
            for event in self.events["manuais"]:
                if event.name == "clima" and not self.clima_event:
                    continue

                if event.name == "abastecimento" and self.abastecido:
                    continue

                event_list.append(event)

        return random.choices(event_list, [event.probability for event in event_list])[0]

    def send_event(self, event, metodo='POST'):
        try:
            data = {
                "ordem_servico_id": self.ordem.id_,
                "operador_id": self.ordem.operador.id_,
                "maquina_id": self.ordem.maquina.id_,
                "empresa_id": self.ordem.operador.empresa_id,
                "grupo_id": self.ordem.operador.grupo_id,
                "nome": event.name,
                "data_inicio": event.data_inicio.isoformat(),
                "data_fim": event.data_fim.isoformat() if event.data_fim else None
            }

            if metodo == "PUT":
                data['id'] = event.id
                data['duracao'] = event.duration

            elif event.name in ["fim_ordem", "troca_turno"]:
                data['duracao'] = event.duration

            response = requests.request(metodo, 'http://localhost:5000/eventos', data=json.dumps(data))

            if response:
                response = response.json()
                print(f"Evento {'atualizado 'if metodo == 'PUT' else 'salvo '}[ID] {response['id']}: {data['nome']},"
                      f" [DURACAO] {event.duration} sec"
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


class Deamon:
    def __init__(self):
        self.runnig = False
        self.ordens_ativas = {}
        signal.signal(signal.SIGINT, self.down)
        signal.signal(signal.SIGTERM, self.down)

    def start(self):
        self.runnig = True
        time.sleep(5)  # sleep de segurança

        while self.runnig:
            print("Running all time...")
            # consultar as ordem ativas junto com os operadores, buscar maquina, etc
            try:
                with psycopg.connect(DB_CONN_STR, row_factory=dict_row) as db:
                    with db.cursor() as cursor:
                        sql = f"""
                             SELECT
                                os.id as id,
                                os.maquina_id as maquina_id,
                                oso.operador_id as operador_id,
                                os.status status,
                                u.turno as turno,
                                u.empresa_id empresa_id,
                                u.grupo_id grupo_id
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

                        for row in result:
                            if row['id'] not in self.ordens_ativas.copy():
                                operador = Operador(row['operador_id'],row['empresa_id'], row['grupo_id'], row['turno'])
                                maquina = Maquina(row['maquina_id'])
                                ordem = Ordem(row['id'], maquina, operador, row['status'])

                                simulador_eventos = EventSimulator(ordem)
                                simulador_eventos.start()
                                self.ordens_ativas[row['id']] = simulador_eventos
            except:
                print("Deu ruim", flush=True)

            for _id, ordem in self.ordens_ativas.copy().items():
                if not ordem.is_alive():
                    print(f"Removendo Ordem {_id} do simulador", flush=True)
                    del self.ordens_ativas[_id]

            time.sleep(60)

    def down(self, signumber=None, stackframe=None):
        print('Sinal de interrupção recebido. Encerrando threads...', flush=True)
        self.runnig = False
        for _id, ordem in self.ordens_ativas.items():
            print(f'Ordem de serviço [{_id}] encerrando...', flush=True)
            ordem.runnig = False
            # ordem.join()

        os._exit(0)

    def get_turno(self):
        now = datetime.datetime.now()
        if 8 <= now.hour < 16:
            return 'M'
        elif 16 >= now.hour < 24:
            return 'T'
        else:
            return 'N'


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simulador de Evento Agro-control")
    parser.add_argument('--start', action="store_true", help="start")
    parsed_args = vars(parser.parse_args())

    if parsed_args['start'] is True:
        deamon = Deamon()
        deamon.start()
    else:
        print("Use: python3/python main.py --start", flush=True)
