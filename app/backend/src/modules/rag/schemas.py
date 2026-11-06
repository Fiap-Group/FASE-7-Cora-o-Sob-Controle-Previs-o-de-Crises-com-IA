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
