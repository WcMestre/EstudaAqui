"""Tabela `tokens_redefinicao_senha`: um registro por link enviado.

O token em si vai só no e-mail; aqui fica apenas o hash SHA-256 dele.
Situações de um registro:
- pendente:     usado_em vazio, ativo = true e expira_em no futuro;
- usado:        usado_em preenchido (o link que de fato trocou a senha);
- invalidado:   ativo = false (outro link do mesmo usuário foi usado antes);
- expirado:     expira_em no passado.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.banco import ModeloBase
from app.modulos.usuarios.modelos import Usuario


class TokenRedefinicaoSenha(ModeloBase):
    __tablename__ = "tokens_redefinicao_senha"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    usado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    usuario: Mapped[Usuario] = relationship()
