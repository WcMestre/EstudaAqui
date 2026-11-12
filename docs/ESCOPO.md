# EstudaAqui — Escopo do Projeto

> Plataforma web de **gestão de conhecimento** para instituições de ensino: professores publicam materiais e atividades; alunos consultam e respondem apenas o que pertence às suas turmas.

Este documento descreve **o que o sistema entrega do ponto de vista de quem o usa**. Não contém decisões técnicas (ver [CLAUDE.md](../CLAUDE.md) para a stack).

---

## 1. Visão geral

### 1.1 Objetivo
Dar a cada professor um espaço próprio para organizar e publicar o conteúdo da sua matéria, e dar a cada aluno um lugar único e organizado para consultar esse conteúdo e cumprir as atividades propostas.

### 1.2 Quem usa o sistema

| Perfil | O que faz no sistema |
|---|---|
| **Administrador** (secretaria / coordenação) | Cadastra e mantém alunos, professores, matérias e turmas, e define quem pertence a quê. Não publica conteúdo pedagógico. |
| **Professor** | É o responsável (administrador) por **uma matéria**. Publica materiais, cria questionários e atividades de entrega de arquivo, corrige e dá notas. |
| **Aluno** | **Consulta** os materiais das matérias das turmas em que está matriculado e responde às atividades que lhe forem destinadas. |

### 1.3 Regras que valem para todo o sistema

1. **Cada matéria tem exatamente um professor responsável**, e cada professor é responsável por **uma matéria diferente** das dos demais.
2. **Cada turma tem um conjunto de matérias.** Uma mesma matéria pode ser oferecida a mais de uma turma.
3. **O aluno só vê o que é da sua turma.** Ele só acessa o painel das matérias das turmas às quais pertence; qualquer outra matéria ou turma é invisível para ele.
4. **O professor só administra a sua matéria.** Ele não vê nem altera o conteúdo de matérias de outros professores.
5. **O acesso do aluno é consultivo:** o aluno lê, visualiza e baixa conteúdo, mas **não cria, edita nem apaga** nada no painel da matéria. A única ação que ele realiza é **responder às atividades** (questionários e envio de arquivos) que o professor liberou para a sua turma.
6. Todo material ou atividade é publicado **para uma ou mais turmas escolhidas pelo professor** (entre as turmas que cursam a sua matéria).
7. Cadastros não são apagados quando já têm histórico; são **inativados** (deixam de aparecer/acessar, mas o histórico é preservado).

---

## 2. Tipos de conteúdo suportados

| Tipo | Exemplos de uso |
|---|---|
| **Aviso / texto** | Comunicados, resumo da aula, orientações |
| **Arquivo** | PDF, documentos de texto, planilhas, apresentações, imagens, arquivos compactados |
| **Vídeo** | Link de vídeo hospedado externamente ou arquivo de vídeo enviado |
| **Link externo** | Artigos, sites, repositórios, leituras complementares |
| **Questionário** | Prova ou exercício com correção automática e/ou manual |
| **Entrega de arquivo** | Atividade em que o aluno envia um trabalho para ser avaliado |

---

## 3. Entregas por Sprint

Cada entrega é descrita como **o que o usuário consegue fazer** ao final. Os critérios de aceite indicam como saber se a entrega está pronta.

### Sprint 1 — Acesso e Cadastros Base
*Meta: a instituição consegue montar sua estrutura (professores, matérias, turmas, alunos) e todos conseguem entrar no sistema.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 1.1 | **Entrar e sair do sistema** | Qualquer usuário acessa com e-mail e senha e sai com segurança. | Credenciais corretas entram; incorretas exibem mensagem clara; sessão pode ser encerrada. |
| 1.2 | **Recuperar senha** | Quem esqueceu a senha solicita a redefinição e cria uma nova. | Usuário recebe orientação de redefinição e consegue entrar com a nova senha. |
| 1.3 | **Perfis de acesso** | Ao entrar, cada usuário é levado à sua área (Administrador, Professor ou Aluno) e só enxerga as opções do seu perfil. | Um aluno não consegue abrir telas de professor ou administrador, e vice-versa. |
| 1.4 | **Cadastro de professores** | O administrador cadastra, edita, consulta e inativa professores. | Professor cadastrado consegue entrar; inativado não consegue mais entrar. |
| 1.5 | **Cadastro de matérias** | O administrador cadastra matérias e define **um professor responsável** por cada uma. | O sistema impede que um mesmo professor seja responsável por duas matérias ou que uma matéria tenha dois responsáveis. |
| 1.6 | **Cadastro de turmas** | O administrador cadastra turmas e escolhe **quais matérias** cada turma cursa. | Uma turma lista suas matérias; uma matéria pode estar em várias turmas. |
| 1.7 | **Cadastro de alunos** | O administrador cadastra alunos individualmente e os **vincula a uma ou mais turmas**. | Aluno aparece na lista da turma; pode ser movido ou removido de uma turma. |
| 1.8 | **Cadastro em lote de alunos** | O administrador importa uma lista de alunos a partir de uma planilha. | Planilha válida cria os alunos; linhas com erro são apontadas sem impedir as demais. |
| 1.9 | **Consultas e buscas nos cadastros** | O administrador filtra e busca professores, matérias, turmas e alunos por nome e situação (ativo/inativo). | Resultados correspondem ao filtro e a listas longas são paginadas. |

