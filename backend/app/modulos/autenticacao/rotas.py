# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Rotas de login, logout e "quem sou eu"."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.banco import obter_sessao
from app.modulos.autenticacao.dependencias import usuario_atual
from app.modulos.autenticacao.schemas import PedidoLogin, UsuarioLogado
from app.modulos.autenticacao.servico import autenticar
from app.modulos.autenticacao.sessao import apagar_cookie_sessao, criar_token, gravar_cookie_sessao
from app.modulos.usuarios.modelos import Usuario

roteador = APIRouter(prefix="/api/v1/auth", tags=["autenticação"])


@roteador.post("/login", response_model=UsuarioLogado)
def login(
    pedido: PedidoLogin,
    resposta: Response,
    sessao: Annotated[Session, Depends(obter_sessao)],
) -> Usuario:
    usuario = autenticar(sessao, pedido.email, pedido.senha)
    gravar_cookie_sessao(resposta, criar_token(usuario.id))
    return usuario


@roteador.post("/logout", status_code=204)
def logout(resposta: Response) -> None:
    apagar_cookie_sessao(resposta)


@roteador.get("/eu", response_model=UsuarioLogado)
def eu(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Usuario:
    return usuario
