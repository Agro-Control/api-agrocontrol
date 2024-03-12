class Operador:
    def __init__(this, id, cpf, nome, turno, email, status, telefone, data):
        this.id = id
        this.cpf = cpf
        this.nome = nome
        this.turno = turno
        this.email = email
        this.status = status
        this.telefone = telefone
        this.data = data

operador1 = Operador(1, "12345678900", "Vinicius", "1", "Vinicius@email.com", "Ativo", "987654321", "2024-03-12")
