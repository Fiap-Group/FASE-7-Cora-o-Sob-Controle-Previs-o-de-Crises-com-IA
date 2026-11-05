"""
=============================================================================
Controller do módulo de risco cardíaco (equivalente a um @Controller do Nest)
=============================================================================
Expõe o fluxo multiagente (shared/agentes/) como endpoint HTTP: recebe os
dados de operação hospitalar, roda a cadeia Orquestrador -> Analista de
Risco -> Especialista em Protocolos -> Planejador de Resposta, e devolve a
recomendação final já validada.

Endpoints:
    POST /api/risco/avaliar    recebe PacienteInput, devolve RecomendacaoFinal
=============================================================================
"""

import logging
from typing import Callable

from fastapi import APIRouter, Depends

from shared.agentes.schemas import PacienteInput, RecomendacaoFinal

from src.common.erros import erro_interno

from .dependencies import get_avaliador_risco

logger = logging.getLogger("genera_api")

router = APIRouter(prefix="/api/risco", tags=["risco"])


@router.post("/avaliar", response_model=RecomendacaoFinal)
def avaliar_risco(
    paciente: PacienteInput,
    avaliador: Callable[[dict], RecomendacaoFinal] = Depends(get_avaliador_risco),
) -> RecomendacaoFinal:
    """Roda o fluxo multiagente completo para os dados de operação recebidos.

    A rota é `def` síncrona (não `async def`) de propósito: `avaliar_paciente`
    chama `Runner.run_sync`, que roda seu próprio `asyncio.run()` por dentro —
    isso só funciona numa thread sem event loop já ativo. Rotas `def` no
    FastAPI são despachadas pro threadpool, igual já acontece hoje quando o
    `demo.py` ou os testes chamam `avaliar_paciente` fora de um `async def`.
    """
    try:
        return avaliador(paciente.como_dict())
    except Exception as e:
        raise erro_interno(logger, "Falha ao avaliar risco cardíaco", e)