### Sprint 2 — Painel do Professor e Publicação de Materiais
*Meta: o professor consegue montar o conteúdo da sua matéria e disponibilizá-lo às turmas.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 2.1 | **Painel da minha matéria** | Ao entrar, o professor vê a sua matéria, as turmas que a cursam e os conteúdos já publicados. | O professor vê apenas a sua matéria e as turmas dela. |
| 2.2 | **Organização por tópicos** | O professor agrupa o conteúdo em seções (ex.: "Unidade 1", "Semana 3") e define a ordem de exibição. | Seções podem ser criadas, renomeadas, reordenadas e removidas. |
| 2.3 | **Publicar aviso/texto** | O professor escreve um comunicado ou texto formatado e publica. | O texto publicado aparece com a formatação escolhida. |
| 2.4 | **Publicar arquivo** | O professor envia um ou mais arquivos (PDF, documentos, planilhas, apresentações, imagens) com título e descrição. | Arquivos válidos são enviados; tipos ou tamanhos não permitidos são recusados com explicação. |
| 2.5 | **Publicar vídeo** | O professor adiciona um vídeo por link externo ou por envio de arquivo. | O vídeo pode ser reproduzido pelo aluno dentro da página da matéria. |
| 2.6 | **Publicar link externo** | O professor compartilha um endereço da internet com título e descrição. | O link abre em nova aba. |
| 2.7 | **Escolher as turmas destinatárias** | A cada publicação o professor marca para quais turmas ela é visível. | Turmas não marcadas não enxergam o conteúdo. |
| 2.8 | **Gerenciar publicações** | O professor edita, oculta, reexibe, reordena e exclui qualquer conteúdo seu. | Conteúdo oculto some para os alunos sem ser apagado; exclusão pede confirmação. |
| 2.9 | **Agendar publicação** | O professor define data e hora em que um conteúdo passa a ficar visível. | O conteúdo só aparece para o aluno a partir do horário definido. |

### Sprint 3 — Painel do Aluno (Consulta)
*Meta: o aluno encontra e consulta todo o conteúdo das suas matérias, de forma estritamente consultiva.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 3.1 | **Minhas matérias** | Ao entrar, o aluno vê um painel com as matérias das turmas em que está matriculado. | São listadas somente matérias das suas turmas. |
| 3.2 | **Painel da matéria** | O aluno abre uma matéria e vê o conteúdo organizado em tópicos, na ordem definida pelo professor. | Mostra apenas conteúdo publicado e destinado à sua turma. |
| 3.3 | **Visualizar e baixar materiais** | O aluno lê textos, reproduz vídeos, abre links e visualiza ou baixa arquivos. | Cada tipo de material abre corretamente; download disponível para arquivos. |
| 3.4 | **Buscar conteúdo** | O aluno pesquisa por título ou descrição dentro de uma matéria ou em todas as suas matérias. | Resultados respeitam as turmas do aluno. |
| 3.5 | **Novidades** | O aluno vê, na tela inicial, os conteúdos publicados mais recentemente. | Itens novos aparecem em ordem do mais recente ao mais antigo. |
| 3.6 | **Acesso estritamente consultivo** | O aluno não vê botões de criar, editar ou excluir conteúdo e não consegue fazê-lo por nenhum caminho. | Tentativa de acessar matéria/turma alheia ou de alterar conteúdo é bloqueada. |
| 3.7 | **Uso em celular** | O painel do aluno é confortável de usar em telas pequenas. | Todas as telas da Sprint 3 funcionam em celular sem perda de função. |

### Sprint 4 — Questionários
*Meta: o professor aplica questionários e o aluno os responde, com correção automática onde possível.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 4.1 | **Criar questionário** | O professor cria um questionário com título, instruções, perguntas e valor de cada pergunta. | Questionário pode ser salvo como rascunho e editado antes de publicar. |
| 4.2 | **Tipos de pergunta** | Perguntas de **múltipla escolha** (uma ou várias respostas), **verdadeiro/falso** e **resposta escrita**. | Cada tipo é exibido corretamente ao aluno. |
| 4.3 | **Gabarito** | Nas perguntas objetivas o professor indica a(s) resposta(s) correta(s). | O gabarito não é visível ao aluno antes da liberação. |
| 4.4 | **Regras de aplicação** | O professor define turmas, período de disponibilidade (início e fim), número de tentativas e tempo limite (opcional). | O aluno só responde dentro do período e do número de tentativas definidos. |
| 4.5 | **Responder questionário** | O aluno abre o questionário, responde e envia. | Respostas ficam registradas; envio fora do prazo é impedido; o aluno recebe confirmação de envio. |
| 4.6 | **Correção automática** | Perguntas objetivas são corrigidas e pontuadas automaticamente ao envio. | A nota das objetivas é calculada conforme o gabarito. |
| 4.7 | **Correção manual** | O professor lê as respostas escritas, atribui pontos e comenta. | A nota final soma objetivas e escritas; o aluno é avisado quando houver correção. |
| 4.8 | **Resultado para o aluno** | O aluno consulta sua nota, suas respostas e, se o professor liberar, o gabarito. | A liberação do gabarito é controlada pelo professor. |
| 4.9 | **Resultados para o professor** | O professor vê quem respondeu, quem não respondeu, notas e desempenho por pergunta. | Lista por turma com filtro de situação (respondeu / pendente). |

