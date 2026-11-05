from agents import function_tool

from shared.agentes.schemas import AnaliseRisco, PacienteInput, ProtocolosResultado
from shared.preditivo.modelo import prever_risco
from shared.preditivo.protocolos import avaliar_protocolos


@function_tool
def ferramenta_prever_risco(paciente: PacienteInput) -> AnaliseRisco:
    """Consulta o modelo preditivo e devolve a probabilidade e a classificação de risco cardíaco do paciente."""
    probabilidade, classe = prever_risco(paciente.como_dict())
    return AnaliseRisco(
        probabilidade=probabilidade,
        classificacao="Alto risco" if classe == 1 else "Baixo risco",
    )


@function_tool
def ferramenta_buscar_protocolos(paciente: PacienteInput, pico_risco_previsto: int) -> ProtocolosResultado:
    """Consulta a base de protocolos e devolve só os que se aplicam a este paciente."""
    return ProtocolosResultado(
        protocolos=avaliar_protocolos(paciente.como_dict(), pico_risco_previsto)
    )
