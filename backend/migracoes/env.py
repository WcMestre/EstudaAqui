# PROVISÓRIO: substituir pela implementação da issue [0.2]
"""Configuração do Alembic: usa a mesma URL e os mesmos modelos da API."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

# Importar os modelos registra as tabelas no metadata (usado pelo autogenerate).
import app.modulos.recuperacao_senha.modelos
import app.modulos.usuarios.modelos  # noqa: F401
from app.banco import Base
from app.config import configuracoes

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def rodar_offline() -> None:
    """Gera o SQL sem conectar ao banco (alembic upgrade head --sql)."""
    context.configure(
        url=configuracoes.database_url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def rodar_online() -> None:
    engine = create_engine(configuracoes.database_url)
    with engine.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    rodar_offline()
else:
    rodar_online()
