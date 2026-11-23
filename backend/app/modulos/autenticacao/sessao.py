# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Sessão do usuário: JWT de curta duração guardado em cookie.

- HttpOnly: o JavaScript da página não consegue ler o cookie (protege de XSS).
- Secure: o navegador só envia o cookie por HTTPS (localhost é exceção).
- SameSite=Lax: outro site não consegue disparar requisições com o cookie
  em formulários POST (protege de CSRF).
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response

from app.config import configuracoes


def criar_token(usuario_id: int) -> str:
    agora = datetime.now(UTC)
    conteudo = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=configuracoes.jwt_expira_minutos),
    }
    return jwt.encode(conteudo, configuracoes.jwt_segredo, algorithm=configuracoes.jwt_algoritmo)


def ler_token(token: str) -> dict | None:
    """Devolve o conteúdo do token, ou None se for inválido ou estiver vencido."""
    try:
        return jwt.decode(
            token,
            configuracoes.jwt_segredo,
            algorithms=[configuracoes.jwt_algoritmo],
            options={"require": ["sub", "iat", "exp"]},
        )
    except jwt.PyJWTError:
        return None


def gravar_cookie_sessao(resposta: Response, token: str) -> None:
    resposta.set_cookie(
        key=configuracoes.cookie_sessao_nome,
        value=token,
        max_age=configuracoes.jwt_expira_minutos * 60,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )


def apagar_cookie_sessao(resposta: Response) -> None:
    resposta.delete_cookie(
        key=configuracoes.cookie_sessao_nome, httponly=True, secure=True, samesite="lax", path="/"
    )
