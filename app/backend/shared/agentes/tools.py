"""
=============================================================================
Ferramentas (function_tool) dos agentes — Fase 6, Parte 2
=============================================================================
Pontes finas entre os agentes e o módulo preditivo (`shared/preditivo/`).
Nenhuma lógica de negócio mora aqui — só tradução de/para os esquemas
Pydantic que os agentes trocam entre si.
=============================================================================
"""

from agents import function_tool

from shared.agentes.schemas import AnaliseRisco, PacienteInput, ProtocolosResultado
from shared.preditivo.modelo import prever_risco
from shared.preditivo.protocolos import avaliar_protocolos


@function_tool
def ferramenta_prever_risco(paciente: PacienteInput) -> AnaliseRisco:
    """Consulta o modelo preditivo (PyTorch) e devolve a probabilidade e a
    classificação de pico de risco cardíaco pra este paciente."""
    probabilidade, classe = prever_risco(paciente.como_dict())
    return AnaliseRisco(
        probabilidade=probabilidade,
        classificacao="Alto risco" if classe == 1 else "Baixo risco",
    )


@function_tool
def ferramenta_buscar_protocolos(paciente: PacienteInput, pico_risco_previsto: int) -> ProtocolosResultado:
    """Consulta a base de protocolos simulada e devolve só os protocolos
    cuja condição real se aplica a este paciente. `pico_risco_previsto`
    deve ser a classe (0 ou 1) já calculada pelo Agente Analista de Risco."""
    return ProtocolosResultado(
        protocolos=avaliar_protocolos(paciente.como_dict(), pico_risco_previsto)
    )
