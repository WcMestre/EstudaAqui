# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Tabela `usuarios`, conforme a especificação da issue [1.1]."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.banco import ModeloBase


class Papel(StrEnum):
    ADMIN = "admin"
    PROFESSOR = "professor"
    ALUNO = "aluno"


class Usuario(ModeloBase):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("papel IN ('admin', 'professor', 'aluno')", name="papel_valido"),
    )

    nome: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[str] = mapped_column(String(20))

    # Adicionado pela issue [1.2] (recuperação de senha) e NÃO provisório:
    # momento da última troca de senha. Sessões (JWT) emitidas antes disso
    # são recusadas pelo usuario_atual. A combinar com a issue [1.1].
    senha_alterada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
