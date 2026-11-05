from datetime import datetime

from pydantic import BaseModel

from src.modules.auth.schemas import UsuarioResponse


class AvaliacaoResumo(BaseModel):
    """Resumo de uma avaliação de risco concluída, no shape exposto pela API."""

    criado_em: datetime
    probabilidade: float
    classificacao: str
    dados: dict[str, float]
    protocolos: list[str]
    recomendacao: str


class PerfilResponse(BaseModel):
    """Ficha de jogador do usuário: conta, avaliação mais recente e histórico."""

    usuario: UsuarioResponse
    avaliacao_mais_recente: AvaliacaoResumo | None
    historico: list[AvaliacaoResumo]
