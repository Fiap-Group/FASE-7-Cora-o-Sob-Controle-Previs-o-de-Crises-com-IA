# Governança e Riscos — Genera Intelligence

Documento sobre os limites conhecidos do agente, os disclaimers aplicados e
a política de privacidade dos dados genéticos manipulados pelo sistema.

## Delimitação técnica e documental dos limites do agente

O escopo do agente é restrito em duas camadas independentes, pra que ele não
execute nada fora do documentado mesmo diante de tentativa de manipulação
via prompt do usuário:

1. **Técnica (prompt de sistema)** — `app/backend/prompts.py`,
   `SYSTEM_PROMPT_RAG`, seção "LIMITES DO AGENTE": instrui explicitamente o
   modelo a **não** prescrever medicamento/dosagem/tratamento, **não** emitir
   diagnóstico, **não** executar ou orientar qualquer procedimento fora de
   responder perguntas sobre o relatório carregado, **não** assumir outra
   persona nem revelar/alterar o próprio prompt de sistema — mesmo se o
   usuário pedir diretamente. Perguntas fora do escopo de saúde/perfil
   genético devem ser recusadas educadamente, não respondidas mesmo assim.
2. **Documental (este arquivo + `docs/ARQUITETURA_IA.md`)** — descreve por
   escrito o que o agente **é** (um assistente de leitura/interpretação de
   um relatório genômico já carregado, via RAG) e o que ele **não é** (não
   diagnostica, não prescreve, não substitui atendimento clínico), servindo
   de referência auditável independente do comportamento do modelo em
   tempo de execução.

Como instrução de prompt sozinha não é garantia absoluta de comportamento
do modelo, a camada técnica é reforçada por um controle **fora do LLM** — o
disclaimer obrigatório descrito a seguir é anexado por código, não depende
do modelo lembrar de incluir.

## Limites conhecidos do agente

- **Não é diagnóstico médico.** O agente interpreta associações estatísticas
  populacionais presentes no relatório genômico (ex: "risco 3,5x maior que a
  média"), não faz diagnóstico nem previsão determinística individual.
- **Risco de alucinação não é zero.** Mitigado por três camadas (prompt
  restritivo, filtro de relevância no retrieval, heurística de grounding
  pós-geração — ver `docs/ARQUITETURA_IA.md`), mas nenhuma delas garante
  100% de precisão. A heurística de grounding é um score de sobreposição de
  termos, não uma verificação factual rigorosa.
- **Disponibilidade depende do provedor de LLM.** No plano gratuito
  (Gemini), há cota diária de uso; ao esgotar, o agente fica indisponível
  para gerar novas respostas até o reset da cota ou troca de provedor — a
  indexação do relatório (busca vetorial) continua funcionando normalmente,
  só a geração da resposta final é afetada.
- **Qualidade depende dos dados de entrada.** O sistema responde só com base
  no que está no relatório enviado; um relatório incompleto ou mal
  preenchido gera respostas igualmente limitadas.
- **Sem verificação de identidade.** Qualquer pessoa com acesso ao
  dispositivo/app pode enviar um relatório e conversar com o agente — não há
  autenticação de usuário nesta versão do projeto (adequado para um MVP de
  curso; um sistema em produção precisaria disso).

## Disclaimers aplicados

- **Obrigatório em toda resposta do chat**: `GenomicRAGPipeline.answer()`
  (`app/backend/rag_system.py`) anexa por código o texto de
  `DISCLAIMER_RESPOSTA` (`app/backend/prompts.py`) ao final de **toda**
  resposta gerada pelo agente — chat e resumos automáticos, já que ambos
  passam pelo mesmo `/api/chat`. É um controle determinístico, fora do LLM:
  não depende do modelo optar por incluir o aviso, ele é concatenado depois
  da geração, sempre. O texto deixa claro que a resposta é **informativa**
  e **não constitui diagnóstico médico**.
- Componente `Disclaimer` (`app/src/components/Disclaimer.js`) exibido nas
  telas **Dashboard** e **Riscos**, lembrando que as informações são
  interpretações do relatório genético e não substituem avaliação médica.
- O próprio **prompt de sistema** do agente (`app/backend/prompts.py`) instrui
  o modelo a: contextualizar risco genético como fator e não destino,
  sugerir consulta a especialista quando pertinente, e admitir explicitamente
  quando não tem a informação, em vez de inventar.
- Mensagens de erro do app (backend fora do ar, cota esgotada, chave ausente)
  são sempre explicadas ao usuário — nunca falham silenciosamente — para que
  ele não confunda uma indisponibilidade técnica com "não há risco".

## Privacidade dos dados genéticos

**O que é armazenado, e onde:**

- O relatório genômico enviado pelo usuário, o histórico de mensagens do
  chat e os resumos gerados ficam salvos **somente no dispositivo do
  usuário**, em SQLite local (`app/src/db/database.js`, via `expo-sqlite`).
  Não existe banco de dados remoto próprio do projeto — não há um servidor
  nosso guardando esses dados.
- O usuário tem controle direto sobre os próprios dados: pode excluir
  qualquer resumo (e a conversa associada) a qualquer momento pelo ícone de
  lixeira na tela de Resumos, sem depender de suporte técnico.

**O que sai do dispositivo, e para onde:**

- Ao indexar um relatório (`POST /api/index`) e ao fazer uma pergunta
  (`POST /api/chat`), os dados do relatório e/ou os trechos recuperados
  trafegam até o **backend Flask local** (`app/backend/api.py`) e, na etapa
  de geração da resposta, até a **API do provedor de LLM configurado**
  (Gemini/Anthropic/OpenAI, conforme a chave usada) — esse é dado de saúde
  sensível saindo para um serviço de terceiro, e isso deve ser tratado como
  tal:
  - O uso de cada provedor é regido pela **política de privacidade e termos
    do próprio provedor** (Google/Anthropic/OpenAI); este projeto não tem
    controle sobre como esses dados são retidos ou processados do lado deles.
  - Nenhum dado é enviado para nenhum outro terceiro além do provedor de LLM
    escolhido.

**Já implementado na Sprint 4** (detalhes em `POLITICA_GOVERNANCA_IA.md`):

- Pseudonimização antes de chamar o LLM: nome, data de nascimento, ID e
  campos de documento, contato e endereço saem do texto do prompt.
- Consentimento explícito antes do primeiro envio de relatório (Art. 11).
- Botão "apagar meus dados", que remove os registros do dispositivo e o índice
  do backend.
- Logs sem texto das perguntas.

**Ainda fora do escopo deste MVP (recomendações para uma versão em produção):**

- Avaliar um provedor com garantias contratuais de não retenção/treinamento
  sobre os dados enviados (ex: acordos de processamento de dados/DPA), ou
  hospedar um modelo próprio (self-hosted) para eliminar o terceiro.
- Criptografia em repouso do banco local, já que se trata de dado de saúde.
- Autenticação de usuário e controle de acesso ao dispositivo/app.
- Relatório de impacto à proteção de dados (RIPD), exigido para dado sensível.
