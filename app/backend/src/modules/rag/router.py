import logging
import os
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from shared.observabilidade import hash_pergunta, metricas
from shared.rag_system import GenomicRAGPipeline

from src.common.erros import erro_interno as _erro_interno_compartilhado

from .dependencies import EstadoIndexacao, get_estado, get_pipeline, get_pipeline_if_exists
from .schemas import ChatRequest, ChatResponse, FonteResposta, HealthResponse, IndexResponse, ResetResponse

logger = logging.getLogger("genera_api")

router = APIRouter(prefix="/api", tags=["rag"])


def erro_interno(contexto: str, excecao: Exception, status: int = 500) -> HTTPException:
    return _erro_interno_compartilhado(logger, contexto, excecao, status)


@router.get("/health", response_model=HealthResponse)
def health(estado: EstadoIndexacao = Depends(get_estado)) -> HealthResponse:
    llm = os.getenv("LLM_BACKEND") or ("gemini" if os.getenv("GEMINI_API_KEY") else "não configurado")
    return HealthResponse(
        status="ok",
        paciente_indexado=estado.indexado,
        llm=llm,
        uptime_s=metricas.resumo()["uptime_s"],
    )


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    return metricas.resumo()


@router.post("/index", response_model=IndexResponse)
def index_patient(
    genomic_json: dict[str, Any],
    estado: EstadoIndexacao = Depends(get_estado),
    pipeline: GenomicRAGPipeline = Depends(get_pipeline),
) -> IndexResponse:
    if not genomic_json:
        raise HTTPException(status_code=400, detail="JSON do perfil genômico é obrigatório")

    try:
        n_chunks = pipeline.index_patient(genomic_json)
        estado.indexado = True
    except Exception as e:
        raise erro_interno("Falha ao indexar perfil genômico", e)

    metricas.incrementar("indexacoes")
    logger.info("Relatório indexado", extra={"evento": "indexacao", "chunks": n_chunks})
    return IndexResponse(status="indexed", chunks=n_chunks)


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    estado: EstadoIndexacao = Depends(get_estado),
    pipeline: GenomicRAGPipeline = Depends(get_pipeline),
) -> ChatResponse:
    if not estado.indexado:
        raise HTTPException(status_code=400, detail="Nenhum perfil genômico indexado. Chame /api/index primeiro.")

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Campo 'question' é obrigatório")

    inicio = time.perf_counter()
    try:
        response = pipeline.answer(question)
    except Exception as e:
        metricas.incrementar("erros_pergunta")
        raise erro_interno("Falha ao gerar resposta", e)

    latencia_ms = (time.perf_counter() - inicio) * 1000
    metricas.incrementar("perguntas")
    metricas.registrar_latencia(latencia_ms)
    if not response.grounded:
        metricas.incrementar("respostas_sem_ancoragem")

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

    return ChatResponse(
        answer=response.answer,
        grounded=response.grounded,
        sources=[
            FonteResposta(
                section=rc.chunk.section,
                subsection=rc.chunk.subsection,
                text=rc.chunk.text,
                score=rc.score,
            )
            for rc in response.retrieved_chunks
        ],
    )


@router.post("/reset", response_model=ResetResponse)
def reset(
    estado: EstadoIndexacao = Depends(get_estado),
    pipeline: GenomicRAGPipeline | None = Depends(get_pipeline_if_exists),
) -> ResetResponse:
    """Apaga o índice do paciente da memória. Os dados do app (SQLite) são apagados no próprio dispositivo."""
    if pipeline is not None:
        pipeline.limpar_indice()
    estado.indexado = False
    metricas.incrementar("resets")
    logger.info("Índice do paciente apagado a pedido do usuário", extra={"evento": "reset"})
    return ResetResponse(status="reset")
