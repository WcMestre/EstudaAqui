"""Testes da troca de senha pelo link: POST /api/v1/auth/redefinir-senha.

Critérios de aceite cobertos (issue #6):
- Pelo link o usuário define uma nova senha e consegue entrar com ela.
- O link é de uso único e tem validade limitada.
- Link expirado ou já usado é recusado com mensagem clara.
- Requisitos técnicos: senha com 8+ caracteres; redefinir invalida sessões anteriores.
"""

from tests.recuperacao_senha.auxiliares import (
    URL_EU,
    URL_REDEFINIR_SENHA,
    entrar,
    pedir_link,
)

NOVA_SENHA = "SenhaNova456"


def redefinir(cliente, token: str, nova_senha: str = NOVA_SENHA):
    return cliente.post(URL_REDEFINIR_SENHA, json={"token": token, "nova_senha": nova_senha})


def test_redefinir_com_link_valido_permite_entrar_com_a_nova_senha(
    cliente, criar_usuario, caixa_de_saida
):
    criar_usuario(email="aluno@example.com")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    resposta = redefinir(cliente, token)

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"]
    assert entrar(cliente, "aluno@example.com", NOVA_SENHA).status_code == 200
    eu = cliente.get(URL_EU)
    assert eu.status_code == 200, "a sessão criada logo após redefinir deve valer"
    assert eu.json()["email"] == "aluno@example.com"


def test_senha_antiga_deixa_de_funcionar_apos_redefinir(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com", senha="SenhaAntiga123")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    redefinir(cliente, token)

    assert entrar(cliente, "aluno@example.com", "SenhaAntiga123").status_code == 401


def test_link_ja_usado_e_recusado_com_mensagem_clara(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")
    redefinir(cliente, token)

    segunda_vez = redefinir(cliente, token, "OutraSenha789")

    assert segunda_vez.status_code == 400
    assert segunda_vez.json()["codigo"] == "link_ja_usado"
    assert segunda_vez.json()["mensagem"]
    assert entrar(cliente, "aluno@example.com", "OutraSenha789").status_code == 401


def test_link_expirado_e_recusado_com_mensagem_clara(cliente, criar_usuario, caixa_de_saida, sql):
    criar_usuario(email="aluno@example.com", senha="SenhaAntiga123")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")
    sql("UPDATE tokens_redefinicao_senha SET expira_em = now() - interval '1 second'")

    resposta = redefinir(cliente, token)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "link_expirado"
    assert resposta.json()["mensagem"]
    assert entrar(cliente, "aluno@example.com", "SenhaAntiga123").status_code == 200


def test_link_inexistente_e_recusado(cliente):
    resposta = redefinir(cliente, "token-que-nunca-foi-gerado")

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "link_invalido"
    assert resposta.json()["mensagem"]


def test_usar_um_link_invalida_os_outros_links_pendentes(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")
    primeiro = pedir_link(cliente, caixa_de_saida, "aluno@example.com")
    segundo = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    assert redefinir(cliente, segundo).status_code == 200
    resposta = redefinir(cliente, primeiro, "OutraSenha789")

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "link_ja_usado"


def test_senha_com_menos_de_8_caracteres_e_recusada_sem_gastar_o_link(
    cliente, criar_usuario, caixa_de_saida
):
    criar_usuario(email="aluno@example.com")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    curta = redefinir(cliente, token, "1234567")

    assert curta.status_code == 422
    assert set(curta.json()) == {"codigo", "mensagem"}
    assert redefinir(cliente, token, "12345678").status_code == 200, (
        "o link deve continuar valendo depois de uma senha recusada"
    )


def test_redefinir_encerra_as_sessoes_abertas_antes(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com", senha="SenhaAntiga123")
    assert entrar(cliente, "aluno@example.com", "SenhaAntiga123").status_code == 200
    assert cliente.get(URL_EU).status_code == 200
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    redefinir(cliente, token)

    # O cliente ainda guarda o cookie da sessão antiga, mas ele não vale mais.
    assert cliente.get(URL_EU).status_code == 401


def test_usuario_inativado_depois_do_pedido_nao_consegue_redefinir(
    cliente, criar_usuario, caixa_de_saida, sql
):
    criar_usuario(email="aluno@example.com")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")
    sql("UPDATE usuarios SET ativo = false WHERE email = 'aluno@example.com'")

    resposta = redefinir(cliente, token)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "link_invalido"
