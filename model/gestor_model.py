class Gestor:
    def __init__(this, id, cpf, email, data_contratacao, status, nome, telefone, gestor_id=None):
        this.id = id
        this.cpf = cpf
        this.email = email
        this.data_contratacao = data_contratacao
        this.status = status
        this.nome = nome
        this.telefone = telefone
        this.gestor_id = gestor_id

    def gestor_gestor(this, gestor_superior_id):
        this.gestor_id = gestor_superior_id

# Exemplo de uso:
gestor1 = Gestor(1, "12345678900", "gestor1@email.com", "2024-01-01", "Ativo", "Gestor 1", "987654321")
gestor2 = Gestor(2, "98765432100", "gestor2@email.com", "2024-02-01", "Ativo", "Gestor 2", "123456789")

# Definindo gestor superior para gestor2 (gestor1 neste caso)
gestor2.gestor_gestor(gestor1.id)

