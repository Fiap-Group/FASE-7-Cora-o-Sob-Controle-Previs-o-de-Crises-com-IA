# Backend — CardioIA

API em **FastAPI**, organizada em dois pilares dentro de `app/backend/`:

- `src/` — camada HTTP (endpoints, módulos `APIRouter`, injeção de dependência
  via `Depends`). Ponto de entrada: `src/main.py`.
- `shared/` — tudo que é compartilhável entre módulos:
  - `rag_system.py`, `prompts.py`, `glossario.py`, `observabilidade.py` —
    pipeline RAG (busca vetorial + Gemini) que responde perguntas sobre o
    perfil genômico do paciente, reaproveitado de uma fase anterior do curso.
  - `preditivo/` — modelo PyTorch que prevê risco cardíaco a partir de dados
    sintéticos de operação hospitalar.
  - `agentes/` — sistema multiagente (OpenAI Agents SDK + Gemini) que
    orquestra análise de risco, protocolos de resposta e recomendação final.

A arquitetura completa do RAG está em `../../docs/ARQUITETURA_IA.md`.

## Rodar com Docker (recomendado)

```bash
cd app/backend
cp .env.example .env              # preencha GEMINI_API_KEY
docker compose up -d --build
curl http://localhost:5000/api/health
```

## Rodar com venv

```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # preencha GEMINI_API_KEY
python -m src.main
# ou, com reload automático em desenvolvimento:
uvicorn src.main:app --reload --port 5000
```

A API sobe em `http://localhost:5000`, com documentação interativa (Swagger)
em `http://localhost:5000/docs`. Deixe esse processo rodando junto do
`npx expo start --web` do app (são dois processos separados).

## Chave de API

O `/api/index` funciona sem chave: os embeddings rodam localmente com
`sentence-transformers`. O `/api/chat` precisa do Gemini para escrever a
resposta. O multiagente (`shared/agentes/`) também usa Gemini.

- **Gemini** (gratuito, sem cartão): crie a chave em
  https://aistudio.google.com/apikey e coloque em `GEMINI_API_KEY` no `.env`.
- Sem a chave, `/api/chat` responde com erro, e o app mostra essa mensagem ao
  usuário. Isso é esperado.

### Variáveis do `.env`

| Variável | Padrão | Função |
|---|---|---|
| `GEMINI_API_KEY` | — | Chave do Gemini (obrigatória para o chat e os agentes) |
| `LLM_MODEL` | `gemini-3.6-flash` | Modelo usado para gerar as respostas |
| `RAG_TOP_K` | `5` | Quantos trechos do relatório entram no contexto |
| `RAG_MIN_SCORE` | `0.25` | Relevância mínima de um trecho |
| `HOST` | `127.0.0.1` | Endereço de escuta (no Docker é `0.0.0.0`) |
| `PORT` | `5000` | Porta da API |
| `CORS_ORIGINS` | `http://localhost:8081,http://localhost:19006` | Origens do front permitidas, separadas por vírgula |

## Endpoints (módulo RAG — `src/modules/rag/`)

- `GET /api/health`: status da API, se já há paciente indexado, uptime.
- `GET /api/metrics`: contadores e latências (p50 e p95) desde o último start.
- `POST /api/index`: indexa o perfil do paciente, substituindo o índice anterior.
  Corpo: o JSON no formato de `sample_sprint1_output.json`.
- `POST /api/chat`: `{ "question": "..." }` → `{ answer, grounded, sources }`.
- `POST /api/reset`: apaga o índice do paciente da memória do backend.

O módulo preditivo/agentes (`shared/preditivo/`, `shared/agentes/`) ainda é
independente — não está exposto via HTTP; ver seção abaixo.

## Testar com curl

```bash
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d @sample_sprint1_output.json

curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual meu risco de diabetes?"}'
```

## Modelo preditivo e multiagente (`shared/preditivo/`, `shared/agentes/`)

```bash
# Treinar o modelo PyTorch de risco cardíaco (gera shared/preditivo/modelo_risco.pt)
python -m shared.preditivo.treinar

# Demo do sistema multiagente (precisa de GEMINI_API_KEY no .env)
python -m shared.agentes.demo
```

## Testes e checagens

```bash
pip install pytest pyright
bash scripts/ci_local.sh          # testes (sem chamar o Gemini) e checagem de tipos
```

Os testes ficam em `tests/` e não chamam o LLM nem baixam o modelo de
embeddings.

## Arquivos

- `src/main.py`: cria o app FastAPI, registra os módulos (equivalente ao
  `app.ts`/`main.ts` do Nest).
- `src/modules/rag/`: `router.py` (endpoints), `dependencies.py`
  (injeção de dependência), `schemas.py` (validação de request/response).
- `shared/rag_system.py`: pipeline RAG (chunking do JSON genômico, embeddings,
  busca vetorial e geração da resposta).
- `shared/prompts.py` e `shared/glossario.py`: prompt para leigos e traduções
  de termos técnicos.
- `shared/observabilidade.py`: logs em JSON (`shared/logs/app.log`) e métricas
  em memória.
- `shared/preditivo/`: dataset sintético, rede neural PyTorch e protocolos de
  resposta do modelo de risco cardíaco.
- `shared/agentes/`: schemas Pydantic, configuração do Gemini e os 4 agentes
  (Orquestrador → Analista de Risco → Especialista em Protocolos →
  Planejador de Resposta).
- `scripts/`: checagens locais (`ci_local.sh`).
- `tests/`: testes automatizados.
- `sample_sprint1_output.json`: exemplo de relatório genômico.
