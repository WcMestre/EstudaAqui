# Recuperação de senha — issue #6 [1.2]

> Documento técnico da entrega 1.2 do [escopo](../ESCOPO.md). Registra o que
> foi feito, as decisões tomadas e o motivo de cada uma.
>
> **Situação:** implementação concluída (F1 a F7); aguardando revisão no Pull Request. Branch `sprint-1/recuperar-senha`.

## 1. O que a entrega faz

Quem esqueceu a senha informa o e-mail na tela "Esqueci minha senha" e recebe
um link válido por 1 hora e de uso único. Pelo link, define a nova senha e
volta a entrar no sistema. Link expirado, já usado ou inválido mostra uma
mensagem clara e oferece pedir outro.

## 2. Andamento por fase

| Fase | Conteúdo | Situação |
|---|---|---|
| F1 | Testes do back-end escritos antes da implementação (20 testes) | Concluída |
| F2 | Base provisória do back-end (FastAPI, banco, erro padrão, login mínimo) | Concluída |
| F3 | Back-end definitivo da recuperação de senha + mensagens em português | Concluída |
| F4 | Front-end: base provisória, telas definitivas e testes (Vitest) | Concluída |
| F5 | Teste ponta a ponta (Playwright + Mailpit) | Concluída |
| F6 | Verificação final: critérios, Definição de pronto, revisão de segurança | Concluída |
| F7 | Documentação final (CLAUDE.md, este documento) e Pull Request | Concluída |

## 3. Arquitetura

### Back-end (`backend/`)

| Caminho | Papel | Provisório? |
|---|---|---|
| `app/modulos/recuperacao_senha/` | Rotas, serviço, modelo, schemas, e-mail e templates da entrega | Não |
| `app/mensagens_validacao.py` | Tradução das mensagens de validação para português | Não |
| `migracoes/versions/0002_*`, `0003_*` | Coluna `senha_alterada_em` e tabela `tokens_redefinicao_senha` | Não |
| `app/main.py`, `config.py`, `banco.py`, `erros.py` | Núcleo da API | Sim — [0.2] |
| `app/modulos/usuarios/`, `app/modulos/autenticacao/` | Tabela `usuarios`, Argon2, JWT em cookie, login | Sim — [1.1] |
| `docker-compose.yml`, `.env.example` | Postgres 16 e Mailpit | Sim — [0.1] |

Rotas:

| Rota | Entrada | Resposta |
|---|---|---|
| `POST /api/v1/auth/esqueci-senha` | `{"email"}` | Sempre `200 {"mensagem"}` (mesma mensagem para qualquer e-mail) |
| `POST /api/v1/auth/redefinir-senha` | `{"token", "nova_senha"}` | `200 {"mensagem"}` ou `400 {"codigo", "mensagem"}` com `link_invalido`, `link_expirado` ou `link_ja_usado` |

Tabela `tokens_redefinicao_senha`: `id`, `usuario_id`, `token_hash`,
`expira_em`, `usado_em`, `ativo`, `criado_em`, `atualizado_em`.

### Front-end (`frontend/`)

| Caminho | Papel | Provisório? |
|---|---|---|
| `src/features/recuperacao-senha/` | Formulários, regras (Zod) e chamadas à API | Não |
| `src/app/esqueci-senha/`, `src/app/redefinir-senha/` | Páginas | Não |
| `next.config.ts` (cabeçalho `Referrer-Policy`) | Proteção do token | Não |
| `src/lib/api/cliente.ts`, `src/app/providers.tsx`, `src/app/layout.tsx`, `src/components/*.tsx` | Cliente HTTP, TanStack Query, layout e componentes | Sim — [0.3] |
| `src/features/autenticacao/`, `src/app/login/` | Tela de login mínima | Sim — [1.1] |

### Teste ponta a ponta

| Caminho | Papel |
|---|---|
| `frontend/playwright.config.ts` | Sobe API (porta 8001) e front (porta 3001, build de produção) só para o teste |
| `frontend/e2e/recuperacao-senha.spec.ts` | Os cenários |
| `frontend/e2e/mailpit.ts` | Lê e apaga e-mails pela API REST do Mailpit |
| `frontend/e2e/preparacao-global.ts`, `usuarios.ts`, `enderecos.ts` | Prepara o banco e2e e define usuários e endereços |
| `backend/scripts/preparar_banco_e2e.py` | Cria o banco `estudaaqui_e2e`, aplica as migrações e cadastra os usuários |

