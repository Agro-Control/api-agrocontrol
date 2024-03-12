class Unidade:
    def __init__(this, id, nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro, numero, complemento, status, empresa_id, gestor_id):
        this.id = id
        this.nome = nome
        this.cnpj = cnpj
        this.telefone = telefone
        this.cep = cep
        this.estado = estado
        this.cidade = cidade
        this.bairro = bairro
        this.logradouro = logradouro
        this.numero = numero
        this.complemento = complemento
        this.status = status
        this.empresa_id = empresa_id
        this.gestor_id = gestor_id

# Exemplo de uso:
unidade1 = Unidade(1, "Unidade A", "12345678901234", "987654321", "12345678", "SP", "São Paulo", "Centro", "Rua A", "123", "Apto 101", "Ativa", 1, 1)
