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

Ainda não há código nem comandos de build/test definidos. Ao criar `frontend/` e `backend/`, **registre aqui** os comandos reais (instalar, rodar, testar, migrar).

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
