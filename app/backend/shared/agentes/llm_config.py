import itertools
import os
from functools import lru_cache

import httpx2
from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

from shared.chaves_llm import ler_chaves_gemini

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

set_tracing_disabled(True)


class _TransporteComRotacaoDeChave(httpx2.AsyncHTTPTransport):
    """Distribui as chamadas entre várias chaves do Gemini (round-robin) e, se uma delas
    devolver 429/503 (cota esgotada ou sobrecarga), tenta de novo com a próxima antes de
    desistir — cada chave vem de uma conta Google diferente, com cota própria.

    Usa httpx2 (não httpx) porque é o que a versão instalada do `openai` espera no
    `http_client` do AsyncOpenAI neste projeto."""

    def __init__(self, chaves: list[str]):
        super().__init__()
        self._chaves = chaves
        self._contador = itertools.count()

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        resposta = await super().handle_async_request(self._com_proxima_chave(request))
        for _ in range(len(self._chaves) - 1):
            if resposta.status_code not in (429, 503):
                return resposta
            await resposta.aread()
            resposta = await super().handle_async_request(self._com_proxima_chave(request))
        return resposta

    def _com_proxima_chave(self, request: httpx2.Request) -> httpx2.Request:
        chave = self._chaves[next(self._contador) % len(self._chaves)]
        request.headers["authorization"] = f"Bearer {chave}"
        return request


@lru_cache(maxsize=1)
def obter_modelo_gemini() -> OpenAIChatCompletionsModel:
    """Cria, uma única vez, o cliente do modelo Gemini usado pelos agentes — rotacionando
    entre todas as chaves de GEMINI_API_KEYS/GEMINI_API_KEY (ver shared/chaves_llm.py)."""
    chaves = ler_chaves_gemini()
    cliente_http = httpx2.AsyncClient(transport=_TransporteComRotacaoDeChave(chaves))
    cliente = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=chaves[0], http_client=cliente_http)
    modelo = os.getenv("LLM_MODEL") or "gemini-3.6-flash"
    return OpenAIChatCompletionsModel(model=modelo, openai_client=cliente)
