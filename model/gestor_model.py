from pydantic import BaseModel
from datetime import datetime

class Gestor(BaseModel):
    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    telefone: str | None = None
    status:  str | None = None
    email:  str | None = None
    data_contratacao:  datetime | None = None
    gestor_id: int | None = None
    empresa_id: int | None = None


# Exemplo de uso:
#gestor1 = Gestor(1, "12345678900", "gestor1@email.com", "2024-01-01", "Ativo", "Gestor 1", "987654321")
#gestor2 = Gestor(2, "98765432100", "gestor2@email.com", "2024-02-01", "Ativo", "Gestor 2", "123456789")
