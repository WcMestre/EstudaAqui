"""Adiciona usuarios.senha_alterada_em (issue [1.2]).

Guarda o momento da última troca de senha. O usuario_atual recusa sessões
(JWT) emitidas antes dele. Coluna a combinar com a issue [1.1].

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios", sa.Column("senha_alterada_em", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("usuarios", "senha_alterada_em")
