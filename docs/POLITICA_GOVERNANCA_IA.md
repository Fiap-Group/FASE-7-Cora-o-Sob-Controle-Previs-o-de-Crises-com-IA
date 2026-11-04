# Política de Governança de IA — Genera Intelligence (Dasa/Genera)

Este documento define como a solução trata dados pessoais e de saúde, como
registra eventos da operação e como sustenta a explicabilidade das respostas
do agente. Complementa `GOVERNANCA_E_RISCOS.md` (limites do agente e riscos)
e `ARQUITETURA_IA.md` (como o sistema funciona).

## 1. Escopo e papéis

- **Finalidade:** explicar, em linguagem simples, o relatório genético que o
  próprio paciente enviou, e apoiar o entendimento de riscos e recomendações
  já constantes desse relatório.
- **Não é finalidade:** diagnóstico, prescrição, decisão clínica ou
  substituição de consulta médica.
- **Controlador dos dados:** o próprio paciente, no dispositivo dele.
- **Operador (terceiro):** Google, via API Gemini, apenas no momento da
  geração da resposta. Os termos e a política de privacidade do provedor
  regem esse tratamento: https://ai.google.dev/gemini-api/terms

## 2. Princípios da LGPD aplicados

| Princípio | Como a solução aplica |
|---|---|
| **Finalidade** | Os dados são usados só para responder perguntas sobre o relatório do próprio paciente. O agente recusa outros temas (ver `prompts.py`, seção de limites). |
| **Adequação e base legal** | Dado de saúde é dado sensível (LGPD, Art. 11). A base adotada é o **consentimento específico e destacado**, pedido antes do primeiro envio do relatório (`ProfileScreen.js`). |
| **Necessidade (minimização)** | Antes de ir ao modelo, o nome e a data de nascimento são removidos do texto. Também saem o ID e os campos de documento, contato e endereço, se existirem (`rag_system.py`, `CAMPOS_IDENTIFICADORES`). Testes em `tests/test_sprint4.py` verificam isso. |
| **Livre acesso e transparência** | A pessoa vê as fontes de cada resposta (seção e trecho do relatório) em "Fontes consultadas no seu relatório". |
| **Segurança** | Logs sem texto das perguntas (ver seção 4). Backend escuta só em `127.0.0.1` por padrão. Erros internos não são devolvidos ao cliente. Chaves ficam no `.env`, fora do repositório. |
| **Prevenção** | Disclaimer de natureza informativa anexado por código a toda resposta. |
| **Eliminação** | Botão "Apagar meus dados" (ver seção 3). |
| **Não discriminação** | O agente trata riscos como fator, não destino, e não emite juízo sobre a pessoa. |
| **Responsabilização** | Logs estruturados e métricas (seção 4) permitem rastrear o comportamento do sistema. |

## 3. Ciclo de vida dos dados

**Onde cada dado fica:**

| Dado | Onde fica | Quanto tempo |
|---|---|---|
| Relatório genético (JSON) | SQLite no dispositivo (`perfil_genomico`) | Até o paciente apagar |
| Histórico de conversa e resumos | SQLite no dispositivo | Até o paciente apagar |
| Registro de consentimento | SQLite no dispositivo (`consentimento`) | Até o paciente apagar |
| Índice vetorial do relatório | Memória do backend | Até reiniciar o backend ou apagar os dados |
| Texto enviado ao Gemini | Só durante a requisição, sem nome nem data de nascimento | Conforme os termos do provedor |
| Logs do backend | `app/backend/logs/app.log`, com rotação | Rotação de 5 MB, 3 arquivos |

**Eliminação ("Apagar meus dados"):** remove, no dispositivo, todas as
tabelas de dados pessoais, incluindo o consentimento, em uma única transação.
Também chama `POST /api/reset`, que apaga o índice da memória do backend.
Se o backend estiver fora do ar, os dados do dispositivo são apagados mesmo
assim.

**Revogação:** apagar os dados também revoga o consentimento. Um novo envio
pede autorização de novo.

## 4. Logging e rastreabilidade

O backend registra eventos em JSON, um por linha (`app/backend/observabilidade.py`):

| Evento | Campos registrados | Campos **não** registrados |
|---|---|---|
| Indexação de relatório | número de trechos | conteúdo do relatório |
| Pergunta respondida | hash curto da pergunta, tamanho, seções recuperadas, `grounded`, latência | **texto da pergunta** |
| Retry de LLM e cota esgotada | tipo do erro e tentativa | conteúdo da pergunta |
| Erro interno | tipo da exceção, rastreamento no servidor | — (não é devolvido ao cliente) |
| Reset do índice | — | — |

**Por que o hash e não a pergunta:** a pergunta pode conter dados de saúde
ou identificação. O hash permite correlacionar eventos (ex.: a mesma pergunta
falhando repetidamente) sem guardar o texto. Métricas agregadas ficam em
`GET /api/metrics`: contadores, latências p50/p95 e último erro.

## 5. Explicabilidade

A explicabilidade é tratada em três níveis:

1. **Fontes:** cada resposta devolve os trechos do relatório usados, com seção
   e relevância. A interface mostra esses trechos em "Fontes consultadas no
   seu relatório". As fontes ficam na sessão atual e não são gravadas no
   histórico.
2. **Ancoragem:** a flag `grounded` indica se a resposta reaproveita termos
   do contexto recuperado. É uma heurística de sobreposição de termos, não uma
   verificação factual. Respostas com `grounded: false` devem ser lidas com
   cautela, e a avaliação (`docs/AVALIACAO_MODELO.md`) reporta essa taxa.
3. **Regras explícitas:** o prompt de sistema (`app/backend/prompts.py`) define
   o formato, o público-alvo e os limites do agente. Essas regras estão
   versionadas no repositório, o que permite auditar qualquer mudança de
   comportamento.

**Limite conhecido:** a explicação das fontes mostra *onde* a resposta foi
buscada, não *como* o modelo chegou à conclusão. Isso é uma limitação dos LLMs
e está documentada.

## 6. Qualidade e validação das respostas

Cada resposta passa por checagens automáticas (`app/backend/avaliacao/validacao.py`):

- tamanho máximo de 130 palavras (sem o disclaimer);
- frases de média até 20 palavras;
- números citados presentes no contexto (evita dado inventado);
- termos técnicos sem explicação entre parênteses;
- linguagem prescritiva (sinal para revisão humana).

Os resultados da avaliação e as limitações estão em `docs/AVALIACAO_MODELO.md`.

## 7. Responsabilidades e revisão

- **Revisão desta política:** a cada nova versão do modelo, do provedor ou da
  base de conhecimento, ou quando surgir um incidente.
- **Incidentes:** resposta incorreta ou potencialmente prejudicial deve ser
  registrada, com a pergunta reproduzida fora do log. Depois, o gabarito de
  avaliação deve ganhar o caso.
- **Dados de terceiros:** o app não aceita dados de outras pessoas. Se o
  relatório pertencer a outra pessoa, o usuário deve apagar os dados e não
  usar o sistema.

## 8. Pendências declaradas

- O consentimento é um aceite único, sem histórico de versões dos termos.
- Não há autenticação de usuário: qualquer pessoa com acesso ao dispositivo
  e ao backend pode consultar o relatório.
- A pseudonimização remove identificadores diretos, mas o relatório ainda
  pode ser identificável pelas características genéticas. Isso é inerente ao
  tipo de dado.
- Em produção, seria necessário um DPA com o provedor de LLM e uma avaliação
  de impacto à proteção de dados (RIPD).
