# FIAP - Faculdade de Informática e Administração Paulista

# Genera Intelligence — Enterprise Challenge (Dasa)

> **Declaração:** esta solução **não concorre ao prêmio Dasa** e é mantida
> em **sigilo** pela equipe de tutores, conforme a orientação da FIAP. O
> repositório é privado e compartilhado apenas com o perfil `fiap-tutoria`.

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

App (React Native/Expo, versão web) + backend (Python/Flask + RAG) para o
desafio Dasa/Genera. O paciente envia o próprio relatório genético e conversa
com um agente de IA sobre ele, em linguagem simples, com as fontes à vista e
aviso de que a resposta é informativa, não um diagnóstico.

## 🎥 Vídeo de apresentação

- **Sprint 4 (versão final):** <https://youtu.be/6f-fDSlXqD8>
- **Sprint 3 (versão anterior):** <https://youtu.be/B0GdbByxrrM>

## 🌐 Aplicação em execução (deploy)

- **Front (web):** https://dashing-mermaid-639c35.netlify.app
- **Backend:** roda no computador da equipe via Docker, exposto por um túnel
  ngrok com **domínio fixo** (`remindful-unsliced-glisten.ngrok-free.dev`),
  ligado apenas durante a apresentação. O front já está publicado apontando
  para esse endereço — ver seção _Como rodar_.
- **Mobile:** o código é Expo, mas a entrega foi validada na **versão web**.
  Não há APK nem build nativo.

## 📁 Estrutura do projeto

```
docs/
  ARQUITETURA_IA.md              # Escolha do LLM, embeddings, retrieval
  GOVERNANCA_E_RISCOS.md          # Limites do agente, disclaimers, privacidade
  POLITICA_GOVERNANCA_IA.md       # LGPD, ciclo de vida dos dados, logging, explicabilidade
  AVALIACAO_MODELO.md             # Resultados da avaliação contra o gabarito

.github/workflows/ci.yml          # CI: testes + checagem de tipos a cada push

app/                              # App React Native/Expo (front web)
  src/                            # screens, components, db (SQLite), services
  netlify.toml                    # Configuração do deploy estático

  backend/                        # Sistema RAG (backend)
    api.py                        # API Flask: index, chat, reset, health, metrics
    rag_system.py                 # Pipeline: limpeza, chunking, embeddings, busca, geração
    prompts.py, glossario.py      # Prompt do agente para leigos e glossário
    observabilidade.py            # Logs estruturados (JSON) e métricas
    avaliacao/                    # Gabarito, avaliação do modelo e validação
    scripts/                      # Rotina de operação e checagens locais
    tests/                        # Testes automatizados (sem chamar o LLM)
    Dockerfile, docker-compose.yml
    sample_sprint1_output.json    # Exemplo de relatório genômico
```

## 🧠 Evolução da inteligência do projeto

- **Sprint 1** — estruturação do laudo genômico em JSON padronizado.
- **Sprint 2** — desenho do pipeline RAG (chunking, embeddings, busca vetorial,
  prompt anti-alucinação) e demo inicial.
- **Sprint 3** — RAG virou API real, consumida por um front funcional; usuário
  passou a fornecer os próprios dados; Gemini como LLM gratuito, com retry;
  resumos e chat persistidos localmente.
- **Sprint 4 (versão final)** — preparo para uso real:
  - **Governança:** consentimento, pseudonimização antes do LLM, "apagar meus
    dados" (`docs/POLITICA_GOVERNANCA_IA.md`).
  - **Explicabilidade:** fontes do relatório em cada resposta.
  - **Logging e monitoramento:** eventos em JSON sem texto das perguntas,
    `GET /api/metrics`, rotina de operação agendável.
  - **Avaliação:** gabarito de 28 perguntas, validação automática das respostas
    (tamanho, clareza, números, jargão) — `docs/AVALIACAO_MODELO.md`.
  - **Linguagem para leigos:** prompt reescrito (respostas curtas, sem jargão
    sem tradução, glossário).
  - **Correções:** índice por paciente, backend só em `127.0.0.1` por padrão,
    erros internos não expostos ao cliente, CORS restrito ao front.

