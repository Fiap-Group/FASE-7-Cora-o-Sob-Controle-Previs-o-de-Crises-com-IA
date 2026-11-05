#!/usr/bin/env bash
# Sobe tudo de uma vez pra testar o fluxo completo localmente: backend (docker
# compose), túnel ngrok (domínio fixo, pro .apk/Vercel falarem com o backend
# local) e os dois dev servers (mobile e web). Cada peça roda em background,
# cada uma na sua própria sessão (setsid) — assim parar-local.sh consegue
# matar a árvore inteira (processos filhos incluídos) com um único kill.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS="$RAIZ/logs"
mkdir -p "$LOGS"

NGROK_DOMINIO="remindful-unsliced-glisten.ngrok-free.dev"

for bin in docker ngrok npx setsid; do
  command -v "$bin" >/dev/null || { echo "✗ '$bin' não encontrado no PATH."; exit 1; }
done

subir_em_background() {
  local pastade="$1" arquivo_pid="$2" arquivo_log="$3"
  shift 3
  (cd "$pastade" && setsid "$@" > "$arquivo_log" 2>&1 < /dev/null &
   echo $! > "$arquivo_pid")
}

echo "→ Backend (docker compose)"
(cd "$RAIZ/app/backend" && docker compose up -d --build)

echo "→ Esperando o backend responder em /api/health..."
for _ in $(seq 1 30); do
  if curl -sf http://localhost:5000/api/health >/dev/null 2>&1; then
    echo "  ✓ backend ok (localhost:5000)"
    break
  fi
  sleep 2
done
curl -sf http://localhost:5000/api/health >/dev/null 2>&1 || echo "  ✗ backend não respondeu — ver 'docker compose logs backend' em app/backend"

echo "→ Túnel ngrok ($NGROK_DOMINIO)"
subir_em_background "$RAIZ" "$LOGS/ngrok.pid" "$LOGS/ngrok.log" ngrok http 5000 --url="$NGROK_DOMINIO"
sleep 3
if curl -sf --max-time 5 "https://$NGROK_DOMINIO/api/health" >/dev/null 2>&1; then
  echo "  ✓ túnel ok — URL pública: https://$NGROK_DOMINIO"
else
  echo "  ✗ túnel não respondeu — ver logs/ngrok.log (ex.: domínio já em uso por outro processo ngrok)"
fi

echo "→ Mobile (Expo web)"
subir_em_background "$RAIZ/app/mobile" "$LOGS/mobile.pid" "$LOGS/mobile.log" npx expo start --web
sleep 2
if curl -sf --max-time 5 http://localhost:8081 >/dev/null 2>&1; then
  echo "  ✓ mobile ok — http://localhost:8081"
else
  echo "  … mobile ainda compilando — ver logs/mobile.log (demora mais que o backend/web)"
fi

echo "→ Web (Vite)"
subir_em_background "$RAIZ/app/web" "$LOGS/web.pid" "$LOGS/web.log" npm run dev -- --port 5173
sleep 2
if curl -sf --max-time 5 http://localhost:5173 >/dev/null 2>&1; then
  echo "  ✓ web ok — http://localhost:5173"
else
  echo "  ✗ web não respondeu — ver logs/web.log"
fi

cat <<EOF

Tudo no ar (o que não ficou "ok" acima, ver o log correspondente em logs/):
  Backend  http://localhost:5000      (docker compose, fica rodando até você parar)
  Grafana  http://localhost:3000      (admin / cardioia)
  ngrok    https://$NGROK_DOMINIO
  Mobile   http://localhost:8081
  Web      http://localhost:5173

Pra derrubar tudo: ./scripts/parar-local.sh
EOF
