from pydantic import BaseModel
from datetime import datetime

class Usuario(BaseModel):
    id: int | None = None
    nome: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    turno: str | None = None
    email: str | None = None
    matricula: str | None = None
    senha: str | None = None
    data_contratacao: datetime | None = None
    tipo: str | None = None
    status: str | None = None
    gestor_id: int | None = None
    empresa_id: int | None = None
    unidade_id: int | None = None
    grupo_id: int | None = None
    empresa: str | None = None
    unidade: str | None = None

