class Maquina:
    def __init__(this, nome, fabricante, modelo, data_aquisicao, status, capacidade_operacional, id, gestor_id, unidade_id):
        this.nome = nome
        this.fabricante = fabricante
        this.modelo = modelo
        this.data_aquisicao = data_aquisicao
        this.status = status
        this.capacidade_operacional = capacidade_operacional
        this.id = id
        this.gestor_id = gestor_id
        this.unidade_id = unidade_id

# Exemplo de uso:
maquina1 = Maquina("Máquina A", "Fabricante A", "Modelo 1", "2024-01-01", "Ativa", "Alta", 1, 1, 1)
