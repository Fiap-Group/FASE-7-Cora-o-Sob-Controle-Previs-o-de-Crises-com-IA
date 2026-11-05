# FIAP - Faculdade de Informática e Administração Paulista

# CardioIA — Fase 7: Coração Sob Controle — Previsão de Crises com IA

## Nome do grupo

41

## 👨‍🎓 Integrantes:

- Guilherme Campos Hermanowski
- Fatima Candal
- Matheus Alboredo Soares
- Jonathan Willian Luft
- Ana Belchior

### Tutor

CaiqueFiap-2026

## 📜 Descrição

Entrega final do curso: uma plataforma de previsão de crise cardíaca a
partir de dados de operação hospitalar, com um app mobile e um web
consumindo o mesmo backend, mais a simulação de um sensor IoT (ESP32). Três
peças de IA compõem o backend:

- **RAG genômico** — infraestrutura herdada de uma fase anterior: o
  paciente envia o relatório genético e conversa com um agente de IA sobre
  ele, em linguagem simples, com as fontes à vista e aviso de que a
  resposta é informativa, não um diagnóstico. Só no app mobile.
- **Modelo preditivo de risco cardíaco** (PyTorch) + **sistema
  multiagente** (OpenAI Agents SDK + Gemini, 4 agentes: Orquestrador →
  Analista de Risco → Especialista em Protocolos → Planejador de
  Resposta) — expostos como `POST /api/risco/avaliar`, consumidos tanto
  pelo mobile quanto pelo web.
- **Conta de usuário + Perfil gamificado** — login compartilhado entre os
  dois front-ends (Postgres no backend) e um histórico de avaliações por
  usuário, exibido como "ficha de jogador" (avatar, risco em destaque,
  histórico).

Detalhes de lógica de negócio, endpoints e como rodar cada parte estão no
README de cada pasta: [`app/backend/README.md`](app/backend/README.md),
[`app/mobile/README.md`](app/mobile/README.md),
[`app/web/README.md`](app/web/README.md).

## 📁 Estrutura do projeto

```
.github/workflows/ci.yml          # CI: testes (unitários + integração) + checagem de tipos a cada push

iot/esp32/                        # Simulação Wokwi (MicroPython): lê o sensor e publica via MQTT
  main.py, diagram.json, secrets.py

app/
  mobile/                         # App React Native/Expo — ver app/mobile/README.md
    src/                          # screens, components, db (SQLite), services
    app.json, eas.json            # Config do build .apk (EAS Build)

  web/                            # App React+Vite — ver app/web/README.md
    src/                          # App.jsx, Dashboard.jsx, Perfil.jsx, api.js
    vercel.json                   # Rotas SPA (deploy na Vercel)

  backend/                        # Backend (FastAPI) — ver app/backend/README.md
    src/modules/{rag,risco,auth,perfil}/   # Endpoints por módulo
    shared/                       # Compartilhável entre módulos
      rag_system.py, prompts.py, glossario.py, observabilidade.py
      preditivo/                  # Modelo PyTorch de risco cardíaco
      agentes/                    # Sistema multiagente (OpenAI Agents SDK + Gemini)
      db.py, models.py            # Postgres/SQLAlchemy (conta + histórico de risco)
    scripts/                      # Checagens locais (ci_local.sh)
    tests/{unitarios,integracao}/ # Testes automatizados (sem chamar o LLM)
    Dockerfile, docker-compose.yml
    sample_sprint1_output.json    # Exemplo de relatório genômico
```

## 🧠 Módulos de inteligência

### RAG (perfil genômico) — infraestrutura herdada

Pipeline de busca vetorial + geração fundamentada (Gemini), com índice por
paciente, pseudonimização antes do LLM, logging estruturado sem dados
pessoais e disclaimers obrigatórios.

### Preditivo de risco cardíaco (`shared/preditivo/`)

Rede neural (PyTorch) treinada sobre uma base sintética de 5000 amostras de
operação hospitalar (10 features: SPO2, FC, carga do sistema, eventos nas
últimas 24h, etc.), prevendo um risco binário (`pico_risco`) e mapeando a
previsão para os 10 protocolos de resposta do enunciado. Acurácia de ~98%
no conjunto de teste (ver `app/backend/shared/preditivo/treinar.py`).

### Multiagente (`shared/agentes/`)

Cadeia de 4 agentes (OpenAI Agents SDK, LLM = Gemini) ligados por handoffs:
**Orquestrador** → **Analista de Risco** (chama o modelo preditivo) →
**Especialista em Protocolos** (avalia os protocolos aplicáveis) →
**Planejador de Resposta** (gera a recomendação final, com saída validada
por Pydantic). Ver `app/backend/shared/agentes/orquestracao.py`.

## ▶️ Como rodar

Pré-requisitos: **Docker**, **Node.js/npm** e uma chave do Gemini (gratuita):
https://aistudio.google.com/apikey

```bash
# 1. Backend (sobe junto o Postgres, via docker-compose)
cd app/backend
cp .env.example .env                  # preencha GEMINI_API_KEY e POSTGRES_PASSWORD
docker compose up -d --build
curl http://localhost:5000/api/health # {"status": "ok", ...}

# 2. Front mobile local (opcional — testa contra o backend da sua máquina)
cd ../mobile
npm install
npx expo start --web                  # abre em http://localhost:8081

# 3. Front web local (opcional)
cd ../web
npm install
npm run dev                           # abre em http://localhost:5173
```

- Testes e checagem de tipos (sem chamar o Gemini): `bash app/backend/scripts/ci_local.sh`.
- Treinar o modelo preditivo: `python -m shared.preditivo.treinar`, em `app/backend`.
- Detalhes de cada parte (endpoints, variáveis de ambiente, lógica de
  negócio): `app/backend/README.md`, `app/mobile/README.md`,
  `app/web/README.md`.

## 🚀 Deploy

| Parte | Onde | Status |
|---|---|---|
| Backend | Túnel ngrok, domínio fixo `remindful-unsliced-glisten.ngrok-free.dev` (ver `app/backend/README.md#deploy`) | Decidido — liga só quando for demonstrar/testar fim-a-fim |
| Web | **Publicado:** https://fase-7-coracao-sob-controle-previsao.vercel.app (Vercel, Root Directory `app/web`, CI/CD a cada push) | ✅ Feito |
| Mobile | `.apk` via `eas build` (perfil `preview`). `EXPO_PUBLIC_API_URL` já preenchido em `eas.json` com a URL do ngrok | Decidido — falta rodar `eas build` |

O túnel ngrok não fica ligado 24/7: o enunciado só exige o backend
acessível no momento de gravar o vídeo de demonstração (fluxo completo
Wokwi → backend → Vercel/APK), não um hosting permanente.

### Observabilidade

`observabilidade.py` não é um script que se roda à parte: ele é importado
pelo `src/main.py` e roda sozinho, junto com o backend. Pra ver o que ele
registra:

- `curl http://localhost:5000/api/metrics` — contadores (perguntas,
  indexações, resets, erros) e latência (p50/p95) desde o último start.
- `app/backend/shared/logs/app.log` — um evento em JSON por linha, sem o
  texto da pergunta (só hash, tamanho e seções usadas).

As métricas zeram quando o backend reinicia; não há painel visual nem alertas.

**Antes de apresentar para outras pessoas:** troque qualquer chave que tenha
sido compartilhada fora do `.env`. O `.env` está no `.gitignore`.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
