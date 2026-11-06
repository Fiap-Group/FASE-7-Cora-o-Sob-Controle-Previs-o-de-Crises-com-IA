import json
import logging

from agents import RunHooks, Runner
from opentelemetry import trace
from opentelemetry.trace import Span

from shared.agentes.definicoes import construir_agentes
from shared.agentes.schemas import RecomendacaoFinal

logger = logging.getLogger("genera_api")


class SpanPorAgenteHooks(RunHooks):
    """Abre um span OTel por agente durante o fluxo multiagente, pro Tempo rastrear cada etapa."""

    def __init__(self):
        self._tracer = trace.get_tracer("cardioia.agentes")
        self._spans: dict[str, Span] = {}

    async def on_agent_start(self, context, agent) -> None:
        logger.info("Agente iniciado: %s", agent.name, extra={"evento": "agente_inicio"})
        self._spans[agent.name] = self._tracer.start_span(agent.name)

    async def on_agent_end(self, context, agent, output) -> None:
        span = self._spans.pop(agent.name, None)
        if span:
            span.end()
        logger.info("Agente concluído: %s", agent.name, extra={"evento": "agente_fim"})


def avaliar_paciente(dados: dict) -> RecomendacaoFinal:
    orquestrador = construir_agentes()
    mensagem = json.dumps(dados, ensure_ascii=False)

    tracer = trace.get_tracer("cardioia.agentes")
    with tracer.start_as_current_span("multiagente.avaliar_paciente"):
        resultado = Runner.run_sync(orquestrador, input=mensagem, hooks=SpanPorAgenteHooks())
    saida = resultado.final_output

    if not isinstance(saida, RecomendacaoFinal):
        raise TypeError(
            f"Fluxo de agentes não terminou em RecomendacaoFinal (terminou em "
            f"{type(saida).__name__}). Ver resultado.final_output: {saida!r}"
        )
    return saida
