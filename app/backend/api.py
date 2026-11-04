"""
=============================================================================
API REST · Genera Intelligence — Challenge Dasa/Genera
=============================================================================
Expõe o pipeline RAG (rag_system.py) como uma API HTTP para o app Expo
(web). Cada evento relevante é registrado em logs/app.log (ver
observabilidade.py e docs/POLITICA_GOVERNANCA_IA.md).

Execução local:
    cp .env.example .env     # preencher GEMINI_API_KEY
    pip install -r requirements.txt
    python api.py

Variáveis de ambiente relevantes:
    HOST          endereço de escuta (padrão 127.0.0.1; Docker usa 0.0.0.0)
    PORT          porta (padrão 5000)
    FLASK_DEBUG   "1" ativa o debugger do Flask. Nunca use em exposição pública.
    CORS_ORIGINS  origens do front permitidas, separadas por vírgula

Endpoints:
    GET  /api/health    status, se há relatório indexado e modo do LLM
    GET  /api/metrics   contadores e latências desde o último start
    POST /api/index     indexa o perfil genômico (substitui o anterior)
    POST /api/chat      { "question": "..." } -> resposta, fontes e flag grounded
    POST /api/reset     apaga o índice do paciente da memória do backend
=============================================================================
"""

import logging
import os
import threading
import time
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from observabilidade import configurar_logs, hash_pergunta, metricas

load_dotenv()
configurar_logs()

from rag_system import GenomicRAGPipeline  # noqa: E402  (precisa vir depois do load_dotenv)

logger = logging.getLogger("genera_api")

app = Flask(__name__)
origens_permitidas = [
    origem.strip()
    for origem in os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:19006").split(",")
    if origem.strip()
]
CORS(app, origins=origens_permitidas)

_pipeline: GenomicRAGPipeline | None = None
_patient_indexed = False
_lock_pipeline = threading.Lock()


def get_pipeline() -> GenomicRAGPipeline:
    """Cria o pipeline RAG uma única vez (embeddings + LLM ficam em memória)."""
    global _pipeline
    with _lock_pipeline:
        if _pipeline is None:
            if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                default_llm_backend = "gemini"
            elif os.getenv("ANTHROPIC_API_KEY"):
                default_llm_backend = "anthropic"
            else:
                default_llm_backend = "openai"
            config: dict[str, Any] = {
                "embedding_backend": os.getenv("EMBEDDING_BACKEND", "sentence_transformers"),
                "embedding_model": os.getenv("EMBEDDING_MODEL"),
                "llm_backend": os.getenv("LLM_BACKEND", default_llm_backend),
                "llm_model": os.getenv("LLM_MODEL"),
                "top_k": int(os.getenv("RAG_TOP_K", "5")),
                "min_score": float(os.getenv("RAG_MIN_SCORE", "0.25")),
            }
            _pipeline = GenomicRAGPipeline.from_config(config)
    return _pipeline


def erro_interno(contexto: str, excecao: Exception, status: int = 500):
    """Loga o erro completo no servidor e devolve ao cliente só uma mensagem genérica."""
    logger.exception(contexto, extra={"evento": "erro", "erro_tipo": type(excecao).__name__})
    metricas.registrar_erro(f"{contexto}: {type(excecao).__name__}")
    return jsonify({"error": contexto}), status


@app.route("/api/health", methods=["GET"])
def health():
    llm = os.getenv("LLM_BACKEND") or ("gemini" if os.getenv("GEMINI_API_KEY") else "não configurado")
    return jsonify({
        "status": "ok",
        "paciente_indexado": _patient_indexed,
        "llm": llm,
        "uptime_s": metricas.resumo()["uptime_s"],
    }), 200


@app.route("/api/metrics", methods=["GET"])
def metrics():
    return jsonify(metricas.resumo()), 200


@app.route("/api/index", methods=["POST"])
def index_patient():
    """Recebe o JSON genômico do paciente e substitui o índice atual."""
    global _patient_indexed

    genomic_json: dict[str, Any] | None = request.get_json(silent=True)
    if not genomic_json:
        return jsonify({"error": "JSON do perfil genômico é obrigatório"}), 400

    try:
        pipeline = get_pipeline()
        n_chunks = pipeline.index_patient(genomic_json)
        _patient_indexed = True
    except Exception as e:
        return erro_interno("Falha ao indexar perfil genômico", e)

    metricas.incrementar("indexacoes")
    logger.info("Relatório indexado", extra={"evento": "indexacao", "chunks": n_chunks})
    return jsonify({"status": "indexed", "chunks": n_chunks}), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """Responde uma pergunta do paciente usando o pipeline RAG (retrieval + LLM)."""
    if not _patient_indexed:
        return jsonify({"error": "Nenhum perfil genômico indexado. Chame /api/index primeiro."}), 400

    data: dict[str, Any] = request.get_json(silent=True) or {}
    question: str = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Campo 'question' é obrigatório"}), 400

    inicio = time.perf_counter()
    try:
        pipeline = get_pipeline()
        response = pipeline.answer(question)
    except Exception as e:
        metricas.incrementar("erros_pergunta")
        return erro_interno("Falha ao gerar resposta", e)

    latencia_ms = (time.perf_counter() - inicio) * 1000
    metricas.incrementar("perguntas")
    metricas.registrar_latencia(latencia_ms)
    if not response.grounded:
        metricas.incrementar("respostas_sem_ancoragem")

    # Log sem o texto da pergunta: só hash, tamanho e metadados técnicos.
    logger.info(
        "Pergunta respondida",
        extra={
            "evento": "pergunta",
            "pergunta_hash": hash_pergunta(question),
            "pergunta_chars": len(question),
            "secoes": [rc.chunk.section for rc in response.retrieved_chunks],
            "grounded": response.grounded,
            "latencia_ms": round(latencia_ms, 1),
        },
    )

    return jsonify({
        "answer": response.answer,
        "grounded": response.grounded,
        "sources": [
            {
                "section": rc.chunk.section,
                "subsection": rc.chunk.subsection,
                "text": rc.chunk.text,
                "score": rc.score,
            }
            for rc in response.retrieved_chunks
        ],
    }), 200


@app.route("/api/reset", methods=["POST"])
def reset():
    """Apaga o índice do paciente da memória. Os dados do app (SQLite) são apagados no próprio dispositivo."""
    global _patient_indexed
    if _pipeline is not None:
        _pipeline.limpar_indice()
    _patient_indexed = False
    metricas.incrementar("resets")
    logger.info("Índice do paciente apagado a pedido do usuário", extra={"evento": "reset"})
    return jsonify({"status": "reset"}), 200


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host=host, port=int(os.getenv("PORT", "5000")), debug=debug)
