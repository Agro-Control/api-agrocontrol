class Empresa:
    def __init__(this, id, nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro, numero, complemento, status, telefone_responsavel, email_responsavel, nome_responsavel, gestor_id):
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
        this.telefone_responsavel = telefone_responsavel
        this.email_responsavel = email_responsavel
        this.nome_responsavel = nome_responsavel
        this.gestor_id = gestor_id

# Exemplo de uso:
empresa1 = Empresa(1, "Empresa A", "12345678901234", "987654321", "12345678", "SP", "São Paulo", "Centro", "Rua A", "123", "Apto 101", "Ativa", "999999999", "responsavel@email.com", "Responsável 1", 1)
