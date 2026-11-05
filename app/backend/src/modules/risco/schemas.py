"""Schemas HTTP próprios do módulo `risco` (diferente de
`shared/agentes/schemas.py`, que são schemas de domínio reaproveitados tanto
pelo módulo quanto pelos agentes). Esses aqui só existem pro shape da
resposta HTTP do endpoint de IoT."""

from datetime import datetime

from pydantic import BaseModel


class LeituraIotResponse(BaseModel):
    conectado: bool
    fc_media: float | None
    pa_sistolica: float | None
    spo2_media: float | None
    recebido_em: datetime | None
