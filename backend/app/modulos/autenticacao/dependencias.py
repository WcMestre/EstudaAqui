# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Dependência `usuario_atual`: protege rotas que exigem login.

Uso numa rota:  usuario: Usuario = Depends(usuario_atual)
"""

from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.banco import obter_sessao
from app.config import configuracoes
from app.erros import ErroAPI
from app.modulos.autenticacao.sessao import ler_token
from app.modulos.usuarios.modelos import Usuario


def nao_autenticado() -> ErroAPI:
    return ErroAPI(401, "nao_autenticado", "Sua sessão expirou. Entre novamente.")


def usuario_atual(
    sessao: Annotated[Session, Depends(obter_sessao)],
    token: Annotated[str | None, Cookie(alias=configuracoes.cookie_sessao_nome)] = None,
) -> Usuario:
    conteudo = ler_token(token) if token else None
    if conteudo is None:
        raise nao_autenticado()

    usuario = sessao.get(Usuario, int(conteudo["sub"]))
    if usuario is None or not usuario.ativo:
        raise nao_autenticado()

    # Issue [1.2] (NÃO provisório; manter na implementação da [1.1]):
    # sessão aberta antes da última troca de senha não vale mais.
    if usuario.senha_alterada_em and conteudo["iat"] < usuario.senha_alterada_em.timestamp():
        raise nao_autenticado()
    return usuario
