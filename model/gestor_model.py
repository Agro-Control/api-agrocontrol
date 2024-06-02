from pydantic import BaseModel
from datetime import datetime

class Gestor(BaseModel):
    id: int | None = None
    nome: str | None = None
    email: str | None = None
    cpf:  str | None = None
    status:  str | None = None
    telefone:  str | None = None
    tipo: str | None = None
    data_contratacao:  datetime | None = None
    empresa_id: int | None = None
    empresa: str | None = None
