from datetime import datetime

from pydantic import BaseModel

from shared.agentes.schemas import PacienteInput


class LeituraIotResponse(BaseModel):
    """Última leitura de sinais vitais recebida do ESP32, no shape da API."""

    conectado: bool
    fc_media: float | None
    pa_sistolica: float | None
    spo2_media: float | None
    recebido_em: datetime | None


class AvaliarRiscoRequest(PacienteInput):
    """Dados de entrada para avaliar o risco cardíaco, com o usuário opcionalmente identificado."""

    usuario_id: int | None = None
