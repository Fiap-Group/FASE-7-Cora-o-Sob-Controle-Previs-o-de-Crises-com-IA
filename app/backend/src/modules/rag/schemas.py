from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Pergunta enviada pelo paciente ao chat do RAG."""

    question: str = ""


class FonteResposta(BaseModel):
    """Um trecho do perfil genômico usado como fonte de uma resposta."""

    section: str
    subsection: str | None
    text: str
    score: float


class ChatResponse(BaseModel):
    """Resposta do chat, com o texto gerado, suas fontes e se está ancorada no contexto."""

    answer: str
    grounded: bool
    sources: list[FonteResposta]


class IndexResponse(BaseModel):
    """Resultado da indexação de um perfil genômico."""

    status: str
    chunks: int


class HealthResponse(BaseModel):
    """Status atual da API, incluindo se há relatório indexado e qual LLM está em uso."""

    status: str
    paciente_indexado: bool
    llm: str
    uptime_s: int


class ResetResponse(BaseModel):
    """Confirmação de que o índice do paciente foi apagado."""

    status: str
