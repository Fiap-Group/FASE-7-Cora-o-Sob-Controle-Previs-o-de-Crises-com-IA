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
    avaliador: Callable[[dict[str, float]], RecomendacaoFinal] = Depends(get_avaliador_risco),
    db: Session = Depends(get_db),
) -> RecomendacaoFinal:
    try:
        recomendacao = avaliador(paciente.como_dict())
    except Exception as e:
        raise erro_interno(logger, "Falha ao avaliar risco cardíaco", e)

    if paciente.usuario_id is not None:
        _registrar_historico(db, paciente, recomendacao)

    return recomendacao


def _registrar_historico(db: Session, paciente: AvaliarRiscoRequest, recomendacao: RecomendacaoFinal) -> None:
    """Grava a avaliação no histórico do usuário, sem derrubar a resposta se isso falhar."""
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
    return LeituraIotResponse(
        conectado=leitura.conectado,
        fc_media=leitura.fc_media,
        pa_sistolica=leitura.pa_sistolica,
        spo2_media=leitura.spo2_media,
        recebido_em=leitura.recebido_em,
    )
