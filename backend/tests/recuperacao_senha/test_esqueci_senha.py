"""Testes do pedido de recuperação: POST /api/v1/auth/esqueci-senha.

Critérios de aceite cobertos (issue #6):
- O usuário informa o e-mail e recebe uma mensagem de que, se o e-mail
  existir, as instruções foram enviadas (mesma mensagem para inexistentes).
- O e-mail contém um link com validade limitada (1 hora).
- Requisitos técnicos: guardar só o hash do token; 3 pedidos por hora por e-mail.
"""

import hashlib

from tests.recuperacao_senha.auxiliares import (
    URL_ESQUECI_SENHA,
    destinatario,
    extrair_token,
    pedir_link,
    texto_do_email,
)


def test_email_cadastrado_recebe_mensagem_generica_e_um_email(
    cliente, criar_usuario, caixa_de_saida
):
    criar_usuario(email="aluno@example.com")

    resposta = cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"]
    assert len(caixa_de_saida) == 1
    assert destinatario(caixa_de_saida[0]) == "aluno@example.com"


def test_mesma_mensagem_para_email_inexistente(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")

    existente = cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})
    inexistente = cliente.post(URL_ESQUECI_SENHA, json={"email": "ninguem@example.com"})

    assert inexistente.status_code == existente.status_code == 200
    assert inexistente.json() == existente.json()
    assert len(caixa_de_saida) == 1, "e-mail inexistente não deve receber nada"


def test_mesma_mensagem_e_nenhum_email_para_usuario_inativo(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="ativo@example.com")
    criar_usuario(email="inativo@example.com", ativo=False)

    ativo = cliente.post(URL_ESQUECI_SENHA, json={"email": "ativo@example.com"})
    inativo = cliente.post(URL_ESQUECI_SENHA, json={"email": "inativo@example.com"})

    assert inativo.status_code == 200
    assert inativo.json() == ativo.json()
    assert [destinatario(m) for m in caixa_de_saida] == ["ativo@example.com"]


def test_email_com_formato_invalido_retorna_erro_no_formato_padrao(cliente):
    resposta = cliente.post(URL_ESQUECI_SENHA, json={"email": "isto-nao-e-email"})

    assert resposta.status_code == 422
    corpo = resposta.json()
    assert set(corpo) == {"codigo", "mensagem"}


def test_link_do_email_aponta_para_a_tela_de_redefinicao(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")

    cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})

    corpo = texto_do_email(caixa_de_saida[0])
    assert "http://localhost:3000/redefinir-senha?token=" in corpo
    assert extrair_token(caixa_de_saida[0])


def test_email_informa_que_o_link_vale_por_uma_hora(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")

    cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})

    assert "1 hora" in texto_do_email(caixa_de_saida[0])


def test_token_fica_guardado_apenas_como_hash_sha256(cliente, criar_usuario, caixa_de_saida, sql):
    criar_usuario(email="aluno@example.com")

    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    hashes = [linha.token_hash for linha in sql("SELECT token_hash FROM tokens_redefinicao_senha")]
    assert hashes == [hashlib.sha256(token.encode()).hexdigest()]
    assert token not in hashes


def test_token_expira_em_uma_hora(cliente, criar_usuario, caixa_de_saida, sql):
    criar_usuario(email="aluno@example.com")

    pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    [(segundos_restantes,)] = sql(
        "SELECT EXTRACT(EPOCH FROM expira_em - now()) FROM tokens_redefinicao_senha"
    )
    assert 3500 < segundos_restantes <= 3600


def test_limite_de_tres_pedidos_por_hora_e_silencioso(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="aluno@example.com")

    respostas = [
        cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"}) for _ in range(4)
    ]

    assert all(r.status_code == 200 for r in respostas)
    assert all(r.json() == respostas[0].json() for r in respostas), (
        "o quarto pedido não pode ter resposta diferente (denunciaria o e-mail)"
    )
    assert len(caixa_de_saida) == 3


def test_limite_e_contado_separadamente_para_cada_email(cliente, criar_usuario, caixa_de_saida):
    criar_usuario(email="primeiro@example.com")
    criar_usuario(email="segundo@example.com")

    for _ in range(3):
        cliente.post(URL_ESQUECI_SENHA, json={"email": "primeiro@example.com"})
    cliente.post(URL_ESQUECI_SENHA, json={"email": "segundo@example.com"})

    assert destinatario(caixa_de_saida[-1]) == "segundo@example.com"
    assert len(caixa_de_saida) == 4


def test_pedidos_com_mais_de_uma_hora_nao_contam_para_o_limite(
    cliente, criar_usuario, caixa_de_saida, sql
):
    criar_usuario(email="aluno@example.com")
    for _ in range(3):
        cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})
    sql("UPDATE tokens_redefinicao_senha SET criado_em = now() - interval '61 minutes'")

    cliente.post(URL_ESQUECI_SENHA, json={"email": "aluno@example.com"})

    assert len(caixa_de_saida) == 4
