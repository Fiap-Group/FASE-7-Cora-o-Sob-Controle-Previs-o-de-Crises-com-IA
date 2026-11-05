# Backend RAG — Genera Intelligence

API que responde perguntas sobre o perfil genômico do paciente usando RAG
(busca vetorial + Gemini). Consumida pelo app (telas Ancestralidade, Riscos,
Dashboard e Chat). A arquitetura completa está em `../../docs/ARQUITETURA_IA.md`.

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
python -m src.api
```

A API sobe em `http://localhost:5000`. Deixe esse processo rodando junto do
`npx expo start --web` do app (são dois processos separados).

## Chave de API

O `/api/index` funciona sem chave: os embeddings rodam localmente com
`sentence-transformers`. O `/api/chat` precisa do Gemini para escrever a
resposta.

- **Gemini** (gratuito, sem cartão): crie a chave em
  https://aistudio.google.com/apikey e coloque em `GEMINI_API_KEY` no `.env`.
- Sem a chave, `/api/chat` responde com erro, e o app mostra essa mensagem ao
  usuário. Isso é esperado.

### Variáveis do `.env`

| Variável | Padrão | Função |
|---|---|---|
| `GEMINI_API_KEY` | — | Chave do Gemini (obrigatória para o chat) |
| `LLM_MODEL` | `gemini-3.6-flash` | Modelo usado para gerar as respostas |
| `RAG_TOP_K` | `5` | Quantos trechos do relatório entram no contexto |
| `RAG_MIN_SCORE` | `0.25` | Relevância mínima de um trecho |
| `HOST` | `127.0.0.1` | Endereço de escuta (no Docker é `0.0.0.0`) |
| `PORT` | `5000` | Porta da API |
| `FLASK_DEBUG` | `0` | `1` ativa o modo debug (não usar em apresentação) |
| `CORS_ORIGINS` | `http://localhost:8081,http://localhost:19006` | Origens do front permitidas, separadas por vírgula |

## Endpoints

- `GET /api/health`: status da API, se já há paciente indexado, uptime.
- `GET /api/metrics`: contadores e latências (p50 e p95) desde o último start.
- `POST /api/index`: indexa o perfil do paciente, substituindo o índice anterior.
  Corpo: o JSON no formato da Sprint 1 (veja `sample_sprint1_output.json`).
- `POST /api/chat`: `{ "question": "..." }` → `{ answer, grounded, sources }`.
- `POST /api/reset`: apaga o índice do paciente da memória do backend.

## Testar com curl

```bash
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d @sample_sprint1_output.json

curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual meu risco de diabetes?"}'
```

## Testes e checagens

```bash
pip install pytest pyright
bash scripts/ci_local.sh          # testes (sem chamar o Gemini) e checagem de tipos
```

Os testes ficam em `tests/` e não chamam o LLM nem baixam o modelo de
embeddings. A avaliação das respostas com o Gemini é separada:
`python avaliacao/avaliar.py --com-llm --limite 10` (consome a cota diária).

## Arquivos

- `api.py`: API Flask que expõe o pipeline para o app.
- `rag_system.py`: pipeline RAG (chunking do JSON genômico, embeddings, busca
  vetorial e geração da resposta).
- `prompts.py` e `glossario.py`: prompt para leigos e traduções de termos técnicos.
- `observabilidade.py`: logs em JSON (`logs/app.log`) e métricas em memória.
- `avaliacao/`: gabarito, avaliação do modelo e validação das respostas.
- `scripts/`: rotina de operação e checagens locais (`ci_local.sh`).
- `tests/`: testes automatizados.
- `sample_sprint1_output.json`: exemplo de relatório genômico.