## 🎨 Evolução da experiência do usuário

- **Sprint 1 → 2:** demo interna (Streamlit), só para validar o pipeline.
- **Sprint 3:** interface para o paciente final, em abas (Dashboard → Riscos →
  Ancestralidade → Análise/Chat); formulário guiado para enviar o relatório;
  envio já leva direto ao resumo e ao chat; exclusão de dados sob controle do
  usuário.
- **Sprint 4:** fontes recolhíveis em cada resposta, consentimento antes do
  envio, botão "Apagar meus dados" (que já abre o formulário para um novo
  relatório, em vez de travar numa tela vazia), link para cancelar a edição
  de um novo relatório sem perder o resumo atual, respostas mais curtas e
  sem jargão.

**Salvaguardas:** disclaimer fixo nas telas e anexado por código a toda
resposta (não depende do LLM lembrar); prompt trata risco genético como fator,
não destino, e nunca inventa valor fora do relatório do usuário; erros do
backend são sempre explicados ao usuário.

**Nota de escopo:** o resumo automático cobre os dados do relatório (riscos e
ancestralidade), não a conversa do chat — o histórico da conversa fica
preservado à parte, no SQLite local.

## ✅ Requisitos desta entrega

| Requisito                                               | Onde está                                                                           |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Dashboard com cards de risco e resumo de ancestralidade | `app/src/screens/DashboardScreen.js`, `HomeScreen.js`                               |
| Front-end simples e funcional                           | `app/` (versão web, Expo)                                                           |
| Navegação clara entre seções do perfil genético         | abas Dashboard / Riscos / Ancestralidade / Análise                                  |
| Personalização das respostas via RAG                    | `app/backend/rag_system.py` (índice por relatório)                                  |
| Simplificação de linguagem (NLP)                        | `prompts.py`, `glossario.py`, `TextCleaner`                                         |
| Sistema RAG (busca vetorial + geração fundamentada)     | `rag_system.py`, detalhado em `docs/ARQUITETURA_IA.md`                              |
| Resumos automáticos do relatório                        | `app/src/services/resumoService.js` (ver nota de escopo)                            |
| Comunicação responsável e disclaimers obrigatórios      | disclaimer anexado por código em `rag_system.py`                                    |
| Multimodalidade (opcional)                              | avaliada e deixada fora do escopo (OCR/visão computacional exigiria frente própria) |
| Persistência de dados e histórico de interações         | `app/src/db/database.js` (SQLite local)                                             |
| **Governança de IA: LGPD, explicabilidade e logging**   | `docs/POLITICA_GOVERNANCA_IA.md`, `observabilidade.py`                              |
| **Monitoramento dos pipelines**                         | `GET /api/health`, `GET /api/metrics`, `logs/app.log`                               |
| **Automações de execução (AI for RPA)**                 | `scripts/rotina_operacao.py`, `.github/workflows/ci.yml`                            |
| **Avaliação do modelo**                                 | `avaliacao/avaliar.py`, `docs/AVALIACAO_MODELO.md`                                  |
| **Validação das respostas**                             | `avaliacao/validacao.py`                                                            |
| **Deploy do front**                                     | `app/netlify.toml`, seção _Como rodar_ abaixo                                       |
| Visão Computacional                                     | não aplicável: não foi utilizada neste projeto                                      |
| Documentação da arquitetura de IA                       | `docs/ARQUITETURA_IA.md`                                                            |
| Relatório de governança e riscos                        | `docs/GOVERNANCA_E_RISCOS.md`, `docs/POLITICA_GOVERNANCA_IA.md`                     |
| Apresentação em vídeo                                   | link no topo deste README                                                           |
| README final                                            | este arquivo                                                                        |

## ▶️ Como rodar

