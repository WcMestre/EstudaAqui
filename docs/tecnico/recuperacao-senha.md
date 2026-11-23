# Recuperação de senha — issue #6 [1.2]

> Documento técnico da entrega 1.2 do [escopo](../ESCOPO.md). Registra o que
> foi feito, as decisões tomadas e o motivo de cada uma.
>
> **Situação:** em andamento (F1 a F5 concluídas; próxima: F6). Branch `sprint-1/recuperar-senha`.

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
| F6 | Verificação final: critérios, Definição de pronto, revisão de segurança | Pendente |
| F7 | Documentação final (CLAUDE.md, este documento) e Pull Request | Pendente |

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
| C2 — link de 1 hora e uso único | `test_token_expira_em_uma_hora`, `test_email_informa_que_o_link_vale_por_uma_hora`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_usar_um_link_invalida_os_outros_links_pendentes` | — |
| C3 — nova senha funciona e permite entrar | `test_redefinir_com_link_valido_permite_entrar_com_a_nova_senha`, `test_senha_antiga_deixa_de_funcionar_apos_redefinir` | sucesso leva a "Entrar" |
| C4 — link expirado/usado: mensagem clara e pedir outro | `test_link_expirado_e_recusado_com_mensagem_clara`, `test_link_ja_usado_e_recusado_com_mensagem_clara`, `test_link_inexistente_e_recusado` | 3 códigos + sem token oferecem "Pedir novo link" |
| Só o hash do token | `test_token_fica_guardado_apenas_como_hash_sha256` | — |
| 3 pedidos por hora | `test_limite_de_tres_pedidos_por_hora_e_silencioso`, `test_limite_e_contado_separadamente_para_cada_email`, `test_pedidos_com_mais_de_uma_hora_nao_contam_para_o_limite` | — |
| Senha com 8+ caracteres | `test_senha_com_menos_de_8_caracteres_e_recusada_sem_gastar_o_link` | 7 caracteres recusados |
| Redefinir encerra sessões | `test_redefinir_encerra_as_sessoes_abertas_antes` | — |
| Mensagens em português | `test_mensagens_em_portugues.py` (14 casos) | — |

Ponta a ponta (Playwright, `frontend/e2e/recuperacao-senha.spec.ts`):

| Teste | Cobre |
|---|---|
| `pedir o link, ler o e-mail, redefinir a senha e entrar com a nova senha` — login → "Esqueci minha senha" → mensagem genérica → e-mail no Mailpit → link abre sem token na URL e com `Referrer-Policy: no-referrer` → nova senha → entra; senha antiga recusada | C1, C2, C3 |
| `link já usado mostra mensagem clara e oferece pedir outro` — link usado uma vez pela API, reaberto no navegador → mensagem → "Pedir novo link" leva a `/esqueci-senha` | C2 (uso único), C4 |

## 6. O que é provisório

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

## 7. Pontos a combinar com o grupo

- Uso do `uv`, base provisória e Mailpit no `docker-compose.yml` (issues [0.1], [0.2], [0.3]).
- Com o responsável pela [1.1]: coluna `senha_alterada_em`, verificação do
  `iat` no `usuario_atual` e `iat` com fração de segundo.

## 8. O que falta

- [ ] F6 — conferir critérios e Definição de pronto, revisão de segurança, lint e testes.
- [ ] F7 — comandos no `CLAUDE.md`, `.env.example` final, versão final deste documento e rascunho do PR.
