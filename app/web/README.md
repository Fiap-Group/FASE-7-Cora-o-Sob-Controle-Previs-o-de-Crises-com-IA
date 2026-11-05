# Web — CardioIA

Dashboard **React + Vite**. Cobre login, avaliação de risco cardíaco, o
perfil gamificado e o RAG genômico (relatório + chat + ancestralidade) —
mesmo conjunto de funcionalidades do mobile, exceto a persistência local
(aqui é `localStorage`, não SQLite).

## Lógica de negócio

- **`Auth.jsx`**: login/cadastro contra `POST /api/auth/*` do backend —
  mesma conta do mobile (Postgres), não é uma conta separada deste app. A
  sessão lembrada neste navegador fica só no `localStorage`
  (`sessao.js`, chave `cardioia_sessao`); a conta em si não.
- **`Dashboard.jsx`**: tela única com um toggle de 3 abas no topo —
  - **Avaliar risco**: formulário com as 10 métricas de operação →
    `POST /api/risco/avaliar` (manda o `usuario.id` logado, pra alimentar
    o Perfil) → mostra risco + protocolos sugeridos.
  - **Perfil** (`Perfil.jsx`): avatar + nickname, risco mais recente em
    destaque, grid com os dados daquela avaliação e histórico curto —
    consome `GET /api/perfil/{usuario_id}`.
  - **Ancestralidade** (`Ancestralidade.jsx` + `Chat.jsx`): formulário de
    relatório genômico (ou "Usar exemplo") → `POST /api/index` →
    barras de ancestralidade + riscos de doenças → chat com o agente
    (`POST /api/chat`) com resumos salvos e fontes citadas. Consentimento
    de uso dos dados via `window.confirm` antes do primeiro envio.
    Persistência (relatório, resumos, mensagens) em
    `localStorage['cardioia_genomico']` (`genomicoDb.js`) — não tem
    SQLite no navegador, mas o contrato replica `app/mobile/src/db/database.js`.
    **O backend indexa um único relatório por vez, global, sem
    usuário/sessão** — mobile e web (e qualquer aba aberta) compartilham
    o mesmo índice; indexar de um lado substitui o relatório indexado do
    outro.

## Rodar localmente

```bash
cd app/web
npm install
npm run dev   # abre em http://localhost:5173
```

Aponta pro backend em `http://localhost:5000` por padrão. Pra apontar pra
outro backend, defina `VITE_API_URL` num `.env` local (não versionado).

## Deploy (Vercel — publicado)

**URL de produção:** https://fase-7-coracao-sob-controle-previsao.vercel.app

- **Root Directory** do projeto na Vercel: `app/web`.
- Build command/output: padrão do Vite (`npm run build` → `dist/`), a
  Vercel detecta sozinha.
- `vercel.json` já tem o rewrite de SPA (`/* → /index.html`), exigido pelo
  enunciado.
- CI/CD: cada push no branch conectado dispara um novo deploy automático.
- Variável de ambiente configurada no painel: `VITE_API_URL` →
  `https://remindful-unsliced-glisten.ngrok-free.dev` (túnel ngrok do
  backend, domínio fixo — ver `app/backend/README.md#deploy`). **O
  dashboard web só consegue falar com o backend enquanto esse túnel
  estiver ligado** — liga-se na hora de testar/gravar a demonstração.

## Arquivos

- `src/App.jsx`: gate de autenticação (mostra `Auth` ou `Dashboard`).
- `src/Auth.jsx`, `src/Dashboard.jsx`, `src/Perfil.jsx`: telas de
  login/cadastro, dashboard (com as 3 abas) e perfil gamificado.
- `src/Ancestralidade.jsx`: formulário + visão do relatório genômico.
- `src/Chat.jsx`: lista de resumos + conversa com o agente RAG.
- `src/api.js`: todas as chamadas HTTP ao backend (risco, auth, perfil e
  RAG genômico).
- `src/resumoService.js`: gera um resumo do perfil consultando o agente.
- `src/genomicoDb.js`: persistência local (`localStorage`) do relatório
  genômico, resumos e conversas.
- `src/perfilGenomico.js`: funções de mapeamento do relatório genômico
  pra exibição (ancestralidade, nível de risco).
- `src/relatorioGenomicoExemplo.js`: relatório de exemplo ("Usar
  exemplo"), mesmo dado do mobile.
- `src/sessao.js`: sessão lembrada neste navegador (`localStorage`).
- `src/riscoCardiacoFeatures.js`: contrato das 10 features com o backend
  (mesmo arquivo do mobile, `src/data/riscoCardiacoFeatures.js`).
