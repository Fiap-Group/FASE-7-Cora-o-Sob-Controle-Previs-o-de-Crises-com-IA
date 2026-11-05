import logging

from fastapi import HTTPException

from shared.observabilidade import metricas


def erro_interno(logger: logging.Logger, contexto: str, excecao: Exception, status: int = 500) -> HTTPException:
    """Loga o erro completo no servidor e devolve ao cliente só uma mensagem genérica."""
    logger.exception(contexto, extra={"evento": "erro", "erro_tipo": type(excecao).__name__})
    metricas.registrar_erro(f"{contexto}: {type(excecao).__name__}")
    return HTTPException(status_code=status, detail=contexto)
