"""Regras da recuperação de senha (issue [1.2]).

Pedido do link (esqueci-senha):
- A rota responde na hora, sempre com a mesma mensagem, e todo o trabalho
  (procurar o usuário, gerar o token, enviar o e-mail) roda em segundo plano.
  Assim nem a resposta nem o tempo dela denunciam se o e-mail existe.
- Limite de 3 pedidos por hora por usuário: o excedente é ignorado em
  silêncio (sem e-mail, mas com a mesma resposta).

Troca da senha (redefinir-senha):
- O link vale 1 hora e serve uma única vez. Ao ser usado, os outros links
  pendentes do mesmo usuário são invalidados.
- A troca grava `senha_alterada_em`, o que derruba as sessões abertas antes.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.banco import SessaoLocal
from app.config import configuracoes
from app.erros import ErroAPI
from app.modulos.recuperacao_senha.email import enviar_email_redefinicao
from app.modulos.recuperacao_senha.modelos import TokenRedefinicaoSenha
from app.modulos.usuarios.modelos import Usuario
from app.modulos.usuarios.seguranca import gerar_hash_senha

VALIDADE_DO_LINK = timedelta(hours=1)
LIMITE_DE_PEDIDOS_POR_HORA = 3

MENSAGEM_PEDIDO_RECEBIDO = (
    "Se o e-mail estiver cadastrado, você receberá em instantes as instruções "
    "para redefinir a senha."
)
MENSAGEM_SENHA_REDEFINIDA = "Senha redefinida com sucesso. Entre com a nova senha."


def link_invalido() -> ErroAPI:
    return ErroAPI(
        400, "link_invalido", "Este link de redefinição não é válido. Peça um novo link."
    )


def link_ja_usado() -> ErroAPI:
    return ErroAPI(400, "link_ja_usado", "Este link já foi usado. Se precisar, peça um novo link.")


def link_expirado() -> ErroAPI:
    return ErroAPI(
        400, "link_expirado", "Este link expirou (ele vale por 1 hora). Peça um novo link."
    )


def calcular_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# --------------------------------------------------------------------------
# Pedido do link
# --------------------------------------------------------------------------


async def processar_pedido(email: str) -> None:
    """Tarefa de segundo plano disparada por POST /esqueci-senha."""
    dados = await run_in_threadpool(_registrar_pedido, email)
    if dados is not None:
        await enviar_email_redefinicao(**dados)


def _registrar_pedido(email: str) -> dict[str, str] | None:
    """Gera e grava o token. Devolve os dados do e-mail, ou None se não deve enviar."""
    with SessaoLocal() as sessao:
        # FOR UPDATE trava a linha do usuário: dois pedidos simultâneos não
        # conseguem furar o limite contando ao mesmo tempo.
        usuario = sessao.scalar(
            select(Usuario).where(func.lower(Usuario.email) == email.lower()).with_for_update()
        )
        if usuario is None or not usuario.ativo:
            return None
        if _pedidos_na_ultima_hora(sessao, usuario.id) >= LIMITE_DE_PEDIDOS_POR_HORA:
            return None

        token = secrets.token_urlsafe(32)  # 32 bytes aleatórios = 256 bits
        sessao.add(
            TokenRedefinicaoSenha(
                usuario_id=usuario.id,
                token_hash=calcular_hash(token),
                expira_em=datetime.now(UTC) + VALIDADE_DO_LINK,
            )
        )
        sessao.commit()
        return {
            "destinatario": usuario.email,
            "nome": usuario.nome,
            "link": f"{configuracoes.frontend_url}/redefinir-senha?token={token}",
        }


def _pedidos_na_ultima_hora(sessao: Session, usuario_id: int) -> int:
    return sessao.scalar(
        select(func.count())
        .select_from(TokenRedefinicaoSenha)
        .where(
            TokenRedefinicaoSenha.usuario_id == usuario_id,
            TokenRedefinicaoSenha.criado_em > func.now() - timedelta(hours=1),
        )
    )


# --------------------------------------------------------------------------
# Troca da senha
# --------------------------------------------------------------------------


def redefinir_senha(sessao: Session, token: str, nova_senha: str) -> None:
    token_hash = calcular_hash(token)

    # Ordem de travamento: SEMPRE a linha do usuário primeiro, depois a do link.
    # Requisições que mexem na mesma conta (o mesmo link repetido ou links
    # diferentes) fazem fila no usuário: a segunda espera a primeira terminar
    # e então vê o próprio link como usado ou invalidado. Travar o link
    # primeiro causava deadlock: cada requisição segurava o seu link e
    # esperava o link da outra (ao invalidá-lo) ou o usuário.
    usuario_id = sessao.scalar(
        select(TokenRedefinicaoSenha.usuario_id).where(
            TokenRedefinicaoSenha.token_hash == token_hash
        )
    )
    if usuario_id is None:
        raise link_invalido()
    sessao.scalar(select(Usuario).where(Usuario.id == usuario_id).with_for_update())

    # Lido de novo já com o usuário travado: enxerga o que a requisição
    # anterior gravou (populate_existing descarta o que estiver em memória).
    registro = sessao.scalar(
        select(TokenRedefinicaoSenha)
        .where(TokenRedefinicaoSenha.token_hash == token_hash)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if registro is None or not registro.usuario.ativo:
        raise link_invalido()
    if registro.usado_em is not None or not registro.ativo:
        raise link_ja_usado()

    agora = datetime.now(UTC)
    if registro.expira_em <= agora:
        raise link_expirado()

    usuario = registro.usuario
    usuario.senha_hash = gerar_hash_senha(nova_senha)
    usuario.senha_alterada_em = agora
    registro.usado_em = agora
    sessao.execute(
        update(TokenRedefinicaoSenha)
        .where(
            TokenRedefinicaoSenha.usuario_id == usuario.id,
            TokenRedefinicaoSenha.id != registro.id,
            TokenRedefinicaoSenha.usado_em.is_(None),
            TokenRedefinicaoSenha.ativo.is_(True),
        )
        .values(ativo=False)
    )
    sessao.commit()