## 4. Decisões e motivos

### Segurança do link

| Decisão | Motivo |
|---|---|
| Token gerado com `secrets.token_urlsafe(32)` (256 bits) | Aleatório criptográfico; impossível de adivinhar por tentativa. |
| Banco guarda só o hash SHA-256 do token | Se o banco vazar, os links continuam inúteis. SHA-256 basta (não precisa Argon2) porque o token já é aleatório e longo. |
| Validade de 1 hora | Exigência da issue; limita a janela de uso de um e-mail esquecido aberto. |
| Uso único + invalidação dos outros links pendentes | Um e-mail antigo esquecido na caixa de entrada não vira "porta dos fundos". O link usado recebe `usado_em`; os outros, `ativo = false`. |
| `SELECT ... FOR UPDATE` no token e no usuário | Duas requisições simultâneas com o mesmo link não trocam a senha duas vezes, e pedidos simultâneos não furam o limite. |
| Usuário inativado não recebe link nem redefine | Regra 7 do CLAUDE.md (inativado não acessa). |

### Não revelar quem tem conta

| Decisão | Motivo |
|---|---|
| Resposta sempre `200` com a mesma mensagem | O pedido não pode denunciar se o e-mail existe. |
| Todo o trabalho do pedido roda em `BackgroundTasks` (busca, token e e-mail) | Se a busca e a gravação rodassem antes da resposta, e-mails existentes demorariam mais. Medido: mediana de 8,4 ms (existe) × 10,8 ms (não existe), faixas sobrepostas. |
| Limite de 3 pedidos por hora por e-mail, silencioso | Evita spam na caixa de alguém; o 4º pedido responde igual, mas não envia. |

### Sessões antigas

| Decisão | Motivo |
|---|---|
| Coluna `usuarios.senha_alterada_em` | Ao redefinir, sessões abertas antes (inclusive a de quem roubou a senha) deixam de valer. |
| `usuario_atual` recusa JWT com `iat` anterior a ela | É o ponto único que todas as rotas protegidas usam. |
| `iat` do JWT com fração de segundo | Com segundos inteiros, um login feito no mesmo segundo da troca seria recusado por engano. |

### Senha e mensagens

| Decisão | Motivo |
|---|---|
| Senha de 8 a 128 caracteres | 8 é a regra da issue; o teto evita gastar CPU com Argon2 em textos enormes. |
| Senha recusada não "gasta" o link | O usuário corrige e tenta de novo com o mesmo link. |
| Mensagens de erro em português, inclusive as de validação do Pydantic | Pedido do produto; o tradutor fica em arquivo próprio para sobreviver à troca da base. |

### E-mail

| Decisão | Motivo |
|---|---|
| `fastapi-mail` + Jinja2, versões HTML e texto puro | Ferramentas da issue; a versão em texto melhora a entrega e a leitura. |
| `autoescape` ligado no HTML | Um nome como `<b>x</b>` vira texto, não HTML. |
| Mailpit no `docker-compose.yml` (versão fixada) | Exigência da issue; mostra os e-mails em http://localhost:8025 e tem API usada no teste ponta a ponta. |
| Falha de SMTP vai para o log, sem o link | O link é secreto e não deve aparecer em log. |

### Front-end

| Decisão | Motivo |
|---|---|
| Token lido no navegador e apagado da URL (`history.replaceState`) | Não fica no histórico, em prints nem no cabeçalho `Referer`. Também mantém a página estática (o Next 16 com `cacheComponents` exigiria `<Suspense>` para `useSearchParams`). |
| `Referrer-Policy: no-referrer` (cabeçalho e meta tag) | Proteção em dobro contra vazamento da URL com o token. |
| Erro do link troca a tela por "Pedir novo link"; outros erros mantêm o formulário | Link morto não tem conserto; erro de digitação tem. |
| Regras repetidas no Zod | Só para retorno imediato; quem garante é o back-end. |

### Ferramentas

| Decisão | Motivo |
|---|---|
| `uv` como gerenciador do Python | Um dos dois sugeridos na issue [0.2]; rápido e com `uv.lock` reproduzível. |
| `httpx2` no lugar de `httpx` nos testes | A versão atual do Starlette marca `httpx` como obsoleto no cliente de testes. |
| `shadcn` em `devDependencies` | O projeto só usa um CSS dele durante o build; a ferramenta de linha de comando não vai para produção. |
| Next 16.4.5, Vitest 4.1.12, sem `@vitejs/plugin-react` | Versões com mais de duas semanas; Vitest 5 exige `@types/node` 22 (projeto usa Node 20); o plugin trazia um Babel de teste em conflito e o Vite 8 já entende JSX. |
| `frontend/AGENTS.md` fora do git | Arquivo gerado automaticamente pelo `next dev`; não faz parte do projeto. |

