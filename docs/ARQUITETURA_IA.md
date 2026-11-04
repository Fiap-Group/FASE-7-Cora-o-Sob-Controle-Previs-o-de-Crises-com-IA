# Arquitetura de IA — Genera Intelligence

Documento técnico da inteligência do sistema: pipeline RAG (`app/backend/rag_system.py`),
API que o expõe (`app/backend/api.py`) e como o front-end consome tudo isso.

## Visão geral do fluxo

```
Usuário (app) → preenche/envia relatório genômico
    ↓
POST /api/index → GenomicChunker → TextCleaner → EmbeddingEngine → VectorStore
    ↓ (uma vez por relatório enviado)
Usuário → faz uma pergunta no chat
    ↓
POST /api/chat → Retriever (busca vetorial) → Context Builder → LLMGenerator → resposta
    ↓
App salva a resposta no SQLite local e exibe no chat
```

## Escolha do LLM

O `LLMGenerator` (`rag_system.py`) suporta três provedores, selecionáveis por
variável de ambiente (`LLM_BACKEND` em `app/backend/.env`), sem mudar código:

| Backend | Modelo padrão | Por que |
|---|---|---|
| **Gemini** (padrão/recomendado) | `gemini-3.6-flash` | Tier gratuito sem cartão de crédito — viável pra um projeto de curso sem custo recorrente. Qualidade de resposta boa em PT-BR. |
| Anthropic | `claude-sonnet-4-...` | Pago, mas resposta mais consistente/qualidade mais alta — opção pra quem já tem créditos. |
| OpenAI | `gpt-4o-mini` | Pago, alternativa equivalente ao Anthropic. |

**Trade-off aceito conscientemente**: o tier gratuito do Gemini tem cota
diária baixa (ex: 20 requisições/dia observadas no modelo usado). Para lidar
com isso sem quebrar a experiência:

- **Erros passageiros** (503 "sobrecarregado") → o `LLMGenerator.generate()`
  tenta de novo automaticamente, com backoff (1s, 2s), até 3 tentativas.
- **Cota esgotada** (429 "quota exceeded") → falha imediatamente com uma
  mensagem clara pro usuário, em vez de insistir à toa (a API pede dezenas
  de segundos de espera, incompatível com uma resposta interativa de chat).

Essa lógica está isolada em `LLMGenerator.generate()`, `_erro_e_transitorio()`
e `_erro_e_cota_esgotada()`, e vale pros três backends.

## Técnica de embeddings

- **Modelo**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
  (`EmbeddingEngine` em `rag_system.py`), rodando **localmente** (sem API,
  sem custo) — só a geração da resposta final depende de um LLM externo.
- **Por quê esse modelo**: suporte nativo a português, sem precisar de
  tradução ou pós-processamento.
- **Normalização**: embeddings L2-normalizados, permitindo usar produto
  interno como equivalente a similaridade de cosseno (mais rápido).
- **Execução forçada em CPU** (`device="cpu"`): evita falhas de
  compatibilidade CUDA em máquinas sem GPU configurada corretamente — o
  volume de dados deste projeto (dezenas de chunks por paciente) não
  justifica o custo de configurar GPU.
- Suporta também embeddings via API OpenAI (`text-embedding-3-small`) como
  alternativa, configurável por `EMBEDDING_BACKEND`.

## Estrutura de recuperação de dados (retrieval)

### Chunking — `GenomicChunker`

O JSON genômico do paciente (formato definido na Sprint 1) é dividido em
chunks por **domínio semântico**, não por tamanho fixo de texto — cada
chunk é uma unidade de informação compreensível sozinha:

- 1 chunk de perfil básico do paciente
- 1 chunk por região de ancestralidade
- 1 chunk por doença/risco genético
- 1 chunk por item de bem-estar/farmacogenômica
- 1 chunk por recomendação clínica

Essa granularidade favorece recuperação precisa: uma pergunta como "qual
meu risco de diabetes?" recupera exatamente o chunk daquela doença, sem
misturar informação de outras seções.

### Vector store — `VectorStore`

FAISS (`IndexFlatIP`, busca exata por produto interno) com fallback
automático para NumPy puro se o FAISS não estiver instalado — mesma
interface, resultado idêntico, só muda a performance (relevante em bases
muito maiores; neste projeto, com um paciente por vez, a diferença é
irrelevante).

