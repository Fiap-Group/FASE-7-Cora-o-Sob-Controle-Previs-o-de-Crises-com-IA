#!/usr/bin/env bash
# Gera um novo .apk do mobile via EAS Build (perfil "preview" — ver
# app/mobile/eas.json). O build roda na nuvem da Expo, não localmente;
# o terminal fica preso até o build terminar e imprime o link do .apk.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v npx >/dev/null || { echo "✗ 'npx' não encontrado no PATH."; exit 1; }

cd "$RAIZ/app/mobile"
npx eas-cli build -p android --profile preview
