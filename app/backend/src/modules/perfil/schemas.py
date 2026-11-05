"""Schemas HTTP do módulo `perfil` — a "ficha de jogador" montada a
partir da conta (shared/models.py:Usuario) e do histórico de avaliações
(shared/models.py:HistoricoRisco)."""

from datetime import datetime

from pydantic import BaseModel

from src.modules.auth.schemas import UsuarioResponse


class AvaliacaoResumo(BaseModel):
    """Montado campo a campo em `service.py` a partir de um
    `HistoricoRisco` (não via `from_attributes`): os nomes de coluna
    (`dados_json`/`protocolos_json`) não batem com os do schema
    (`dados`/`protocolos`) de propósito — aqui é o shape da API."""

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
