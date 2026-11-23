"""Cria a tabela tokens_redefinicao_senha (issue [1.2]).

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-23
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tokens_redefinicao_senha",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_tokens_redefinicao_senha_usuario_id", "tokens_redefinicao_senha", ["usuario_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_tokens_redefinicao_senha_usuario_id", "tokens_redefinicao_senha")
    op.drop_table("tokens_redefinicao_senha")
