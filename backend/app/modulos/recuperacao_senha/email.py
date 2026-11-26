"""Envio do e-mail de redefinição (fastapi-mail + templates Jinja2).

Em desenvolvimento o SMTP é o Mailpit (http://localhost:8025 mostra os
e-mails). Nos testes, EMAIL_SUPRIMIR_ENVIO=true faz a mensagem ser montada
e registrada, mas não enviada.
"""

import logging
from pathlib import Path

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    MultipartSubtypeEnum,
)

from app.config import configuracoes

PASTA_TEMPLATES = Path(__file__).parent / "templates"

log = logging.getLogger(__name__)

cliente_email = FastMail(
    ConnectionConfig(
        MAIL_SERVER=configuracoes.smtp_host,
        MAIL_PORT=configuracoes.smtp_porta,
        MAIL_USERNAME=configuracoes.smtp_usuario,
        MAIL_PASSWORD=configuracoes.smtp_senha,
        MAIL_STARTTLS=configuracoes.smtp_starttls,
        MAIL_SSL_TLS=configuracoes.smtp_ssl,
        USE_CREDENTIALS=bool(configuracoes.smtp_usuario),
        MAIL_FROM=configuracoes.email_remetente,
        MAIL_FROM_NAME=configuracoes.email_remetente_nome,
        SUPPRESS_SEND=int(configuracoes.email_suprimir_envio),
        TEMPLATE_FOLDER=PASTA_TEMPLATES,
    )
)


async def enviar_email_redefinicao(destinatario: str, nome: str, link: str) -> bool:
    """Envia o e-mail com versão HTML e versão em texto puro.

    Devolve True se o servidor SMTP aceitou a mensagem. Falhas são registradas
    no log (sem o link, que é secreto) e não sobem: isto roda em segundo
    plano, depois que a resposta já foi enviada.
    """
    mensagem = MessageSchema(
        subject="Redefinição de senha - EstudaAqui",
        recipients=[destinatario],
        template_body={"nome": nome, "link": link, "validade": "1 hora"},
        subtype=MessageType.html,
        multipart_subtype=MultipartSubtypeEnum.alternative,
    )
    try:
        await cliente_email.send_message(
            mensagem,
            html_template="redefinir_senha.html",
            plain_template="redefinir_senha.txt",
        )
    except Exception:
        log.exception("Falha ao enviar o e-mail de redefinição de senha")
        return False
    return True
