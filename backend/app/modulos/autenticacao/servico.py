# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Regras do login. Sem limite de tentativas: isso é entrega da issue [1.1]."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.erros import ErroAPI
from app.modulos.usuarios.modelos import Usuario
from app.modulos.usuarios.seguranca import HASH_FICTICIO, verificar_senha


def credenciais_invalidas() -> ErroAPI:
    return ErroAPI(401, "credenciais_invalidas", "E-mail ou senha incorretos.")


def autenticar(sessao: Session, email: str, senha: str) -> Usuario:
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == email))
    # Verifica a senha mesmo sem usuário, para o tempo de resposta ser igual.
    senha_ok = verificar_senha(senha, usuario.senha_hash if usuario else HASH_FICTICIO)
    if usuario is None or not senha_ok or not usuario.ativo:
        raise credenciais_invalidas()
    return usuario
