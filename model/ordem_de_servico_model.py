from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any
from model.operador_model import Operador
class OrdemServico(BaseModel):
    id: int | None = None
    data_criacao: datetime | None = None
    data_inicio: datetime | None = None
    data_previsao_fim: datetime | None = None
    data_fim: datetime | None = None
    status: str | None = None
    velocidade_minima: float | None = None
    velocidade_maxima: float | None = None
    rpm: int | None = None
    gestor_id: int | None = None
    talhao_id: int | None = None
    unidade_id: int | None = None
    empresa_id: int | None = None
    maquina_id: int | None = None
    nome_maquina: str | None = None
    operadores:  List[int | Operador | None ] | Dict | str = []

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        if hasattr(kwargs, "exclude_none"):
            _ignored = kwargs.pop("exclude_none")

        return super().dict(*args, exclude_none=True, **kwargs)
