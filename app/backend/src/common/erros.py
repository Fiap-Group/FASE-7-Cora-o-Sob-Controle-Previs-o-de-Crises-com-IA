"""
=============================================================================
Helper de erro HTTP compartilhado entre os módulos (src/modules/*)
=============================================================================
Fica em `src/` (não em `shared/`) porque depende do FastAPI — `shared/`
continua livre de dependência de framework web, usada também por scripts
fora de um contexto HTTP (treinar.py, demo.py).
=============================================================================
"""

import logging

from fastapi import HTTPException

from shared.observabilidade import metricas


def erro_interno(logger: logging.Logger, contexto: str, excecao: Exception, status: int = 500) -> HTTPException:
    """Loga o erro completo no servidor e devolve ao cliente só uma mensagem genérica."""
    logger.exception(contexto, extra={"evento": "erro", "erro_tipo": type(excecao).__name__})
    metricas.registrar_erro(f"{contexto}: {type(excecao).__name__}")
    return HTTPException(status_code=status, detail=contexto)
