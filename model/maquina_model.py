from pydantic import BaseModel
from datetime import datetime

class Maquina(BaseModel):
    id: int | None = None
    nome: str | None = None
    fabricante: str | None = None
    modelo: str | None = None
    status:  str | None = None
    capacidade_operacional:  int | None = None
    data_aquisicao:  datetime | None = None
    gestor_id: int | None = None
    empresa_id: int | None = None

#maquina1 = Maquina("Máquina A", "Fabricante A", "Modelo 1", "2024-01-01", "Ativa", "Alta", 1, 1, 1)
