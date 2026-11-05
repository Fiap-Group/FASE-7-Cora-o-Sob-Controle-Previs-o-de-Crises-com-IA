"""
=============================================================================
Esquemas (Pydantic) do sistema multiagente — Fase 6, Parte 2
=============================================================================
Usados como `output_type` dos agentes: a OpenAI Agents SDK força o LLM a
devolver uma estrutura validada, em vez de texto livre. `RecomendacaoFinal`
tem uma validação extra (`protocolos_sao_validos`) que rejeita qualquer
protocolo que não esteja na base conhecida — essa é a "validação de saída"
exigida pelo enunciado: pega o LLM inventando um protocolo que não existe.
=============================================================================
"""

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
        desconhecidos = set(self.protocolos) - set(PROTOCOLOS)
        if desconhecidos:
            raise ValueError(
                f"Protocolo(s) fora da base conhecida (possível alucinação do LLM): {desconhecidos}"
            )
        return self
