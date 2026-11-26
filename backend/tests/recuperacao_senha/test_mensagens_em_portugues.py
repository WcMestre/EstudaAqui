"""Testes das mensagens de erro das rotas da recuperação de senha.

Toda resposta de erro de /esqueci-senha e /redefinir-senha deve vir no
formato padrão {"codigo", "mensagem"} e com a mensagem em português,
inclusive os erros de validação que o FastAPI/Pydantic geram sozinhos.
"""

import pytest

from tests.recuperacao_senha.auxiliares import URL_ESQUECI_SENHA, URL_REDEFINIR_SENHA


def erro_422(resposta) -> str:
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["codigo"] == "dados_invalidos"
    return corpo["mensagem"]


@pytest.mark.parametrize("email", ["isto-nao-e-email", "sem-dominio@", "@sem-usuario.com"])
def test_email_invalido_tem_mensagem_em_portugues(cliente, email):
    resposta = cliente.post(URL_ESQUECI_SENHA, json={"email": email})

    assert erro_422(resposta) == "Informe um e-mail válido."


def test_email_ausente_tem_mensagem_em_portugues(cliente):
    resposta = cliente.post(URL_ESQUECI_SENHA, json={})

    assert erro_422(resposta) == "O campo 'email' é obrigatório."


def test_email_que_nao_e_texto_tem_mensagem_em_portugues(cliente):
    resposta = cliente.post(URL_ESQUECI_SENHA, json={"email": 123})

    assert erro_422(resposta) == "O campo 'email' deve ser um texto."


def test_senha_curta_tem_mensagem_em_portugues(cliente):
    resposta = cliente.post(URL_REDEFINIR_SENHA, json={"token": "abc", "nova_senha": "1234567"})

    assert erro_422(resposta) == "A nova senha deve ter pelo menos 8 caracteres."


def test_senha_longa_demais_tem_mensagem_em_portugues(cliente):
    resposta = cliente.post(URL_REDEFINIR_SENHA, json={"token": "abc", "nova_senha": "a" * 129})

    assert erro_422(resposta) == "A nova senha deve ter no máximo 128 caracteres."


@pytest.mark.parametrize(
    ("corpo", "mensagem"),
    [
        ({"nova_senha": "12345678"}, "O campo 'token' é obrigatório."),
        ({"token": "abc"}, "O campo 'nova_senha' é obrigatório."),
    ],
)
def test_campos_ausentes_no_redefinir_tem_mensagem_em_portugues(cliente, corpo, mensagem):
    resposta = cliente.post(URL_REDEFINIR_SENHA, json=corpo)

    assert erro_422(resposta) == mensagem


@pytest.mark.parametrize("url", [URL_ESQUECI_SENHA, URL_REDEFINIR_SENHA])
def test_corpo_que_nao_e_json_tem_mensagem_em_portugues(cliente, url):
    resposta = cliente.post(
        url, content="isto não é json", headers={"Content-Type": "application/json"}
    )

    assert erro_422(resposta) == "O corpo da requisição não é um JSON válido."


@pytest.mark.parametrize("url", [URL_ESQUECI_SENHA, URL_REDEFINIR_SENHA])
def test_corpo_que_nao_e_objeto_tem_mensagem_em_portugues(cliente, url):
    resposta = cliente.post(url, json=["uma", "lista"])

    assert erro_422(resposta) == "O corpo da requisição deve ser um objeto JSON."


def test_erros_de_link_tem_mensagem_em_portugues(cliente):
    resposta = cliente.post(
        URL_REDEFINIR_SENHA, json={"token": "token-inexistente", "nova_senha": "12345678"}
    )

    assert resposta.json() == {
        "codigo": "link_invalido",
        "mensagem": "Este link de redefinição não é válido. Peça um novo link.",
    }
