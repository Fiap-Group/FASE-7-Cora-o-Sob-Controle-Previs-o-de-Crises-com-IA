"""
=============================================================================
Rotina de operação (AI for RPA) — executa a checagem do sistema e registra o resultado
=============================================================================
Faz, em ordem:
  1. testes unitários (pytest), que não chamam o LLM;
  2. avaliação de recuperação contra o gabarito (sem LLM);
  3. checagem de saúde do backend, se ele estiver rodando.

Grava o resultado em logs/rotina_operacao.json. Pode ser agendada com cron
(Linux/macOS), Agendador de Tarefas (Windows) ou executada à mão:

    python scripts/rotina_operacao.py

Código de saída 0 = tudo passou; 1 = alguma etapa falhou.
=============================================================================
"""

from typing import Any
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
REGISTRO = BACKEND / "logs" / "rotina_operacao.json"
URL_SAUDE = f"http://127.0.0.1:{os.getenv('PORT', '5000')}/api/health"


def executar(nome: str, comando: list[str]) -> dict[str, Any]:
    inicio = datetime.now()
    processo = subprocess.run(comando, cwd=BACKEND, capture_output=True, text=True)
    return {
        "etapa": nome,
        "ok": processo.returncode == 0,
        "duracao_s": round((datetime.now() - inicio).total_seconds(), 1),
        "saida_final": (processo.stdout or processo.stderr).strip().splitlines()[-1:] or [""],
    }


def checar_backend() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(URL_SAUDE, timeout=5) as resposta:
            corpo = json.loads(resposta.read().decode("utf-8"))
            return {"etapa": "backend em execução", "ok": resposta.status == 200, "detalhe": corpo}
    except Exception as erro:  # backend desligado não é falha da rotina
        return {"etapa": "backend em execução", "ok": None, "detalhe": f"não respondeu: {type(erro).__name__}"}


def main() -> int:
    python = sys.executable
    etapas = [
        executar("testes unitários", [python, "-m", "pytest", "tests/", "-q"]),
        executar("avaliação de recuperação", [python, "avaliacao/avaliar.py"]),
        checar_backend(),
    ]
    falhou = any(e["ok"] is False for e in etapas)
    registro = {
        "executado_em": datetime.now().isoformat(timespec="seconds"),
        "status": "falhou" if falhou else "ok",
        "etapas": etapas,
    }
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rotina {registro['status']}. Registro em {REGISTRO}")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
