# EstudaAqui — Memória base do projeto

Plataforma web de **gestão de conhecimento** (matérias, turmas, materiais e atividades). Escopo completo e entregas por Sprint em [docs/ESCOPO.md](docs/ESCOPO.md) — **leia antes de implementar qualquer funcionalidade** e mantenha-o atualizado quando o escopo mudar.

Contexto: projeto acadêmico (UNILAGO — Desenvolvimento de Sistemas WEB, P2). Idioma do produto, da documentação e dos commits: **português (Brasil)**.

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | **Next.js** (React) |
| Back-end | **Python** (framework a definir na Sprint 1; sugestão: FastAPI) |
| Banco de dados | **PostgreSQL** |

Estrutura planejada do repositório (criar conforme as sprints avançarem):

```
EstudaAqui/
├── docs/        # documentação (ESCOPO.md e futuras)
├── frontend/    # aplicação Next.js
├── backend/     # API Python
└── CLAUDE.md
```

## Comandos

> **Provisório:** a estrutura atual veio da issue [1.2] (recuperação de senha) antes das bases do projeto. Os comandos marcados com [0.1], [0.2] ou [0.3] serão confirmados ou substituídos por essas issues.

**Gerenciador de dependências do back-end: `uv`** (uma das opções da [0.2]). Instala o Python 3.12 fixado em `backend/.python-version` e trava as versões em `backend/uv.lock`, para todos rodarem exatamente o mesmo ambiente.

Pré-requisitos: Docker, [`uv`](https://docs.astral.sh/uv/) e Node 20 (`frontend/.nvmrc`).

| Ação | Comando | Origem |
|---|---|---|
| Variáveis de ambiente | `cp .env.example .env` e `cp frontend/.env.example frontend/.env.local` (troque o `JWT_SEGREDO`) | [0.1] |
| Subir Postgres 16 e Mailpit | `docker compose up -d` (e-mails de desenvolvimento em http://localhost:8025) | [0.1] |
| Back: instalar | `cd backend && uv sync` | [0.2] |
| Back: migrar o banco | `uv run alembic upgrade head` | [0.2] |
| Back: criar migração | `uv run alembic revision --autogenerate -m "descricao"` | [0.2] |
| Back: rodar | `uv run uvicorn app.main:app --reload` (documentação em http://localhost:8000/docs) | [0.2] |
| Back: testar | `uv run pytest` (usa o banco `estudaaqui_teste`, criado sozinho) | [0.2] |
| Back: lint e formatação | `uv run ruff check . && uv run ruff format --check .` | [0.2] |
| Front: instalar | `cd frontend && npm ci` | [0.3] |
| Front: rodar | `npm run dev` (http://localhost:3000) | [0.3] |
| Front: testar | `npm test` (Vitest) | [0.3] |
| Front: lint, tipos e formatação | `npm run lint && npm run typecheck && npm run format:check` | [0.3] |
| Ponta a ponta | `npx playwright install --with-deps chromium` (uma vez) e `npm run test:e2e` — exige `docker compose up -d` e `uv` no PATH; usa as portas 3001/8001 e o banco `estudaaqui_e2e` | [0.3] |

## Domínio e regras de negócio (invariantes)

Perfis: **Administrador** (cadastros), **Professor** (responsável por uma matéria), **Aluno** (consulta + responde atividades).

Estas regras valem em **toda** a aplicação e **devem ser garantidas no back-end** (nunca só escondendo botões no front):

1. Cada **matéria** tem exatamente **um professor responsável**; cada professor responde por **uma única matéria** (unicidade nos dois sentidos).
2. Cada **turma** tem várias matérias; uma matéria pode estar em várias turmas. Aluno pode estar em mais de uma turma.
3. **Aluno só acessa matérias das turmas às quais pertence.** Qualquer outro recurso responde como inexistente/proibido.
4. **Professor só administra a própria matéria** (conteúdo, atividades, correções).
5. **Acesso do aluno é consultivo (somente leitura)** — a única escrita permitida a ele é responder questionários e enviar arquivos de atividades liberadas à sua turma, dentro do prazo e das regras da atividade.
6. Todo conteúdo/atividade é publicado para **turmas escolhidas** (subconjunto das turmas que cursam a matéria).
7. Cadastros com histórico são **inativados**, não excluídos (exclusão lógica).
8. Aluno só vê a **própria** nota, resposta e devolutiva.

Tipos de conteúdo: aviso/texto, arquivo, vídeo, link externo, questionário (múltipla escolha, V/F, escrita), entrega de arquivo para avaliação.

## Roadmap (resumo — detalhes em docs/ESCOPO.md)

1. Acesso e cadastros base (login, professores, matérias, turmas, alunos)
2. Painel do professor e publicação de materiais
3. Painel do aluno (consulta)
4. Questionários
5. Entrega de arquivos para avaliação
6. Notas, acompanhamento e fechamento

## Convenções de trabalho

- Branch principal: `main`. Para cada sprint/entrega, preferir branch própria (`sprint-N/descricao`) e integrar via PR.
- Mensagens de commit em português, no imperativo, referenciando a entrega do escopo quando houver (ex.: `Adiciona cadastro de matérias (1.5)`).
- Mudou regra de negócio ou escopo? Atualize `docs/ESCOPO.md` e a seção de invariantes deste arquivo no mesmo commit.
- Não versionar segredos (`.env`, chaves, credenciais); fornecer um `.env.example` quando necessário.
- Documento de escopo é **não técnico** e descreve entregas em nível de usuário; detalhes técnicos ficam neste arquivo ou em `docs/` separados.

## Pontos em aberto (ver docs/ESCOPO.md §5 e §6)

Perfil Administrador assumido; limites de upload; escala de notas; notificações por e-mail; visibilidade de colegas de turma.