### Teste ponta a ponta

| Decisão | Motivo |
|---|---|
| Banco (`estudaaqui_e2e`) e portas (3001/8001) próprios | Nunca apaga dados de desenvolvimento nem reaproveita por engano um servidor de desenvolvimento aberto. |
| Script de preparação recusa banco que não termine em `_e2e` | Trava contra apagar o banco errado. |
| Usuários criados direto no banco pelo script | O cadastro pela tela é da issue [1.4], que ainda não existe. |
| Front em build de produção (`next build` + `next start`) | Testa o que vai ao ar, inclusive o cabeçalho `Referrer-Policy`. |
| E-mail lido de verdade no Mailpit, filtrado por destinatário | Prova o caminho real (SMTP → caixa → link), sem simulação. |
| Um teste por vez (`workers: 1`) e um usuário por teste | Os testes compartilham banco e caixa de e-mail; evita interferência. |

## 5. Critério de aceite → testes

| Critério / requisito | Back-end (pytest) | Front-end (Vitest) |
|---|---|---|
| C1 — "Esqueci minha senha" com mensagem igual para todos | `test_email_cadastrado_recebe_mensagem_generica_e_um_email`, `test_mesma_mensagem_para_email_inexistente`, `test_mesma_mensagem_e_nenhum_email_para_usuario_inativo` | link no login; envio mostra a mensagem genérica |
| C2 — link de 1 hora e uso único | `test_token_expira_em_uma_hora`, `test_email_informa_que_o_link_vale_por_uma_hora`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_usar_um_link_invalida_os_outros_links_pendentes`, `test_mesmo_link_enviado_ao_mesmo_tempo_so_funciona_uma_vez` | — |
| C3 — nova senha funciona e permite entrar | `test_redefinir_com_link_valido_permite_entrar_com_a_nova_senha`, `test_senha_antiga_deixa_de_funcionar_apos_redefinir` | sucesso leva a "Entrar" |
| C4 — link expirado/usado: mensagem clara e pedir outro | `test_link_expirado_e_recusado_com_mensagem_clara`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_link_inexistente_e_recusado` | 3 códigos + sem token oferecem "Pedir novo link" |
| Só o hash do token | `test_token_fica_guardado_apenas_como_hash_sha256` | — |
| 3 pedidos por hora | `test_limite_de_tres_pedidos_por_hora_e_silencioso`, `test_limite_e_contado_separadamente_para_cada_email`, `test_pedidos_com_mais_de_uma_hora_nao_contam_para_o_limite` | — |
| Senha com 8+ caracteres | `test_senha_com_menos_de_8_caracteres_e_recusada_sem_gastar_o_link` | 7 caracteres recusados |
| Redefinir encerra sessões | `test_redefinir_encerra_as_sessoes_abertas_antes` | — |
| Mensagens em português | `test_mensagens_em_portugues.py` (14 casos) | — |
| Segurança (ataques específicos) | `test_seguranca.py` (3 testes; ver §6.3) | — |

Ponta a ponta (Playwright, `frontend/e2e/recuperacao-senha.spec.ts`):

| Teste | Cobre |
|---|---|
| `pedir o link, ler o e-mail, redefinir a senha e entrar com a nova senha` — login → "Esqueci minha senha" → mensagem genérica → e-mail no Mailpit → link abre sem token na URL e com `Referrer-Policy: no-referrer` → nova senha → entra; senha antiga recusada | C1, C2, C3 |
| `link já usado mostra mensagem clara e oferece pedir outro` — link usado uma vez pela API, reaberto no navegador → mensagem → "Pedir novo link" leva a `/esqueci-senha` | C2 (uso único), C4 |

## 6. Verificação final (F6)

Executada em 24/11/2026: pytest 37/37, Vitest 14/14, Playwright 2/2; ruff, ESLint,
`tsc`, Prettier e `alembic check` sem pendências.

### 6.1 Critérios de aceite da issue #6

