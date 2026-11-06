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
    usuario_id: int | None = None
