# Mobile — CardioIA

App **React Native / Expo**, 6 abas (`App.js`):

| Aba | Tela | O que faz |
|---|---|---|
| Dashboard | `DashboardScreen` | resumo do perfil genômico (risco de maior severidade + ancestralidade) |
| Riscos | `HomeScreen` | lista completa de riscos genéticos mapeados do relatório |
| Ancestralidade | `ProfileScreen` | perfil de ancestralidade genômica (dados importados, não calculados aqui) |
| Análise | `AnaliseStack` | resumos gerados + chat com o agente RAG sobre o relatório |
| Previsão | `PrevisaoStack` | formulário das 10 métricas de operação → avalia risco cardíaco pelo backend |
| Perfil | `PerfilUsuarioScreen` | avatar + nickname + risco mais recente em destaque + histórico ("ficha de jogador") |

## Lógica de negócio

- **Conta compartilhada com o web**: login/cadastro (`AuthStack`,
  `AuthContext`) chama `POST /api/auth/*` no backend — a conta em si mora
  no Postgres do backend, não neste app. O que fica neste aparelho é só a
  "sessão lembrada" (tabela `sessao_atual` do SQLite local), pra não pedir
  login de novo a cada abertura.
- **SQLite local** (`src/db/database.js`) guarda o que é só deste
  dispositivo: relatório genômico importado, histórico de chat/resumos,
  consentimento LGPD aceito e um cache local das avaliações de risco já
  feitas. O histórico **oficial** do Perfil (o que a aba "Perfil" mostra)
  vem do backend, não deste cache.
- **Previsão de risco**: a tela de Previsão manda as 10 métricas pro
  backend (`POST /api/risco/avaliar`) junto do `usuario.id` de quem está
  logado — é esse `usuario_id` que faz a avaliação aparecer depois na aba
  Perfil.
- **IoT**: o botão "Usar leitura do sensor" busca a última leitura MQTT do
  ESP32 (`GET /api/risco/leitura-iot`) e preenche automaticamente as 3
  métricas que vêm do sensor (FC, SPO2, pressão); as outras 7 (métricas de
  operação hospitalar) continuam manuais.

## Rodar localmente

```bash
cd app/mobile
npm install
npx expo start --web   # abre em http://localhost:8081
```

Por padrão aponta pro backend em `http://localhost:5000` (`10.0.2.2` no
emulador Android). Pra apontar pra outro backend, defina
`EXPO_PUBLIC_API_URL` antes de rodar.

## Gerar o `.apk` (EAS Build — publicado)

**Download direto:** https://expo.dev/artifacts/eas/b2WWbMLX0PBgg02x2llJ0ZgWl-_Wcosrzd5SJqXA4do.apk

**Build no dashboard:** https://expo.dev/accounts/jonny_1/projects/cardioia/builds/d16c7193-34cd-4ee7-9aaf-40524c311894

```bash
npx eas-cli login
npx eas-cli build -p android --profile preview
```

- `app.json`: nome, slug, `package`/`bundleIdentifier`
  (`com.jonathanluft.cardioia`) e `extra.eas.projectId` já configurados
  (projeto `@jonny_1/cardioia`).
- `eas.json`: perfil `preview` (build interno, `.apk` direto).
  `env.EXPO_PUBLIC_API_URL` já está preenchido com o túnel ngrok do
  backend (`https://remindful-unsliced-glisten.ngrok-free.dev`, domínio
  fixo — ver `app/backend/README.md#deploy`). O `.apk` só fala com o
  backend enquanto esse túnel estiver ligado.

## Arquivos

- `src/screens/`: uma tela por rota das abas/stacks.
- `src/navigation/`: `AuthStack`, `AnaliseStack`, `PrevisaoStack`.
- `src/services/`: `api.js` (chamadas HTTP ao backend), `riscoService.js`
  (avalia + persiste local), `resumoService.js`.
- `src/db/database.js`: schema e queries do SQLite local (`expo-sqlite`).
- `src/context/AuthContext.js`: sessão lembrada neste aparelho.
- `src/components/`: `RiscoCard`, `Avatar`, `Disclaimer`, etc.
- `src/data/riscoCardiacoFeatures.js`: contrato das 10 features com o
  backend (`shared/preditivo/dataset.py`).
