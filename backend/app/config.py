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

    # E-mail (SMTP). Os padrões apontam para o Mailpit do docker-compose.
    smtp_host: str = "localhost"
    smtp_porta: int = 1025
    smtp_usuario: str = ""
    smtp_senha: str = ""
    smtp_starttls: bool = False
    smtp_ssl: bool = False
    email_remetente: str = "nao-responda@example.com"
    email_remetente_nome: str = "EstudaAqui"
    # true = não envia de verdade (usado pelos testes automatizados).
    email_suprimir_envio: bool = False


configuracoes = Configuracoes()
