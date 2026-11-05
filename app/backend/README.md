# Backend — CardioIA

API em **FastAPI**, organizada por módulo (`src/modules/<nome>/`: `router.py`
+ `dependencies.py` + `schemas.py`, cada um um `APIRouter` registrado em
`src/main.py`) e uma camada `shared/` com o que não é HTTP.

## Lógica de negócio, por módulo

- **`rag`** — pipeline RAG (busca vetorial + Gemini) herdado de uma fase
  anterior: o paciente envia o relatório genômico, o backend indexa (chunking
  + embeddings) e responde perguntas sobre ele em linguagem simples, citando
  as fontes e nunca inventando dado clínico fora do relatório. Pseudonimiza
  antes de mandar pro LLM e não loga o texto da pergunta nem do relatório
  (`shared/observabilidade.py`).
- **`risco`** — o core da Fase 7: recebe 10 métricas de operação hospitalar
  (`POST /api/risco/avaliar`) e roda a cadeia de 4 agentes
  (`shared/agentes/`: Orquestrador → Analista de Risco → Especialista em
  Protocolos → Planejador de Resposta) que prevê o risco de crise cardíaca
  (modelo PyTorch, `shared/preditivo/`) e recomenda os protocolos de resposta
  aplicáveis. Também assina o tópico MQTT do ESP32 (`iot/esp32/`) e guarda a
  última leitura em memória (`GET /api/risco/leitura-iot`) — o ESP32 publica
  a cada 2s, então a avaliação continua manual (senão a cota gratuita do
  Gemini estoura em menos de um minuto).
- **`auth`** — conta de usuário (e-mail + senha com hash, depois escolhe um
  nickname), a única coisa compartilhada entre os dois front-ends
  (mobile e web) que por isso não pode viver em SQLite local de cada
  aparelho: fica no Postgres (`shared/db.py`, `shared/models.py`). Sem
  token/sessão — o front manda o `usuario_id` direto no corpo da
  requisição; suficiente pro que o enunciado pede, não é um auth de
  produção.
- **`perfil`** — a "ficha de jogador": toda vez que `risco/avaliar` termina
  com sucesso e veio um `usuario_id`, grava uma linha em `historico_risco`
  (10 features + risco + protocolos + recomendação). `GET
  /api/perfil/{usuario_id}` devolve a conta + a avaliação mais recente em
  destaque + as últimas 10 do histórico — consumido pela aba "Perfil" do
  mobile e do web.

## Rodar com Docker (recomendado)

```bash
cd app/backend
cp .env.example .env   # preencha GEMINI_API_KEY e POSTGRES_PASSWORD
docker compose up -d --build
curl http://localhost:5000/api/health
```

Sobe dois serviços: `db` (Postgres 16) e `backend`. O volume do Postgres é
nomeado (`postgres_data`), então os dados sobrevivem a `docker compose down`
(sem `-v`) e a reinícios do container.

## Rodar com venv

```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # preencha GEMINI_API_KEY e POSTGRES_PASSWORD
docker compose up -d db          # só o Postgres, publicado em localhost:5432
python -m src.main
# ou, com reload automático em desenvolvimento:
uvicorn src.main:app --reload --port 5000
```

A API sobe em `http://localhost:5000`, com Swagger em
`http://localhost:5000/docs`.

## Chave de API e variáveis do `.env`

- **Gemini** (gratuito, sem cartão): https://aistudio.google.com/apikey →
  `GEMINI_API_KEY`. Usado por `/api/chat` (RAG) e por `/api/risco/avaliar`
  (os 4 agentes). Sem a chave, essas rotas respondem com erro — esperado.
- **Postgres**: só precisa de `POSTGRES_PASSWORD` (o resto já tem padrão).
  `DATABASE_URL` aponta pra `localhost` fora do Docker; dentro do
  `docker-compose`, o serviço `backend` sobrescreve pra `db` automaticamente.
- **MQTT**: opcional — só necessário se o ESP32 (ou o simulador Wokwi)
  estiver publicando de verdade. Sem isso, `leitura-iot` sempre devolve
  `conectado: false`.

