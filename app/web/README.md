# Web — CardioIA

Dashboard **React + Vite**. Cobre a parte do enunciado voltada a operação
hospitalar: login, avaliação de risco e o perfil gamificado — não tem o
RAG genômico (chat/ancestralidade), que é exclusivo do mobile.

## Lógica de negócio

- **`Auth.jsx`**: login/cadastro contra `POST /api/auth/*` do backend —
  mesma conta do mobile (Postgres), não é uma conta separada deste app. A
  sessão lembrada neste navegador fica só no `localStorage`
  (`sessao.js`, chave `cardioia_sessao`); a conta em si não.
- **`Dashboard.jsx`**: tela única com um toggle no topo —
  - **Avaliar risco**: formulário com as 10 métricas de operação →
    `POST /api/risco/avaliar` (manda o `usuario.id` logado, pra alimentar
    o Perfil) → mostra risco + protocolos sugeridos.
  - **Perfil** (`Perfil.jsx`): avatar + nickname, risco mais recente em
    destaque, grid com os dados daquela avaliação e histórico curto —
    consome `GET /api/perfil/{usuario_id}`.

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
- `src/Auth.jsx`, `src/Dashboard.jsx`, `src/Perfil.jsx`: as 3 telas.
- `src/api.js`: todas as chamadas HTTP ao backend.
- `src/sessao.js`: sessão lembrada neste navegador (`localStorage`).
- `src/riscoCardiacoFeatures.js`: contrato das 10 features com o backend
  (mesmo arquivo do mobile, `src/data/riscoCardiacoFeatures.js`).
