class Talhao:
    def __init__(this, id, codigo, tamanho, status, gestor_id, unidade_id):
        this.id = id
        this.codigo = codigo
        this.tamanho = tamanho
        this.status = status
        this.gestor_id = gestor_id
        this.unidade_id = unidade_id

# Exemplo de uso:
talhao1 = Talhao(1, "T001", 100, "Ativo", 1, 1)
