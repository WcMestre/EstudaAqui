"""Mensagens de validação em português.

O Pydantic gera as mensagens de validação em inglês ("Field required",
"value is not a valid email address"...). Este módulo as converte para
português antes de chegarem ao usuário.

Há dois caminhos:
1. Validações nossas (ex.: "senha com 8+ caracteres") levantam
   `erro_em_portugues(...)`, e a mensagem é usada como está.
2. Erros genéricos do Pydantic/FastAPI (campo ausente, tipo errado, JSON
   quebrado) são traduzidos pelo tipo do erro em `traduzir_erro`.

Atenção: este arquivo NÃO é provisório. Ao substituir app/erros.py pela
implementação da issue [0.2], manter a chamada a `traduzir_erro`.
"""

from typing import Any

from pydantic_core import PydanticCustomError

TIPO_MENSAGEM_PRONTA = "mensagem_em_portugues"


def erro_em_portugues(mensagem: str) -> PydanticCustomError:
    """Erro de validação cuja mensagem já está pronta para o usuário."""
    return PydanticCustomError(TIPO_MENSAGEM_PRONTA, mensagem)


def traduzir_erro(erro: dict[str, Any]) -> str:
    """Recebe um item de `RequestValidationError.errors()` e devolve a mensagem."""
    tipo = erro["type"]
    if tipo == TIPO_MENSAGEM_PRONTA:
        return erro["msg"]
    if tipo == "json_invalid":
        return "O corpo da requisição não é um JSON válido."

    # loc é o "endereço" do erro: ("body",) é o corpo inteiro;
    # ("body", "email") é o campo email.
    local = erro.get("loc", ())
    if len(local) < 2:
        if tipo == "missing":
            return "O corpo da requisição é obrigatório."
        return "O corpo da requisição deve ser um objeto JSON."

    campo = local[-1]
    if tipo == "missing":
        return f"O campo '{campo}' é obrigatório."
    if tipo == "string_type":
        return f"O campo '{campo}' deve ser um texto."
    return f"O campo '{campo}' tem um valor inválido."
