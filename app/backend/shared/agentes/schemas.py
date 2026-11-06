from typing import Literal

from pydantic import BaseModel, model_validator

from shared.preditivo.dataset import COLUNAS_FEATURES
from shared.preditivo.protocolos import PROTOCOLOS


class PacienteInput(BaseModel):
    idade_media: float
    carga_sistema: float
    tempo_espera: float
    fc_media: float
    spo2_media: float
    pa_sistolica: float
    temperatura: float
    densidade_eventos: float
    eventos_24h: float
    disponibilidade_recursos: float

    def como_dict(self) -> dict[str, float]:
        """Converte os dados do paciente num dicionário com as colunas usadas pelo modelo."""
        return {coluna: getattr(self, coluna) for coluna in COLUNAS_FEATURES}


class AnaliseRisco(BaseModel):
    probabilidade: float
    classificacao: Literal["Alto risco", "Baixo risco"]


class ProtocolosResultado(BaseModel):
    protocolos: list[str]


class RecomendacaoFinal(BaseModel):
    probabilidade: float
    classificacao: Literal["Alto risco", "Baixo risco"]
    protocolos: list[str]
    recomendacao: str

    @model_validator(mode="after")
    def protocolos_sao_validos(self) -> "RecomendacaoFinal":
        """Garante que todos os protocolos recomendados pertencem à base conhecida."""
        desconhecidos = set(self.protocolos) - set(PROTOCOLOS)
        if desconhecidos:
            raise ValueError(
                f"Protocolo(s) fora da base conhecida (possível alucinação do LLM): {desconhecidos}"
            )
        return self
