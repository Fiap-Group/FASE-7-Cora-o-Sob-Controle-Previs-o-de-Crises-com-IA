"""
=============================================================================
Configuração do LLM dos agentes — Gemini via endpoint compatível com OpenAI
=============================================================================
A OpenAI Agents SDK (`agents`) espera um modelo compatível com a API de
chat da OpenAI. O Gemini expõe um endpoint compatível
(`v1beta/openai/`), então apontamos a SDK pra lá em vez de usar o backend
Ollama local que uma entrega anterior usava — reaproveita a mesma
`GEMINI_API_KEY`/`LLM_MODEL` já usada pelo RAG (`shared/rag_system.py`).

Nada aqui chama a rede na importação do módulo (`obter_modelo_gemini` é
`lru_cache`, só constrói o cliente na primeira chamada) — isso permite
importar `shared.agentes.*` em testes estruturais sem precisar de uma
chave real.
=============================================================================
"""

import os
from functools import lru_cache

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Não estamos usando a plataforma da OpenAI (dashboard/tracing) — evita
# erro/ruído de tracing tentando mandar telemetria pra lá.
set_tracing_disabled(True)


@lru_cache(maxsize=1)
def obter_modelo_gemini() -> OpenAIChatCompletionsModel:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY não definido — necessário pra rodar os agentes "
            "(ver app/backend/.env.example)."
        )
    cliente = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=api_key)
    # `or`, não o default de getenv: o .env do time deixa LLM_MODEL em
    # branco de propósito (o rag_system.py já tem seu próprio default), e
    # getenv("LLM_MODEL", "...") só usaria o default se a variável nem
    # existisse — com ela vazia, mandaria model="" pro Gemini.
    modelo = os.getenv("LLM_MODEL") or "gemini-3.6-flash"
    return OpenAIChatCompletionsModel(model=modelo, openai_client=cliente)
