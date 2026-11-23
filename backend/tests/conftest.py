"""Configuração compartilhada pelos testes do back-end.

Os testes rodam contra um banco PostgreSQL de testes separado (nunca o de
desenvolvimento). Antes de começar, o banco é criado (se ainda não existir) e
recebe todas as migrações do Alembic. Antes de cada teste as tabelas são
esvaziadas, para que um teste nunca dependa do que outro deixou para trás.
"""

import os
from pathlib import Path

# As variáveis precisam estar definidas ANTES de importar a aplicação, porque
# a configuração é lida uma única vez, na importação.
URL_BANCO_TESTE = os.environ.get(
    "DATABASE_URL_TESTE",
    "postgresql+psycopg://estudaaqui:estudaaqui@localhost:5432/estudaaqui_teste",
)
os.environ["DATABASE_URL"] = URL_BANCO_TESTE
os.environ.setdefault("JWT_SEGREDO", "segredo-usado-somente-nos-testes")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
# Nos testes nenhum e-mail sai de verdade: as mensagens são capturadas na memória.
os.environ["EMAIL_SUPRIMIR_ENVIO"] = "true"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

PASTA_BACKEND = Path(__file__).resolve().parents[1]


def _criar_banco_se_nao_existir(url: str) -> None:
    url_banco = make_url(url)
    servidor = create_engine(url_banco.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with servidor.connect() as conexao:
        existe = conexao.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"),
            {"nome": url_banco.database},
        )
        if not existe:
            conexao.execute(text(f'CREATE DATABASE "{url_banco.database}"'))
    servidor.dispose()


@pytest.fixture(scope="session", autouse=True)
def banco_de_testes():
    """Cria o banco de testes e aplica as migrações uma vez por execução."""
    from alembic import command
    from alembic.config import Config

    _criar_banco_se_nao_existir(URL_BANCO_TESTE)
    command.upgrade(Config(str(PASTA_BACKEND / "alembic.ini")), "head")
    yield


@pytest.fixture(autouse=True)
def tabelas_vazias(banco_de_testes):
    """Começa cada teste com as tabelas vazias."""
    from app.banco import engine

    with engine.begin() as conexao:
        conexao.execute(
            text("TRUNCATE tokens_redefinicao_senha, usuarios RESTART IDENTITY CASCADE")
        )
    yield


@pytest.fixture
def cliente():
    """Cliente HTTP que conversa com a API sem subir servidor.

    Usa https porque o cookie de sessão é Secure: em http o navegador (e o
    cliente de testes) não o enviaria de volta.
    """
    from app.main import app

    with TestClient(app, base_url="https://testserver") as cliente_http:
        yield cliente_http


@pytest.fixture
def sql():
    """Executa SQL direto no banco, para preparar ou conferir situações."""
    from app.banco import engine

    def _executar(comando: str, **parametros):
        with engine.begin() as conexao:
            resultado = conexao.execute(text(comando), parametros)
            return resultado.all() if resultado.returns_rows else []

    return _executar


@pytest.fixture
def criar_usuario():
    """Fábrica de usuários já gravados no banco, com a senha em hash Argon2."""
    from app.banco import SessaoLocal
    from app.modulos.usuarios.modelos import Usuario
    from app.modulos.usuarios.seguranca import gerar_hash_senha

    def _criar(
        email: str = "aluno@example.com",
        senha: str = "SenhaAntiga123",
        nome: str = "Aluno de Teste",
        papel: str = "aluno",
        ativo: bool = True,
    ):
        with SessaoLocal() as sessao:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha_hash=gerar_hash_senha(senha),
                papel=papel,
                ativo=ativo,
            )
            sessao.add(usuario)
            sessao.commit()
            sessao.refresh(usuario)
            return usuario

    return _criar


@pytest.fixture
def caixa_de_saida():
    """Lista com os e-mails que a aplicação 'enviou' durante o teste."""
    from app.modulos.recuperacao_senha.email import cliente_email

    with cliente_email.record_messages() as mensagens:
        yield mensagens
