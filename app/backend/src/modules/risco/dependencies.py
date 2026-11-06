from typing import Callable

from shared.agentes.orquestracao import avaliar_paciente
from shared.agentes.schemas import RecomendacaoFinal


def get_avaliador_risco() -> Callable[[dict], RecomendacaoFinal]:
    return avaliar_paciente
