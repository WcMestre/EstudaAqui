"""Prepara o banco usado pelo teste ponta a ponta (Playwright).

Cria o banco (se não existir), aplica as migrações, esvazia as tabelas e
cadastra os usuários recebidos em JSON:

    uv run python scripts/preparar_banco_e2e.py '[{"email": "...", "senha": "...", "nome": "..."}]'

Por segurança, só roda se o nome do banco em DATABASE_URL terminar com
"_e2e": assim nunca apaga o banco de desenvolvimento por engano.
"""

import json
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

PASTA_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_BACKEND))

from app.config import configuracoes  # noqa: E402


def main() -> None:
    url = make_url(configuracoes.database_url)
    if not (url.database or "").endswith("_e2e"):
        sys.exit(f"Recusado: o banco '{url.database}' não termina com '_e2e'.")

    servidor = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with servidor.connect() as conexao:
        existe = conexao.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"), {"nome": url.database}
        )
        if not existe:
            conexao.execute(text(f'CREATE DATABASE "{url.database}"'))
    servidor.dispose()

    command.upgrade(Config(str(PASTA_BACKEND / "alembic.ini")), "head")

    # Importados só depois das migrações, para usar a mesma configuração.
    from app.banco import SessaoLocal, engine
    from app.modulos.usuarios.modelos import Usuario
    from app.modulos.usuarios.seguranca import gerar_hash_senha

    with engine.begin() as conexao:
        conexao.execute(
            text("TRUNCATE tokens_redefinicao_senha, usuarios RESTART IDENTITY CASCADE")
        )

    usuarios = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
    with SessaoLocal() as sessao:
        for dados in usuarios:
            sessao.add(
                Usuario(
                    nome=dados["nome"],
                    email=dados["email"],
                    senha_hash=gerar_hash_senha(dados["senha"]),
                    papel="aluno",
                )
            )
        sessao.commit()
    print(f"Banco {url.database} pronto com {len(usuarios)} usuário(s).")


if __name__ == "__main__":
    main()
