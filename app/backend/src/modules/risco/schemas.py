"""Schemas HTTP próprios do módulo `risco` (diferente de
`shared/agentes/schemas.py`, que são schemas de domínio reaproveitados tanto
pelo módulo quanto pelos agentes). Esses aqui só existem pro shape da
resposta HTTP do endpoint de IoT e pro corpo de /avaliar."""

from datetime import datetime

from pydantic import BaseModel

from shared.agentes.schemas import PacienteInput


class LeituraIotResponse(BaseModel):
    conectado: bool
    fc_media: float | None
    pa_sistolica: float | None
    spo2_media: float | None
    recebido_em: datetime | None


class AvaliarRiscoRequest(PacienteInput):
    """`usuario_id` é opcional pra não quebrar quem já chamava o endpoint
    sem usuário — `PacienteInput.como_dict()` só lê as 10 colunas
    conhecidas, então esse campo extra não chega a ir pro agente, só é
    usado aqui no router pra decidir se grava o HistoricoRisco."""

    usuario_id: int | None = None
