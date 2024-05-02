from pydantic import BaseModel
from datetime import datetime

class Grupo(BaseModel):
    id: int | None = None
    nome: str | None = None
    data_criacao: datetime | None = None
    status: str | None = None
