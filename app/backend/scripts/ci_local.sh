#!/usr/bin/env bash
# Roda localmente as mesmas checagens do CI (.github/workflows/ci.yml),
# sem precisar do GitHub. Use com a venv ativa: bash scripts/ci_local.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Testes (unitários + integração, sem chamar o LLM de verdade) =="
python -m pytest tests/ -q -p no:cacheprovider

echo "== Checagem de tipos (pyright) =="
python -m pyright
