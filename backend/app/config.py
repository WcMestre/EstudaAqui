# PROVISÓRIO: substituir pela implementação da issue [0.2]
"""Configuração da API, lida de variáveis de ambiente (ou do arquivo .env).

Nenhum valor secreto tem padrão aqui: se faltar, a API nem sobe. Assim um
segredo de exemplo nunca vai parar em produção por esquecimento.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PASTA_RAIZ = Path(__file__).resolve().parents[2]


class Configuracoes(BaseSettings):
    model_config = SettingsConfigDict(env_file=PASTA_RAIZ / ".env", extra="ignore")

    database_url: str
    jwt_segredo: str
    jwt_algoritmo: str = "HS256"
    jwt_expira_minutos: int = 30
    cookie_sessao_nome: str = "estudaaqui_sessao"
    frontend_url: str = "http://localhost:3000"


configuracoes = Configuracoes()
