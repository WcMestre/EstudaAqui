"""Funções de apoio usadas pelos testes da recuperação de senha."""

import re
from email.message import Message
from email.utils import parseaddr

URL_ESQUECI_SENHA = "/api/v1/auth/esqueci-senha"
URL_REDEFINIR_SENHA = "/api/v1/auth/redefinir-senha"
URL_LOGIN = "/api/v1/auth/login"
URL_EU = "/api/v1/auth/eu"


def destinatario(mensagem: Message) -> str:
    """Endereço do destinatário, sem o nome (ex.: 'Fulano <f@x.com>' -> 'f@x.com')."""
    return parseaddr(mensagem["To"])[1]


def texto_do_email(mensagem: Message) -> str:
    """Junta o texto de todas as partes do e-mail (texto puro e HTML)."""
    partes = []
    for parte in mensagem.walk():
        if parte.get_content_maintype() == "text":
            conteudo = parte.get_payload(decode=True)
            partes.append(conteudo.decode(parte.get_content_charset() or "utf-8"))
    return "\n".join(partes)


def extrair_token(mensagem: Message) -> str:
    """Tira do e-mail o token que vem no link de redefinição."""
    achado = re.search(r"/redefinir-senha\?token=([A-Za-z0-9_\-]+)", texto_do_email(mensagem))
    assert achado, "o e-mail não contém o link de redefinição"
    return achado.group(1)


def pedir_link(cliente, caixa_de_saida, email: str) -> str:
    """Pede a recuperação e devolve o token que chegou por e-mail."""
    enviados_antes = len(caixa_de_saida)
    resposta = cliente.post(URL_ESQUECI_SENHA, json={"email": email})
    assert resposta.status_code == 200
    assert len(caixa_de_saida) == enviados_antes + 1, "nenhum e-mail foi enviado"
    return extrair_token(caixa_de_saida[-1])


def entrar(cliente, email: str, senha: str):
    return cliente.post(URL_LOGIN, json={"email": email, "senha": senha})
