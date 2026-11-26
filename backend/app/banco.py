# PROVISÓRIO: substituir pela implementação da issue [0.2]
"""Conexão com o PostgreSQL e base comum de todas as tabelas."""

from collections.abc import Iterator
from datetime import datetime

from sqlalchemy import DateTime, create_engine, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import configuracoes

engine = create_engine(configuracoes.database_url, pool_pre_ping=True)
SessaoLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ModeloBase(Base):
    """Colunas que toda tabela do projeto tem (convenção da issue [0.2]).

    `ativo` é a exclusão lógica: em vez de apagar, marcamos como inativo.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    ativo: Mapped[bool] = mapped_column(default=True, server_default=text("true"))


def obter_sessao() -> Iterator[Session]:
    """Dependência do FastAPI: abre uma sessão por requisição e fecha no fim."""
    with SessaoLocal() as sessao:
        yield sessao
