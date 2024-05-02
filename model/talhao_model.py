from pydantic import BaseModel
from datetime import datetime

class Talhao(BaseModel):
    id: int | None = None
    codigo: str | None = None
    tamanho:  str | None = None
    status:  str | None = None
    unidade_id:  int | None = None

# Exemplo de uso:
#talhao1 = Talhao(1, "T001", 100, "Ativo", 1, 1)