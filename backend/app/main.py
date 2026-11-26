# PROVISÓRIO: substituir pela implementação da issue [0.2]
"""Ponto de entrada da API. Rodar com: uv run uvicorn app.main:app --reload"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import configuracoes
from app.erros import registrar_tratadores_de_erro
from app.modulos.autenticacao.rotas import roteador as rotas_autenticacao
from app.modulos.recuperacao_senha.rotas import roteador as rotas_recuperacao_senha

app = FastAPI(title="EstudaAqui API", version="0.1.0")

# O front roda em outro endereço (porta 3000); sem isto o navegador bloqueia
# as chamadas. allow_credentials permite enviar o cookie de sessão.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracoes.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_tratadores_de_erro(app)
app.include_router(rotas_autenticacao)
app.include_router(rotas_recuperacao_senha)
