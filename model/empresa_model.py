from pydantic import BaseModel
from datetime import datetime

class Empresa(BaseModel):
    id: int | None = None
    nome: str | None = None
    cnpj:  str | None = None
    telefone: str | None = None
    cep:  str | None = None
    estado:  str | None = None
    cidade:  str | None = None
    bairro:  str | None = None
    logradouro:  str | None = None
    numero:  str | None = None
    complemento:  str | None = None
    status:  str | None = None
    data_criacao: datetime | None = None
    telefone_responsavel: str | None = None
    email_responsavel: str | None = None
    nome_responsavel: str | None = None
    gestor_id: int | None = None
    grupo_empresarial_id: int | None = None

# Exemplo de uso:
#empresa1 = Empresa(1, "Empresa A", "12345678901234", "987654321", "12345678", "SP", "São Paulo", "Centro", "Rua A", "123", "Apto 101", "Ativa", "999999999", "responsavel@email.com", "Responsável 1", 1)
