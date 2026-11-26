"""Rotas da recuperação de senha (issue [1.2]).

Ficam num módulo próprio, separado do login (issue [1.1]), para que as duas
entregas possam evoluir sem conflito.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.banco import obter_sessao
from app.modulos.recuperacao_senha.schemas import (
    PedidoEsqueciSenha,
    PedidoRedefinirSenha,
    RespostaMensagem,
)
from app.modulos.recuperacao_senha.servico import (
    MENSAGEM_PEDIDO_RECEBIDO,
    MENSAGEM_SENHA_REDEFINIDA,
    processar_pedido,
    redefinir_senha,
)

roteador = APIRouter(prefix="/api/v1/auth", tags=["recuperação de senha"])

ERRO_PADRAO = {"description": "Erro no formato {codigo, mensagem}"}


@roteador.post(
    "/esqueci-senha",
    response_model=RespostaMensagem,
    summary="Pedir o link de redefinição de senha",
    responses={422: ERRO_PADRAO},
)
def esqueci_senha(pedido: PedidoEsqueciSenha, tarefas: BackgroundTasks) -> RespostaMensagem:
    """Sempre responde 200 com a mesma mensagem, exista o e-mail ou não."""
    tarefas.add_task(processar_pedido, pedido.email)
    return RespostaMensagem(mensagem=MENSAGEM_PEDIDO_RECEBIDO)


@roteador.post(
    "/redefinir-senha",
    response_model=RespostaMensagem,
    summary="Definir a nova senha usando o link recebido",
    responses={400: ERRO_PADRAO, 422: ERRO_PADRAO},
)
def redefinir(
    pedido: PedidoRedefinirSenha, sessao: Annotated[Session, Depends(obter_sessao)]
) -> RespostaMensagem:
    redefinir_senha(sessao, pedido.token, pedido.nova_senha)
    return RespostaMensagem(mensagem=MENSAGEM_SENHA_REDEFINIDA)
