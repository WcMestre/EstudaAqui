"""Formatos de entrada e saída das rotas de recuperação de senha.

As validações levantam mensagens já em português (ver app/mensagens_validacao.py).
"""

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, field_validator

from app.mensagens_validacao import erro_em_portugues

TAMANHO_MINIMO_SENHA = 8
# Limite superior evita que alguém envie um texto enorme só para gastar CPU
# no cálculo do hash Argon2.
TAMANHO_MAXIMO_SENHA = 128


class PedidoEsqueciSenha(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def _email_valido(cls, valor: str) -> str:
        try:
            return validate_email(valor, check_deliverability=False).normalized
        except EmailNotValidError:
            raise erro_em_portugues("Informe um e-mail válido.") from None


class PedidoRedefinirSenha(BaseModel):
    token: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def _tamanho_da_senha(cls, valor: str) -> str:
        if len(valor) < TAMANHO_MINIMO_SENHA:
            raise erro_em_portugues(
                f"A nova senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
            )
        if len(valor) > TAMANHO_MAXIMO_SENHA:
            raise erro_em_portugues(
                f"A nova senha deve ter no máximo {TAMANHO_MAXIMO_SENHA} caracteres."
            )
        return valor


class RespostaMensagem(BaseModel):
    mensagem: str
