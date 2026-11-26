"""Testes de segurança da recuperação de senha.

Cada teste comprova uma proteção contra um ataque específico, que não é
coberto diretamente pelos critérios de aceite.
"""

from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from tests.recuperacao_senha.auxiliares import (
    URL_ESQUECI_SENHA,
    URL_REDEFINIR_SENHA,
    parte_do_email,
    pedir_link,
    texto_do_email,
)


def test_nome_do_usuario_nao_vira_html_no_email(cliente, criar_usuario, caixa_de_saida):
    """Ataque: cadastrar um nome com HTML para injetar conteúdo no e-mail."""
    criar_usuario(email="aluno@example.com", nome='<a href="https://golpe.example">Clique</a>')

    pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    # Na versão HTML, o nome vira texto (as marcações são "escapadas").
    html = parte_do_email(caixa_de_saida[0], "html")
    assert '<a href="https://golpe.example">' not in html
    assert "&lt;a href=&#34;https://golpe.example&#34;&gt;" in html
    # Na versão de texto puro o nome aparece como digitado, e isso é seguro:
    # leitores de e-mail não interpretam HTML em texto puro.
    texto = parte_do_email(caixa_de_saida[0], "plain")
    assert '<a href="https://golpe.example">Clique</a>' in texto


def test_link_usa_o_endereco_configurado_e_ignora_o_host_do_pedido(
    cliente, criar_usuario, caixa_de_saida
):
    """Ataque: falsificar o cabeçalho Host para o link apontar ao site do atacante."""
    criar_usuario(email="aluno@example.com")

    cliente.post(
        URL_ESQUECI_SENHA,
        json={"email": "aluno@example.com"},
        headers={
            "Host": "site-do-atacante.example",
            "X-Forwarded-Host": "site-do-atacante.example",
        },
    )

    corpo = texto_do_email(caixa_de_saida[0])
    assert "site-do-atacante.example" not in corpo
    assert "http://localhost:3000/redefinir-senha?token=" in corpo


def test_mesmo_link_enviado_ao_mesmo_tempo_so_funciona_uma_vez(
    cliente, criar_usuario, caixa_de_saida
):
    """Ataque: disparar o mesmo link em paralelo para usá-lo mais de uma vez."""
    from app.main import app

    criar_usuario(email="aluno@example.com")
    token = pedir_link(cliente, caixa_de_saida, "aluno@example.com")

    def usar_link(senha: str) -> int:
        with TestClient(app, base_url="https://testserver") as outro_cliente:
            resposta = outro_cliente.post(
                URL_REDEFINIR_SENHA, json={"token": token, "nova_senha": senha}
            )
            return resposta.status_code

    with ThreadPoolExecutor(max_workers=5) as paralelo:
        resultados = list(paralelo.map(usar_link, [f"SenhaParalela{i}" for i in range(5)]))

    assert sorted(resultados) == [200, 400, 400, 400, 400]


RODADAS_DOIS_LINKS_EM_PARALELO = 20


def test_dois_links_da_mesma_conta_usados_ao_mesmo_tempo_so_um_funciona(
    cliente, criar_usuario, caixa_de_saida
):
    """Ataque: pedir dois links e usar os dois em paralelo para trocar a senha duas vezes.

    Um deve funcionar e o outro receber `link_ja_usado`; nunca erro 500 nem
    travamento. Repetido várias vezes porque a disputa depende do momento
    exato em que cada requisição chega ao banco.
    """
    from app.main import app

    def usar_link(token: str, senha: str) -> tuple[int, str | None]:
        # raise_server_exceptions=False: um erro interno vira resposta 500 em
        # vez de exceção, para o teste mostrar o que o usuário receberia.
        with TestClient(
            app, base_url="https://testserver", raise_server_exceptions=False
        ) as outro_cliente:
            resposta = outro_cliente.post(
                URL_REDEFINIR_SENHA, json={"token": token, "nova_senha": senha}
            )
            codigo = resposta.json().get("codigo") if resposta.status_code == 400 else None
            return resposta.status_code, codigo

    for rodada in range(RODADAS_DOIS_LINKS_EM_PARALELO):
        email = f"aluno{rodada}@example.com"
        criar_usuario(email=email)
        primeiro_link = pedir_link(cliente, caixa_de_saida, email)
        segundo_link = pedir_link(cliente, caixa_de_saida, email)

        with ThreadPoolExecutor(max_workers=2) as paralelo:
            tarefas = [
                paralelo.submit(usar_link, primeiro_link, "SenhaDoPrimeiro1"),
                paralelo.submit(usar_link, segundo_link, "SenhaDoSegundo2"),
            ]
            # O timeout transforma um travamento em falha, em vez de deixar o teste parado.
            resultados = sorted(tarefa.result(timeout=30) for tarefa in tarefas)

        assert resultados == [(200, None), (400, "link_ja_usado")], f"rodada {rodada}"
