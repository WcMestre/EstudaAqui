# PROVISÓRIO: substituir pela implementação da issue [0.2]
"""Formato padrão de erro da API: {"codigo": "...", "mensagem": "..."}.

`codigo` é estável e serve para o front decidir o que fazer;
`mensagem` é o texto em português para mostrar ao usuário.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

CODIGOS_POR_STATUS = {
    400: "requisicao_invalida",
    401: "nao_autenticado",
    403: "acesso_negado",
    404: "nao_encontrado",
    405: "metodo_nao_permitido",
    409: "conflito",
    422: "dados_invalidos",
}


class ErroAPI(Exception):
    """Erro de regra de negócio, lançado pelos serviços."""

    def __init__(self, status: int, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem


def _resposta(status: int, codigo: str, mensagem: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"codigo": codigo, "mensagem": mensagem})


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    @app.exception_handler(ErroAPI)
    async def _erro_api(_: Request, erro: ErroAPI) -> JSONResponse:
        return _resposta(erro.status, erro.codigo, erro.mensagem)

    @app.exception_handler(RequestValidationError)
    async def _erro_validacao(_: Request, erro: RequestValidationError) -> JSONResponse:
        primeiro = erro.errors()[0]
        campo = primeiro["loc"][-1]
        return _resposta(422, "dados_invalidos", f"Campo '{campo}' inválido: {primeiro['msg']}")

    @app.exception_handler(StarletteHTTPException)
    async def _erro_http(_: Request, erro: StarletteHTTPException) -> JSONResponse:
        codigo = CODIGOS_POR_STATUS.get(erro.status_code, "erro")
        return _resposta(erro.status_code, codigo, str(erro.detail))
