from pydantic import BaseModel
from datetime import datetime

class Operador(BaseModel):
    id: int | None = None
    nome: str | None = None
    matricula: str | None = None
    cpf:  str | None = None
    status:  str | None = None
    turno:  str | None = None
    telefone:  str | None = None
    data_contratacao:  datetime | None = None
    gestor_id: int | None = None
    unidade_id: int | None = None

#operador1 = Operador(1, "12345678900", "Vinicius", "1", "Vinicius@email.com", "Ativo", "987654321", "2024-03-12")