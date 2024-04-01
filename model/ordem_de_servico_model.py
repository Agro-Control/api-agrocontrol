class OrdemServico:
    def __init__(self, id= None, data_inicio= None, status= None, data_fim=None,
                 velocidade_minima=None, velocidade_maxima=None, rpm=None,
                 gestor_id=None, talhao_id=None, unidade_id=None,empresa_id=None,
                 maquina_id=None, operadores_ids= []):
        self.id = id
        self.data_inicio = data_inicio
        self.status = status
        self.data_fim = data_fim
        self.velocidade_minima = velocidade_minima
        self.velocidade_maxima = velocidade_maxima
        self.rpm = rpm
        self.gestor_id = gestor_id
        self.talhao_id = talhao_id
        self.empresa_id = empresa_id
        self.unidade_id = unidade_id
        self.maquina_id = maquina_id
        self.operadores_ids = operadores_ids

    def dict(self):
        return {
            "id": self.id,
            "data_criacao": self.data_inicio if not self.data_inicio else self.data_inicio.isoformat(),
            "status": self.status,
            "data_fim": self.data_fim if not self.data_fim else self.data_fim.isoformat(),
            "velocidade_minima": self.velocidade_minima,
            "velocidade_maxima": self.velocidade_maxima,
            "rpm": self.rpm,
            "gestor_id": self.gestor_id,
            "talhao_id": self.talhao_id,
            "unidade_id": self.unidade_id,
            "empresa_id": self.empresa_id,
            "maquina_id": self.maquina_id,
            "operadores_ids": self.operadores_ids
        }
# Exemplo de uso:
#ordem_servico1 = OrdemServico(1, "2024-03-12", "Em andamento", velocidade_minima=10, velocidade_maxima=20, rpm=2000, gestor_id=1, talhao_id=1, unidade_id=1, maquina_id=1)
