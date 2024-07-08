from datetime import datetime
from pydantic import BaseModel


class OrdemAlocacao(BaseModel):
    id: str | None = None
    operador_id: int | None = None
    data: datetime | None= None
    maquina_id: int | None = None
    ordem_id: int | None = None
    empresa_id: int | None = None
    grupo_id: int | None = None
