from pydantic import BaseModel, Field
from datetime import datetime


class Evento(BaseModel):
    id: str | None = None
    nome: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    duracao: int | None = None
    ordem_servico_id: int | None = None
    maquina_id: int | None = None
    operador_id: int | None = None
    empresa_id: int | None = None
    grupo_id: int | None = None