| # | Critério | Comprovação | Resultado |
|---|---|---|---|
| C1 | Na tela de login existe "Esqueci minha senha"; o usuário informa o e-mail e recebe a mesma mensagem, exista o e-mail ou não | Vitest: link no login aponta para `/esqueci-senha`; envio mostra a mensagem genérica. pytest: `test_email_cadastrado_recebe_mensagem_generica_e_um_email`, `test_mesma_mensagem_para_email_inexistente`, `test_mesma_mensagem_e_nenhum_email_para_usuario_inativo`. Playwright: clica no link do login e vê a mensagem | Atendido |
| C2 | O e-mail contém um link com validade limitada (1 hora) e de uso único | pytest: `test_token_expira_em_uma_hora`, `test_email_informa_que_o_link_vale_por_uma_hora`, `test_link_expirado_e_recusado_com_mensagem_clara`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_usar_um_link_invalida_os_outros_links_pendentes`, `test_mesmo_link_enviado_ao_mesmo_tempo_so_funciona_uma_vez`. Playwright: link lido no Mailpit; link já usado | Atendido |
| C3 | Pelo link o usuário define uma nova senha e consegue entrar com ela | pytest: `test_redefinir_com_link_valido_permite_entrar_com_a_nova_senha`, `test_senha_antiga_deixa_de_funcionar_apos_redefinir`. Vitest: sucesso oferece "Entrar". Playwright: entra com a nova senha; a antiga é recusada | Atendido |
| C4 | Link expirado ou já usado mostra mensagem clara e oferece pedir outro | pytest: `test_link_expirado_e_recusado_com_mensagem_clara`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_link_inexistente_e_recusado`. Vitest: os 3 códigos e a falta de token mostram a mensagem e "Pedir novo link". Playwright: link já usado → mensagem → "Pedir novo link" abre `/esqueci-senha` | Atendido |

### 6.2 Definição de pronto

| Item | Situação | Comprovação |
|---|---|---|
| Branch própria e integração via PR revisado por outro desenvolvedor | Parcial | Branch `sprint-1/recuperar-senha` no GitHub. PR com pedido de revisão aberto na F7, aguardando o revisor |
| Critérios de aceite verificados manualmente, passo a passo | Atendido | Roteiro manual da seção 7 (10 passos) executado pelo autor no navegador em 24/11/2026, todos com o resultado esperado; conferido pelos registros da API, do banco e do Mailpit. Antes disso: servidor real e Mailpit (F3) e navegador real via Playwright (F5) |
| Testes automatizados criados e passando (pytest; vitest/playwright quando há tela) | Atendido | pytest 37, Vitest 14, Playwright 2 |
| Regras de permissão garantidas no back-end | Atendido | Toda regra (usuário inativo, validade, uso único, limite, sessões) está em `servico.py`/`dependencias.py` e é comprovada pelo pytest direto na API, sem passar pelo front. O Zod no front só repete validações |
| Nenhum segredo versionado; `.env.example` atualizado | Atendido | Varredura de todos os commits da branch (§6.3). `.env.example` (raiz e `frontend/`) com todas as variáveis novas |
| Comandos novos registrados no `CLAUDE.md` | Atendido | Seção "Comandos" com a escolha do `uv` e os comandos de instalar, rodar, migrar e testar (back, front e ponta a ponta), conferidos num clone novo da branch (F7) |

### 6.3 Revisão de segurança

**Verificações automáticas**

| Verificação | Comando | Resultado |
|---|---|---|
| Regras de segurança do ruff (Bandit) | `uv run ruff check --select S .` | 66 avisos, todos S101 (`assert`) em `tests/`: é como o pytest verifica resultados. Justificado. Código da aplicação, scripts e migrações: 0. A regra `S` ficou **ativa permanentemente** no `pyproject.toml`, com exceção do S101 só em `tests/` |
| Dependências do back-end | `uv export ... > req.txt && uvx pip-audit -r req.txt` | 55 pacotes, **0 vulnerabilidades** |
| Dependências do front-end | `npm audit` e `npm audit --omit=dev` | Produção: **0**. Completo: 4 moderadas, uma só cadeia (`shadcn` → `ts-morph` → `minimatch`, lentidão com padrão de arquivo malicioso). É a ferramenta de linha de comando do shadcn: não entra no build (conferido em `.next/`) e só processa padrões do próprio desenvolvedor. O `shadcn` foi movido para `devDependencies` (o projeto só usa um CSS dele no build). O `npm audit fix --force` rebaixaria o shadcn para 1.0.0 e quebraria o projeto; forçar `minimatch` 11 via `overrides` contraria a versão pedida pelo `@ts-morph/common` |
| Segredos no histórico | varredura de `git log -p main..HEAD` | 0. Só os `.env.example` (valores de exemplo) foram versionados; nenhuma chave conhecida (GitHub, AWS, chave privada, JWT); o segredo real do `.env` local não aparece em nenhum commit |