### Retriever

- **Top-k = 5**: recupera os 5 chunks mais similares à pergunta.
- **Score mínimo = 0,25**: descarta chunks pouco relevantes; se nada passar
  do limiar, usa o melhor resultado como fallback (evita responder "não sei"
  quando existe alguma informação próxima).
- **Context Builder**: formata os chunks recuperados com seção e score de
  relevância, delimitados, antes de injetar no prompt do LLM — isso reduz
  alucinação porque o modelo enxerga claramente onde termina um trecho e
  começa outro.

### Anti-alucinação (3 camadas, ver `docs/GOVERNANCA_E_RISCOS.md` para a
discussão de riscos)

1. **Prompt de sistema** (`app/backend/prompts.py`) instrui o modelo a
   responder só com base no contexto fornecido.
2. **Score mínimo** no retrieval descarta contexto irrelevante antes mesmo
   de chegar no LLM.
3. **Grounding check** heurístico pós-geração (`_check_grounding`): verifica
   se pelo menos 30% dos termos significativos da resposta aparecem no
   contexto recuperado; o resultado (`grounded: true/false`) é devolvido pra
   API e poderia ser usado no front-end pra sinalizar respostas menos
   confiáveis.

## Engenharia de prompts

- `app/backend/prompts.py` — prompt de sistema do agente de chat
  (`SYSTEM_PROMPT_RAG`), separado da lógica do pipeline. Na Sprint 4 foi
  reescrito para o paciente leigo: respostas de até 120 palavras, ordem fixa
  (resposta direta → o que significa → o que fazer) e linguagem sem jargão.
- `app/backend/glossario.py` — termos técnicos com explicação pronta em
  linguagem simples (ex.: alelo, haplogrupo, MTHFR). O glossário é injetado no
  prompt, para que o modelo use as traduções já escritas, em vez de criar uma
  explicação diferente a cada resposta.
- `app/src/services/resumoService.js` — prompt fixo usado para gerar os
  resumos automáticos (`PROMPT_RESUMO`), no front-end, reaproveitando o
  mesmo endpoint `/api/chat`.

## Operação, avaliação e validação (Sprint 4)

- **Índice por relatório:** cada `POST /api/index` substitui o índice anterior
  (`VectorStore.reset()` em `GenomicRAGPipeline.index_patient`). Antes, os
  relatórios se acumulavam e a busca podia misturar pacientes.
- **Logs estruturados:** `observabilidade.py` grava eventos em JSON em
  `app/backend/logs/app.log`, com rotação. O texto das perguntas não entra no
  log: registram-se um hash, o tamanho, as seções recuperadas e a latência.
- **Métricas:** `GET /api/metrics` devolve contadores (perguntas, erros,
  respostas sem ancoragem, resets) e latências p50/p95 desde o último start.
- **Avaliação do modelo:** `avaliacao/avaliar.py` mede a recuperação contra o
  gabarito de 28 perguntas (`avaliacao/gabarito.json`). Com `--com-llm`, também
  avalia as respostas, respeitando a cota diária. Resultados em
  `docs/AVALIACAO_MODELO.md`.
- **Validação automática das respostas:** `avaliacao/validacao.py` checa
  tamanho, clareza (frases curtas), números que não estão no contexto, termos
  técnicos sem tradução e linguagem prescritiva.
- **Rotina de operação:** `scripts/rotina_operacao.py` roda os testes, a
  avaliação de recuperação e a checagem de saúde, e grava o resultado em
  `logs/rotina_operacao.json`. Pode ser agendada.
- **Pseudonimização antes do LLM:** `GenomicChunker._chunk_patient_profile`
  remove identificadores diretos do texto enviado ao modelo (`CAMPOS_IDENTIFICADORES`).

## Pipeline de NLP (limpeza de texto)

`TextCleaner` (`rag_system.py`) normaliza o texto antes de gerar embeddings:
normalização Unicode (NFC), remoção de caracteres de controle, normalização
de espaços/pontuação, padronização de listas, e expansão de siglas genômicas
comuns (SNP, VUS, LD, GWAS, PRS, OR) para termos por extenso — melhora a
qualidade do embedding para buscas em português.