| Variável | Padrão | Função |
|---|---|---|
| `GEMINI_API_KEY` | — | Chave do Gemini (RAG e multiagente) |
| `LLM_MODEL` | `gemini-3.6-flash` | Modelo usado para gerar as respostas |
| `RAG_TOP_K` / `RAG_MIN_SCORE` | `5` / `0.25` | Retrieval do RAG |
| `MQTT_SERVER`/`MQTT_PORT`/`MQTT_USER`/`MQTT_PASSWORD`/`MQTT_TOPIC` | — | Broker do ESP32 (mesmo do `iot/esp32/secrets.py`) |
| `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` | `cardioia`/—/`cardioia` | Credenciais do serviço `db` |
| `DATABASE_URL` | `postgresql+psycopg2://...@localhost:5432/cardioia` | Sobrescrito para `@db:...` dentro do Docker |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Endereço de escuta (Docker usa `0.0.0.0`) |
| `CORS_ORIGINS` | `http://localhost:8081,http://localhost:19006,http://localhost:5173` | Origens permitidas — em produção, inclua as URLs do mobile/web publicados |

## Endpoints

| Módulo | Rota | O que faz |
|---|---|---|
| `rag` | `GET /api/health` | status, se há paciente indexado, uptime |
| `rag` | `GET /api/metrics` | contadores e latência (p50/p95) desde o último start |
| `rag` | `POST /api/index` | indexa o relatório genômico (substitui o índice anterior) |
| `rag` | `POST /api/chat` | `{question}` → `{answer, grounded, sources}` |
| `rag` | `POST /api/reset` | apaga o índice em memória |
| `risco` | `POST /api/risco/avaliar` | 10 métricas → risco + protocolos + recomendação (grava histórico se vier `usuario_id`) |
| `risco` | `GET /api/risco/leitura-iot` | última leitura MQTT do ESP32 |
| `auth` | `POST /api/auth/cadastro` | cria a conta (e-mail + senha) |
| `auth` | `POST /api/auth/login` | autentica |
| `auth` | `POST /api/auth/nickname` | define o nickname |
| `perfil` | `GET /api/perfil/{usuario_id}` | conta + avaliação mais recente + histórico |

## Testar com curl

```bash
curl -X POST http://localhost:5000/api/risco/avaliar \
  -H "Content-Type: application/json" \
  -d '{"idade_media":60,"carga_sistema":90,"tempo_espera":100,"fc_media":125,"spo2_media":85,"pa_sistolica":85,"temperatura":39,"densidade_eventos":7,"eventos_24h":6,"disponibilidade_recursos":20}'
```

## Treinar o modelo / demo do multiagente

```bash
python -m shared.preditivo.treinar   # gera shared/preditivo/modelo_risco.pt
python -m shared.agentes.demo        # precisa de GEMINI_API_KEY
```

## Testes e checagens

```bash
pip install pytest pyright
bash scripts/ci_local.sh
```

Uma única suíte (`pytest tests/`), dividida em `tests/unitarios/` (modelo
preditivo e wiring dos agentes — sem HTTP, sem banco) e `tests/integracao/`
(endpoints FastAPI via `TestClient`, Postgres substituído por SQLite em
memória). Não chama o LLM de verdade.

## Deploy

**Ainda em aberto** onde o backend vai ficar publicamente acessível (ex.:
túnel via ngrok/cloudflared, ou um VPS rodando o `docker-compose.yml` como
está). Qualquer que seja a opção: publique a porta 5000, aponte
`CORS_ORIGINS` para as URLs de produção do mobile e do web, e troque
`EXPO_PUBLIC_API_URL` (`app/mobile/eas.json`) e `VITE_API_URL` (painel da
Vercel) pra URL final.

## Arquivos

- `src/main.py`: cria o app FastAPI, registra os 4 módulos, garante as
  tabelas do Postgres no startup (`Base.metadata.create_all`).
- `src/modules/{rag,risco,auth,perfil}/`: `router.py` + `dependencies.py` +
  `schemas.py` (e `service.py` onde a lógica não é só HTTP).
- `shared/db.py`, `shared/models.py`: sessão do Postgres (SQLAlchemy) e os
  modelos `Usuario`/`HistoricoRisco`.
- `shared/rag_system.py`, `prompts.py`, `glossario.py`: pipeline RAG.
- `shared/observabilidade.py`: logs em JSON (`shared/logs/app.log`) e
  métricas em memória.
- `shared/preditivo/`: dataset sintético, rede PyTorch e protocolos de
  resposta.
- `shared/agentes/`: schemas Pydantic e os 4 agentes (OpenAI Agents SDK +
  Gemini).
- `scripts/ci_local.sh`: mesmas checagens do CI, local.
- `tests/`: `unitarios/` + `integracao/`.
- `sample_sprint1_output.json`: exemplo de relatório genômico.
