"""
=============================================================================
Esquemas (Pydantic) do módulo RAG
=============================================================================
Request/response dos endpoints de `router.py`. Equivalente aos DTOs de um
controller do Nest — a diferença é que aqui a validação e a documentação
(Swagger) saem de graça, só por declarar o tipo.
=============================================================================
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str = ""


class FonteResposta(BaseModel):
    section: str
    subsection: str | None
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    grounded: bool
    sources: list[FonteResposta]


class IndexResponse(BaseModel):
    status: str
    chunks: int


class HealthResponse(BaseModel):
    status: str
    paciente_indexado: bool
    llm: str
    uptime_s: int


class ResetResponse(BaseModel):
    status: str
