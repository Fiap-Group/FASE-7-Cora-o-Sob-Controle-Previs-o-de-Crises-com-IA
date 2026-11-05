"""
=============================================================================
Providers do módulo de risco cardíaco (equivalente aos providers do @Module do Nest)
=============================================================================
`get_avaliador_risco` é injetado na rota via `Depends(get_avaliador_risco)` —
mesmo motivo de `get_pipeline` em `src/modules/rag/dependencies.py`: os
testes substituem essa dependência por uma função fake via
`app.dependency_overrides`, sem chamar o Gemini de verdade.
=============================================================================
"""

from typing import Callable

from shared.agentes.orquestracao import avaliar_paciente
from shared.agentes.schemas import RecomendacaoFinal


def get_avaliador_risco() -> Callable[[dict], RecomendacaoFinal]:
    return avaliar_paciente