**Ameaça → Proteção → Teste que comprova**

| Ameaça | Proteção | Teste que comprova |
|---|---|---|
| Descobrir quem tem conta pela resposta | Resposta sempre 200 com a mesma mensagem (inclusive inativos e limite estourado) | `test_mesma_mensagem_para_email_inexistente`, `test_mesma_mensagem_e_nenhum_email_para_usuario_inativo`, `test_limite_de_tres_pedidos_por_hora_e_silencioso` |
| Descobrir quem tem conta pelo tempo de resposta | Busca, token e e-mail rodam depois da resposta (`BackgroundTasks`) | Medição manual (F3): mediana 8,4 ms × 10,8 ms. Sem teste automatizado: tempo varia por máquina e daria falso alarme |
| Adivinhar um token | `secrets.token_urlsafe(32)` (256 bits) | `test_link_inexistente_e_recusado` |
| Vazamento do banco expõe links válidos | Só o hash SHA-256 é guardado | `test_token_fica_guardado_apenas_como_hash_sha256` |
| Reusar um link | Uso único (`usado_em`) | `test_link_ja_usado_e_recusado_com_mensagem_clara`; Playwright "link já usado" |
| Usar o mesmo link várias vezes em paralelo | `SELECT ... FOR UPDATE` no token | `test_mesmo_link_enviado_ao_mesmo_tempo_so_funciona_uma_vez` (sem o `FOR UPDATE` o teste falha: 5 trocas aceitas) |
| E-mail antigo esquecido na caixa vira porta dos fundos | Usar um link invalida os pendentes | `test_usar_um_link_invalida_os_outros_links_pendentes` |
| Link usado muito depois | Validade de 1 hora | `test_token_expira_em_uma_hora`, `test_link_expirado_e_recusado_com_mensagem_clara` |
| Inundar a caixa de alguém | 3 pedidos por hora por e-mail, silencioso | `test_limite_de_tres_pedidos_por_hora_e_silencioso`, `test_limite_e_contado_separadamente_para_cada_email`, `test_pedidos_com_mais_de_uma_hora_nao_contam_para_o_limite` |
| Invasor segue logado depois da troca | `senha_alterada_em` + recusa de JWT com `iat` anterior | `test_redefinir_encerra_as_sessoes_abertas_antes` (e `test_redefinir_com_link_valido_permite_entrar_com_a_nova_senha` prova que a sessão nova vale) |
| Token vaza pelo histórico, prints ou cabeçalho `Referer` | Token apagado da URL + `Referrer-Policy: no-referrer` | Vitest "tira o token da URL..."; Playwright confere URL limpa e o cabeçalho |
| Link do e-mail apontar para o site do atacante (cabeçalho `Host` falso) | Link montado com `FRONTEND_URL` da configuração | `test_link_usa_o_endereco_configurado_e_ignora_o_host_do_pedido` |
| Injetar HTML no e-mail pelo nome | `autoescape` do Jinja2 | `test_nome_do_usuario_nao_vira_html_no_email` |
| Gastar CPU com senha gigante (Argon2) | Máximo de 128 caracteres | `test_senha_longa_demais_tem_mensagem_em_portugues` |
| Usuário inativado recuperar acesso | Inativo não recebe link nem redefine | `test_mesma_mensagem_e_nenhum_email_para_usuario_inativo`, `test_usuario_inativado_depois_do_pedido_nao_consegue_redefinir` |
| Outro site chamar a API com o cookie do usuário | CORS só para `FRONTEND_URL`, cookie `SameSite=Lax`; redefinir exige o token | Verificação manual (F4): preflight de outra origem recusado (400) |
| Link secreto parar em log | Falha de SMTP registrada sem o link | Revisão de código (`email.py`) |

