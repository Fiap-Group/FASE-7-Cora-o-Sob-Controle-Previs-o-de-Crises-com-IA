from typing import Callable

from shared.agentes.orquestracao import avaliar_paciente
from shared.agentes.schemas import RecomendacaoFinal


def get_avaliador_risco() -> Callable[[dict], RecomendacaoFinal]:
    """Devolve a função que roda o fluxo multiagente de avaliação de risco."""
    return avaliar_paciente
