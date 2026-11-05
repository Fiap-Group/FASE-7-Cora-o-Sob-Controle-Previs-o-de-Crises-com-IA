#!/usr/bin/env bash
# Sobe tudo de uma vez pra testar o fluxo completo localmente: backend (docker
# compose), túnel ngrok (domínio fixo, pro .apk/Vercel falarem com o backend
# local) e os dois dev servers (mobile e web). Cada peça roda em background;
# o script só confirma que cada uma subiu e devolve o terminal.
set -euo pipefail
set -m # cada job em background vira líder do seu próprio grupo de processos,
       # pra parar-local.sh conseguir matar a árvore inteira (ngrok/npx/node
       # filhos) com um kill no grupo, não só no processo-pai.

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS="$RAIZ/logs"
mkdir -p "$LOGS"

NGROK_DOMINIO="remindful-unsliced-glisten.ngrok-free.dev"

for bin in docker ngrok npx; do
  command -v "$bin" >/dev/null || { echo "✗ '$bin' não encontrado no PATH."; exit 1; }
done

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
nohup ngrok http 5000 --url="$NGROK_DOMINIO" > "$LOGS/ngrok.log" 2>&1 < /dev/null &
disown
echo $! > "$LOGS/ngrok.pid"
sleep 2
echo "  ✓ log em logs/ngrok.log — URL pública: https://$NGROK_DOMINIO"

echo "→ Mobile (Expo web)"
(cd "$RAIZ/app/mobile" && nohup npx expo start --web > "$LOGS/mobile.log" 2>&1 < /dev/null &
disown
echo $! > "$LOGS/mobile.pid")
sleep 2
echo "  ✓ log em logs/mobile.log — http://localhost:8081"

echo "→ Web (Vite)"
(cd "$RAIZ/app/web" && nohup npm run dev -- --port 5173 > "$LOGS/web.log" 2>&1 < /dev/null &
disown
echo $! > "$LOGS/web.pid")
sleep 2
echo "  ✓ log em logs/web.log — http://localhost:5173"

cat <<EOF

Tudo no ar:
  Backend  http://localhost:5000      (docker compose, fica rodando até você parar)
  Grafana  http://localhost:3000      (admin / cardioia)
  ngrok    https://$NGROK_DOMINIO
  Mobile   http://localhost:8081
  Web      http://localhost:5173

Logs em $LOGS/*.log. Pra parar mobile/web/ngrok:
  kill \$(cat $LOGS/ngrok.pid $LOGS/mobile.pid $LOGS/web.pid)
O backend continua até você rodar (em app/backend):
  docker compose down
EOF
