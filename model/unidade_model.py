from pydantic import BaseModel
from datetime import datetime

class Unidade(BaseModel):
    id: int | None = None
    nome: str | None = None
    cep:  str | None = None
    estado:  str | None = None
    cidade:  str | None = None
    bairro:  str | None = None
    logradouro:  str | None = None
    numero:  str | None = None
    complemento:  str | None = None
    status:  str | None = None
    data_criacao: datetime | None = None
    empresa_id:  int | None = None
    gestor_id: int | None = None


# Exemplo de uso:
#unidade1 = Unidade(1, "Unidade A", "12345678901234", "987654321", "12345678", "SP", "São Paulo", "Centro", "Rua A", "123", "Apto 101", "Ativa", 1, 1)
