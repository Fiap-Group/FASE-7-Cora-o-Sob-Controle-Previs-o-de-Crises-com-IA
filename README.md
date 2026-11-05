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

Entrega final do curso, unindo e evoluindo o que foi construído nas fases
anteriores em um único repositório:

- **App** (React Native/Expo, versão web) + **backend** (Python/FastAPI +
  RAG): infraestrutura herdada de uma fase anterior, reaproveitada como
  base — o paciente envia o próprio relatório genético e conversa com um
  agente de IA sobre ele, em linguagem simples, com as fontes à vista e
  aviso de que a resposta é informativa, não um diagnóstico.
- **Modelo preditivo de risco cardíaco** (PyTorch), treinado sobre uma base
  sintética de operação hospitalar.
- **Sistema multiagente** (OpenAI Agents SDK + Gemini), com 4 agentes
  especializados (Orquestrador → Analista de Risco → Especialista em
  Protocolos → Planejador de Resposta) que analisam o risco previsto e
  recomendam uma resposta operacional.

O modelo preditivo e o sistema multiagente já estão implementados e
testados de forma independente (`app/backend/shared/preditivo/`,
`app/backend/shared/agentes/`), mas ainda não estão expostos como endpoints
HTTP — essa integração, o deploy e a simulação de IoT fazem parte do
restante do escopo da Fase 7 e estão em andamento.

## 📁 Estrutura do projeto

```
docs/
  ARQUITETURA_IA.md              # Escolha do LLM, embeddings, retrieval (módulo RAG)
  GOVERNANCA_E_RISCOS.md          # Limites do agente, disclaimers, privacidade
  POLITICA_GOVERNANCA_IA.md       # LGPD, ciclo de vida dos dados, logging, explicabilidade
  AVALIACAO_MODELO.md             # Resultados da avaliação contra o gabarito (RAG)

.github/workflows/ci.yml          # CI: testes + checagem de tipos a cada push

app/                              # App React Native/Expo (front web)
  src/                            # screens, components, db (SQLite), services
  netlify.toml                    # Configuração do deploy estático

  backend/                        # Backend (FastAPI)
    src/
      main.py                     # Ponto de entrada da API (equivalente a app.ts/main.ts)
      modules/rag/                # Endpoints do RAG (router, dependencies, schemas)
    shared/                       # Compartilhável entre módulos
      rag_system.py, prompts.py, glossario.py, observabilidade.py
      preditivo/                  # Parte 1: modelo PyTorch de risco cardíaco
      agentes/                    # Parte 2: sistema multiagente (OpenAI Agents SDK + Gemini)
    avaliacao/                    # Gabarito, avaliação do modelo e validação (RAG)
    scripts/                      # Rotina de operação e checagens locais
    tests/                        # Testes automatizados (sem chamar o LLM)
    Dockerfile, docker-compose.yml
    sample_sprint1_output.json    # Exemplo de relatório genômico
```

## 🧠 Módulos de inteligência

### RAG (perfil genômico) — infraestrutura herdada

Pipeline de busca vetorial + geração fundamentada (Gemini), com índice por
paciente, pseudonimização antes do LLM, logging estruturado sem dados
pessoais, avaliação automática das respostas contra um gabarito e
disclaimers obrigatórios. Detalhado em `docs/ARQUITETURA_IA.md`,
`docs/GOVERNANCA_E_RISCOS.md` e `docs/POLITICA_GOVERNANCA_IA.md`.

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
# 1. Backend (RAG)
cd app/backend
cp .env.example .env                  # preencha GEMINI_API_KEY
docker compose up -d --build
curl http://localhost:5000/api/health # {"status": "ok", ...}

# 2. Front local (opcional — testa contra o backend da sua máquina)
cd ..
npm install
npx expo start --web                  # abre em http://localhost:8081
```

- Testes e checagem de tipos (sem chamar o Gemini): `bash app/backend/scripts/ci_local.sh`.
- Avaliação do RAG com o Gemini (usa a cota diária): `python avaliacao/avaliar.py --com-llm --limite 10`, em `app/backend`.
- Treinar o modelo preditivo: `python -m shared.preditivo.treinar`, em `app/backend`.
- Demo do multiagente (precisa de `GEMINI_API_KEY`): `python -m shared.agentes.demo`, em `app/backend`.
- Detalhes do backend (endpoints, variáveis de ambiente, curl): `app/backend/README.md`.

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
