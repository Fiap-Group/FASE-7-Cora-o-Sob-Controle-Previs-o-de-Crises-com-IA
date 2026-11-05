import os
from functools import lru_cache

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

set_tracing_disabled(True)


@lru_cache(maxsize=1)
def obter_modelo_gemini() -> OpenAIChatCompletionsModel:
    """Cria, uma única vez, o cliente do modelo Gemini usado pelos agentes."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY não definido — necessário pra rodar os agentes "
            "(ver app/backend/.env.example)."
        )
    cliente = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=api_key)
    modelo = os.getenv("LLM_MODEL") or "gemini-3.6-flash"
    return OpenAIChatCompletionsModel(model=modelo, openai_client=cliente)
