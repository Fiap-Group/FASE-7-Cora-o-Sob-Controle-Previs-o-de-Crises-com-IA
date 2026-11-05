from typing import Any
import hashlib
import json
import logging
import os
import threading
import time
from collections import deque
from logging.handlers import RotatingFileHandler

PASTA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
ARQUIVO_LOG = os.path.join(PASTA_LOGS, "app.log")


class FormatadorJSON(logging.Formatter):
    """Formata cada registro de log como uma linha JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Converte um registro de log em uma string JSON com os campos relevantes."""
        evento: dict[str, object] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(record.created)),
            "nivel": record.levelname,
            "logger": record.name,
            "mensagem": record.getMessage(),
        }
        for chave in ("evento", "pergunta_hash", "pergunta_chars", "secoes",
                      "grounded", "latencia_ms", "chunks", "erro_tipo"):
            if hasattr(record, chave):
                evento[chave] = getattr(record, chave)
        return json.dumps(evento, ensure_ascii=False)


def configurar_logs():
    """Configura o logger raiz com handlers de arquivo (com rotação) e console, em JSON."""
    os.makedirs(PASTA_LOGS, exist_ok=True)
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    if getattr(raiz, "_observabilidade_ok", False):
        return
    arquivo = RotatingFileHandler(ARQUIVO_LOG, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    arquivo.setFormatter(FormatadorJSON())
    console = logging.StreamHandler()
    console.setFormatter(FormatadorJSON())
    raiz.addHandler(arquivo)
    raiz.addHandler(console)
    setattr(raiz, "_observabilidade_ok", True)


def hash_pergunta(texto: str) -> str:
    """Gera um identificador curto e não reversível de uma pergunta, usado para correlacionar logs."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


class Metricas:
    """Contadores e latências em memória, reiniciados sempre que o backend sobe."""

    def __init__(self, tamanho_janela: int = 500):
        """Inicializa os contadores e a janela de latências."""
        self._lock = threading.Lock()
        self.iniciado_em = time.time()
        self.contadores: dict[str, int] = {
            "indexacoes": 0,
            "perguntas": 0,
            "erros_pergunta": 0,
            "respostas_sem_ancoragem": 0,
            "resets": 0,
        }
        self.latencias_ms: deque[float] = deque(maxlen=tamanho_janela)
        self.ultimo_erro: dict[str, str] | None = None

    def incrementar(self, nome: str):
        """Incrementa em um o contador com este nome."""
        with self._lock:
            self.contadores[nome] = self.contadores.get(nome, 0) + 1

    def registrar_latencia(self, ms: float):
        """Adiciona uma nova amostra de latência à janela."""
        with self._lock:
            self.latencias_ms.append(ms)

    def registrar_erro(self, mensagem: str):
        """Guarda o último erro ocorrido, com data e mensagem."""
        with self._lock:
            self.ultimo_erro = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "mensagem": mensagem}

    def resumo(self) -> dict[str, Any]:
        """Monta um resumo atual das métricas: uptime, contadores e percentis de latência."""
        with self._lock:
            ordenadas: list[float] = sorted(self.latencias_ms)

            def percentil(p: float) -> float | None:
                """Calcula o percentil `p` das latências ordenadas."""
                if not ordenadas:
                    return None
                return round(ordenadas[min(len(ordenadas) - 1, int(p * len(ordenadas)))], 1)
            return {
                "uptime_s": round(time.time() - self.iniciado_em),
                "contadores": dict(self.contadores),
                "latencia_ms": {"p50": percentil(0.50), "p95": percentil(0.95), "amostras": len(ordenadas)},
                "ultimo_erro": self.ultimo_erro,
            }


metricas = Metricas()