**Limitações conhecidas** (fora do escopo da #6)

- A busca do e-mail não diferencia maiúsculas, mas a coluna `email` da tabela
  provisória é única diferenciando maiúsculas. Se existirem `A@x.com` e
  `a@x.com`, o link vai para um deles. Normalizar e-mails é da [1.1]/[1.4].
- O limite é por e-mail; não há limite por IP (a issue não pede).

## 7. Como rodar e testar

Os comandos (instalar, rodar, migrar, testar) estão no [CLAUDE.md](../../CLAUDE.md#comandos).
Roteiro manual da entrega (executado pelo autor em 24/11/2026, todos os passos com o resultado esperado):

1. `docker compose up -d`; na pasta `backend/`, `uv run alembic upgrade head` e `uv run uvicorn app.main:app --reload`; na pasta `frontend/`, `npm run dev`.
2. Cadastre um usuário de teste (ainda não há tela de cadastro, que é da [1.4]):
   `cd backend && uv run python -c "from app.banco import SessaoLocal; from app.modulos.usuarios.modelos import Usuario; from app.modulos.usuarios.seguranca import gerar_hash_senha as h; s=SessaoLocal(); s.add(Usuario(nome='Teste', email='teste@example.com', senha_hash=h('SenhaAntiga123'), papel='aluno')); s.commit()"`
3. Em http://localhost:3000/login, clique em **Esqueci minha senha** e informe `teste@example.com`. Repita com `ninguem@example.com`: a mensagem é a mesma.
4. Abra o e-mail em http://localhost:8025 e clique em **Criar nova senha**. O token some da barra de endereço.
5. Defina a nova senha e entre com ela em `/login`. A senha antiga é recusada.
6. Abra o mesmo link do e-mail de novo e tente usar: aparece "Este link já foi usado" com o botão **Pedir novo link**.

## 8. Tamanho da entrega

Linhas adicionadas na branch em relação à `main` (`git diff --numstat main..HEAD`):

| Grupo | Arquivos | Linhas | % |
|---|---:|---:|---:|
| Gerados automaticamente (travas de versão `package-lock.json`/`uv.lock` = 11.948; componentes e configurações do shadcn/Next/Alembic) | 17 | 12.643 | 79,5 |
| Base provisória ([0.1], [0.2], [0.3], [1.1]) | 24 | 860 | 5,4 |
| Testes (pytest, Vitest, Playwright e preparação do banco e2e) | 21 | 1.179 | 7,4 |
| Código definitivo da #6 | 18 | 826 | 5,2 |
| Documentação (este documento e `CLAUDE.md`) | 2 | 317 | 2,0 |
| Configuração (`package.json`, `.gitignore`, Prettier, `.nvmrc`, `__init__.py`) | 10 | 78 | 0,5 |
| **Total** | **92** | **15.903** | 100 |

Sem os arquivos gerados, a entrega tem 3.260 linhas escritas à mão, das quais 36 % são testes.

## 9. O que é provisório

Todo arquivo provisório tem no topo o comentário
`PROVISÓRIO: substituir pela implementação da issue [x.y]`. Ao substituir,
**manter** os trechos marcados como "issue [1.2] (NÃO provisório)":

- coluna `senha_alterada_em` em `usuarios/modelos.py`;
- verificação do `iat` em `autenticacao/dependencias.py`;
- `iat` com fração de segundo em `autenticacao/sessao.py`;
- chamada a `traduzir_erro` em `app/erros.py`.

Fora da base provisória (são entregas de outras issues): rota `/saude`, seed do
administrador, CI, limite de tentativas de login, redirecionamento por perfil,
`middleware.ts`.

## 10. Pontos a combinar com o grupo

Situação em 24/11/2026: **a combinar** (o grupo ainda não foi avisado).

- Uso do `uv`, base provisória e Mailpit no `docker-compose.yml` (issues [0.1], [0.2], [0.3]).
- Com o responsável pela [1.1]: coluna `senha_alterada_em`, verificação do
  `iat` no `usuario_atual` e `iat` com fração de segundo.

## 11. O que falta

- [ ] Revisão do PR por outro desenvolvedor (sugestão: responsável pela [1.1], por causa dos pontos da seção 10).
- [ ] Avisar o grupo e combinar os pontos da seção 10.
- [ ] `README.md` da raiz ainda diz "nenhum código implementado"; a seção "Como rodar o projeto" é entrega da [0.1].

**Melhorias futuras sugeridas** (configuração do repositório, fora do código):
ativar o **Dependabot** (avisos e PRs automáticos de dependências vulneráveis)
e o **CodeQL** (análise de segurança do código a cada PR) em
*Settings → Code security*.