Pré-requisitos: **Docker**, **Node.js/npm** e uma chave do Gemini (gratuita):
https://aistudio.google.com/apikey

```bash
# 1. Backend
cd app/backend
cp .env.example .env                  # preencha GEMINI_API_KEY
docker compose up -d --build
curl http://localhost:5000/api/health # {"status": "ok", ...}

# 2. Expor o backend (domínio fixo, não muda entre execuções)
ngrok http --url=remindful-unsliced-glisten.ngrok-free.dev 5000

# 3. Front local (opcional — testa contra o backend da sua máquina)
cd ..
npm install
npx expo start --web                  # abre em http://localhost:8081
```

- O site publicado (**https://dashing-mermaid-639c35.netlify.app**) já aponta
  para o domínio do ngrok acima. Com os passos 1 e 2 no ar, ele funciona sem
  precisar gerar build nem publicar de novo.
- Para parar: `docker compose down` em `app/backend` e `Ctrl+C` no terminal do ngrok.
- Testes e checagem de tipos (sem chamar o Gemini): `bash app/backend/scripts/ci_local.sh`.
- Avaliação com o Gemini (usa a cota diária): `python avaliacao/avaliar.py --com-llm --limite 10`, em `app/backend`.
- Fluxo de teste manual: aba **Ancestralidade** → "Usar exemplo" → "Enviar relatório" (autorize o consentimento) → pergunte algo no **Chat** → confira as fontes da resposta → "Apagar meus dados" ao final.
- Detalhes do backend (endpoints, variáveis de ambiente, curl): `app/backend/README.md`.

### Por que ngrok

O backend não está hospedado em nenhuma nuvem: ele roda no Docker do
computador da equipe, só em `localhost`. O [ngrok](https://ngrok.com/) cria um
túnel que expõe esse `localhost:5000` num endereço público (`https://...`),
sem precisar configurar roteador nem contratar servidor.

O problema do plano gratuito do ngrok é que, normalmente, **o endereço muda
toda vez que o túnel é reiniciado** — e o front publicado no Netlify já tem
esse endereço fixado no build (`EXPO_PUBLIC_API_URL`). Pra não ter que gerar
um build novo e publicar de novo a cada apresentação, reservamos um
**domínio estático gratuito** na conta de ngrok da equipe
(`remindful-unsliced-glisten.ngrok-free.dev`): esse endereço nunca muda,
então o túnel pode cair e subir de novo quantas vezes for preciso que o front
publicado continua funcionando, sem novo deploy.

Resumindo o fluxo: `docker compose up` sobe o backend em `localhost:5000` →
`ngrok http --url=remindful-unsliced-glisten.ngrok-free.dev 5000` expõe esse
endereço publicamente, sempre no mesmo domínio → o front no Netlify já está
configurado pra falar com esse domínio. Só é preciso ligar os dois (Docker +
ngrok) antes de uma demonstração; o túnel fica sem uso (mas sem custo) o
resto do tempo.

### Observabilidade

`observabilidade.py` não é um script que se roda à parte: ele é importado
pelo `api.py` e roda sozinho, junto com o backend. Pra ver o que ele registra:

- `curl http://localhost:5000/api/metrics` — contadores (perguntas,
  indexações, resets, erros) e latência (p50/p95) desde o último start.
- `app/backend/logs/app.log` — um evento em JSON por linha, sem o texto da
  pergunta (só hash, tamanho e seções usadas).

As métricas zeram quando o backend reinicia; não há painel visual nem alertas.

### Se o código do front mudar

O build publicado precisa ser refeito:

```bash
cd app
EXPO_PUBLIC_API_URL=https://remindful-unsliced-glisten.ngrok-free.dev npx expo export -p web --clear
npx netlify-cli deploy --prod --dir dist
```

**Antes de apresentar para outras pessoas:** troque qualquer chave que tenha
sido compartilhada fora do `.env`. O `.env` está no `.gitignore`.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
