"""Adiciona tokens_redefinicao_senha.falha_envio_em (issue [1.2]).

Preenchida quando o e-mail com o link não pôde ser enviado. Links com
falha não contam no limite de 3 pedidos por hora.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-24
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tokens_redefinicao_senha",
        sa.Column("falha_envio_em", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tokens_redefinicao_senha", "falha_envio_em")
