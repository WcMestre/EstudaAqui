# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Formatos de entrada e saída das rotas de login."""

from pydantic import BaseModel, ConfigDict, EmailStr


class PedidoLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioLogado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    papel: str
