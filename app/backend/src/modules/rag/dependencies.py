import os
import threading
from typing import Any

from shared.rag_system import GenomicRAGPipeline

_pipeline: GenomicRAGPipeline | None = None
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


def get_pipeline_if_exists() -> GenomicRAGPipeline | None:
    """Devolve o pipeline já criado, sem forçar sua criação."""
    return _pipeline


class EstadoIndexacao:
    def __init__(self) -> None:
        self.indexado = False


_estado = EstadoIndexacao()


def get_estado() -> EstadoIndexacao:
    return _estado
