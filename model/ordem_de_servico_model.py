class OrdemServico:
    def __init__(this, id, data_criacao, status, data_fim, velocidade_min, velocidade_max, rpm, gestor_id, talhao_id, unidade_id, maquina_id):
        this.id = id
        this.data_criacao = data_criacao
        this.status = status
        this.data_fim = data_fim
        this.velocidade_min = velocidade_min
        this.velocidade_max = velocidade_max
        this.rpm = rpm
        this.gestor_id = gestor_id
        this.talhao_id = talhao_id
        this.unidade_id = unidade_id
        this.maquina_id = maquina_id

# Exemplo de uso:
ordem_servico1 = OrdemServico(1, "2024-03-12", "Em andamento", None, 10, 20, 2000, 1, 1, 1, 1)
