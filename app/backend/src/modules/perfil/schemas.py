from datetime import datetime

from pydantic import BaseModel

from src.modules.auth.schemas import UsuarioResponse


class AvaliacaoResumo(BaseModel):
    criado_em: datetime
    probabilidade: float
    classificacao: str
    dados: dict[str, float]
    protocolos: list[str]
    recomendacao: str


class PerfilResponse(BaseModel):
    usuario: UsuarioResponse
    avaliacao_mais_recente: AvaliacaoResumo | None
    historico: list[AvaliacaoResumo]
