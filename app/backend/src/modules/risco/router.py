"""
=============================================================================
Controller do módulo de risco cardíaco (equivalente a um @Controller do Nest)
=============================================================================
Expõe o fluxo multiagente (shared/agentes/) como endpoint HTTP: recebe os
dados de operação hospitalar, roda a cadeia Orquestrador -> Analista de
Risco -> Especialista em Protocolos -> Planejador de Resposta, e devolve a
recomendação final já validada.

Endpoints:
    POST /api/risco/avaliar       recebe PacienteInput, devolve RecomendacaoFinal
    GET  /api/risco/leitura-iot   última leitura publicada pelo ESP32 via MQTT
=============================================================================
"""

import logging
from typing import Callable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.agentes.schemas import RecomendacaoFinal
from shared.db import get_db
from shared.models import HistoricoRisco

from src.common.erros import erro_interno

from .dependencies import get_avaliador_risco
from .mqtt_listener import LeituraIot, get_leitura_iot
from .schemas import AvaliarRiscoRequest, LeituraIotResponse

logger = logging.getLogger("genera_api")

router = APIRouter(prefix="/api/risco", tags=["risco"])


@router.post("/avaliar", response_model=RecomendacaoFinal)
def avaliar_risco(
    paciente: AvaliarRiscoRequest,
    avaliador: Callable[[dict], RecomendacaoFinal] = Depends(get_avaliador_risco),
    db: Session = Depends(get_db),
) -> RecomendacaoFinal:
    """Roda o fluxo multiagente completo para os dados de operação recebidos.

    A rota é `def` síncrona (não `async def`) de propósito: `avaliar_paciente`
    chama `Runner.run_sync`, que roda seu próprio `asyncio.run()` por dentro —
    isso só funciona numa thread sem event loop já ativo. Rotas `def` no
    FastAPI são despachadas pro threadpool, igual já acontece hoje quando o
    `demo.py` ou os testes chamam `avaliar_paciente` fora de um `async def`.
    """
    try:
        recomendacao = avaliador(paciente.como_dict())
    except Exception as e:
        raise erro_interno(logger, "Falha ao avaliar risco cardíaco", e)

    if paciente.usuario_id is not None:
        _registrar_historico(db, paciente, recomendacao)

    return recomendacao


def _registrar_historico(db: Session, paciente: AvaliarRiscoRequest, recomendacao: RecomendacaoFinal) -> None:
    """Alimenta o "Perfil" gamificado (src/modules/perfil). Falha aqui não
    pode derrubar a resposta da avaliação — mesmo espírito de "infra
    opcional não quebra o que já funcionava" do listener MQTT."""
    try:
        db.add(
            HistoricoRisco(
                usuario_id=paciente.usuario_id,
                dados_json=paciente.como_dict(),
                probabilidade=recomendacao.probabilidade,
                classificacao=recomendacao.classificacao,
                protocolos_json=recomendacao.protocolos,
                recomendacao=recomendacao.recomendacao,
            )
        )
        db.commit()
    except Exception as e:
        logger.warning("Falha ao gravar histórico de risco: %s", e, extra={"evento": "historico_risco_erro"})


@router.get("/leitura-iot", response_model=LeituraIotResponse)
def leitura_iot(leitura: LeituraIot = Depends(get_leitura_iot)) -> LeituraIotResponse:
    """Snapshot em memória da última mensagem MQTT recebida do ESP32 — não
    chama o modelo nem os agentes, só expõe o que já está guardado."""
    return LeituraIotResponse(
        conectado=leitura.conectado,
        fc_media=leitura.fc_media,
        pa_sistolica=leitura.pa_sistolica,
        spo2_media=leitura.spo2_media,
        recebido_em=leitura.recebido_em,
    )