### Sprint 5 — Entrega de Arquivos para Avaliação
*Meta: o professor propõe trabalhos e o aluno envia arquivos para serem avaliados.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 5.1 | **Criar atividade de entrega** | O professor cria uma atividade com título, instruções, anexos de apoio, turmas, prazo e nota máxima. | Atividade aparece no painel das turmas escolhidas. |
| 5.2 | **Regras de envio** | O professor define tipos e tamanho de arquivo aceitos, quantidade de arquivos e se aceita envio após o prazo. | Envios fora das regras são recusados com explicação. |
| 5.3 | **Enviar trabalho** | O aluno anexa seu arquivo e envia, recebendo comprovante com data e hora. | O envio fica registrado e o aluno consegue conferi-lo. |
| 5.4 | **Substituir envio** | O aluno pode trocar o arquivo enviado enquanto o prazo estiver aberto. | Após o prazo (e sem aceite de atraso) a troca é bloqueada. |
| 5.5 | **Acompanhar entregas** | O professor vê, por turma, quem enviou, quem não enviou e quem enviou com atraso. | Lista filtrável por situação. |
| 5.6 | **Avaliar entrega** | O professor baixa o arquivo, atribui nota e escreve um comentário de retorno. | Nota respeita o máximo definido e fica salva. |
| 5.7 | **Devolutiva ao aluno** | O aluno vê nota e comentário do professor sobre o seu trabalho. | Aluno só vê a devolutiva da sua própria entrega. |
| 5.8 | **Avisos de prazo** | O aluno vê destaque para atividades com prazo próximo ou vencido. | Destaques refletem a data atual. |

### Sprint 6 — Notas, Acompanhamento e Fechamento
*Meta: visão consolidada do desempenho e entrega final pronta para uso real.*

| # | Entrega | Descrição (nível usuário) | Critérios de aceite |
|---|---|---|---|
| 6.1 | **Quadro de notas do professor** | O professor vê, por turma, todas as notas dos alunos em questionários e entregas, com a média. | Quadro bate com as notas lançadas nas atividades. |
| 6.2 | **Minhas notas (aluno)** | O aluno consulta suas notas por matéria. | Mostra apenas as notas do próprio aluno. |
| 6.3 | **Agenda de atividades do aluno** | O aluno vê em um só lugar todas as atividades pendentes, com prazos, de todas as suas matérias. | Lista ordenada por prazo; atividades concluídas saem de "pendentes". |
| 6.4 | **Relatório de participação** | O professor acompanha acessos e participação da turma (quem acessou, quem respondeu, quem entregou). | Relatório por turma e por período. |
| 6.5 | **Exportar notas** | O professor e o administrador exportam notas para planilha. | Arquivo gerado reflete o filtro escolhido. |
| 6.6 | **Visão geral do administrador** | O administrador vê totais de alunos, professores, matérias, turmas e atividade recente. | Números conferem com os cadastros. |
| 6.7 | **Homologação e ajustes finais** | Validação com usuários reais (administrador, professor e aluno) e correção do que for apontado. | Roteiro de testes executado sem pendências críticas. |

---

## 4. Fora do escopo (nesta versão)

- Matrícula/financeiro, emissão de boletim oficial e histórico escolar.
- Aulas ao vivo / videoconferência integradas.
- Fórum, chat e mensagens entre usuários.
- Aplicativo móvel nativo (o sistema é acessível pelo navegador, inclusive no celular).
- Integração com sistemas acadêmicos externos.
- Certificados e gamificação.

## 5. Premissas adotadas (a validar com o cliente)

1. **Existe um perfil Administrador** (secretaria/coordenação) responsável pelos cadastros, pois o enunciado não diz quem cadastra alunos, matérias, turmas e professores.
2. **"Acesso consultivo" do aluno** é entendido como somente leitura sobre o conteúdo; responder questionários e enviar arquivos é a única interação permitida, pois são o objetivo das atividades.
3. **Um aluno pode pertencer a mais de uma turma.**
4. **O professor não é responsável por mais de uma matéria**, e a matéria não muda de responsável sem ação do administrador.
5. **O idioma do sistema é português (Brasil).**
6. Limites de tamanho e tipos de arquivo aceitos serão definidos com o cliente na Sprint 2.

## 6. Pontos em aberto

- O aluno deve poder ver a lista de colegas da turma?
- As notas têm escala própria (0–10) ou configurável por atividade?
- O administrador precisa ver o conteúdo das matérias (somente leitura) para auditoria?
- Haverá notificação por e-mail (novo conteúdo, nota liberada, prazo próximo)?
