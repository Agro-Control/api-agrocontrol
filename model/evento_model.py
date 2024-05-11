from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

class Evento(BaseModel):
    _id: ObjectId | None = None
    nome: str | None = None
    descricao: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    duracao: int | None = None
    ordem_servico_id: int | None = None
    maquina_id: int | None
    operador_id: int | None