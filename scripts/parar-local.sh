#!/usr/bin/env bash
# Derruba tudo que o subir-local.sh levantou: ngrok, mobile, web (pelos PIDs
# salvos em logs/*.pid, com fallback por padrão de comando) e o backend
# (docker compose down, sem apagar os volumes — Postgres/Grafana continuam
# preservados pra próxima subida).
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS="$RAIZ/logs"

parar_pid() {
  local nome="$1" arquivo="$2"
  if [ ! -f "$arquivo" ]; then
    echo "  - $nome: sem logs/$(basename "$arquivo"), pulando"
    return
  fi
  local pid
  pid="$(cat "$arquivo")"
  rm -f "$arquivo"

  if ! kill -0 "$pid" 2>/dev/null; then
    echo "  - $nome já não estava rodando"
    return
  fi

  kill -TERM -- "-$pid" 2>/dev/null
  kill -TERM "$pid" 2>/dev/null
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    kill -KILL -- "-$pid" 2>/dev/null
    kill -KILL "$pid" 2>/dev/null
    sleep 1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    # O ngrok instalado via snap roda confinado pelo AppArmor e pode recusar
    # sinais de certos contextos ("permission denied" mesmo sendo o mesmo
    # usuário). Se isso acontecer, `sudo kill -9 $pid` costuma resolver.
    echo "  ✗ $nome (pid $pid) não respondeu a kill — rode: sudo kill -9 $pid"
  else
    echo "  ✓ $nome parado (pid $pid)"
  fi
}

echo "→ Parando ngrok/mobile/web"
parar_pid "ngrok"  "$LOGS/ngrok.pid"
parar_pid "mobile" "$LOGS/mobile.pid"
parar_pid "web"    "$LOGS/web.pid"

# Fallback por padrão de comando — cobre processos filhos que sobraram
# (ex.: sessões antigas, subidas antes do script usar 'set -m').
pkill -f "ngrok http 5000" 2>/dev/null && echo "  ✓ resquício de ngrok encerrado"
pkill -f "$RAIZ/app/mobile/node_modules/.bin/expo" 2>/dev/null && echo "  ✓ resquício do metro/expo encerrado"
pkill -f "$RAIZ/app/web/node_modules/.bin/vite" 2>/dev/null && echo "  ✓ resquício do vite encerrado"

echo "→ Backend (docker compose down)"
(cd "$RAIZ/app/backend" && docker compose down)

echo "✓ Tudo parado. Volumes do Postgres/Grafana preservados."
