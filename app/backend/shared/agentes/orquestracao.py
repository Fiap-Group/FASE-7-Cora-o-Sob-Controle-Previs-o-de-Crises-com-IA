"""
=============================================================================
Ponto de entrada do fluxo multiagente — Fase 6, Parte 2
=============================================================================
`avaliar_paciente` é o ÚNICO lugar do sistema que chama `Runner.run` — e
chama sempre no Orquestrador, nunca direto num agente do meio da cadeia.
Isso garante que os handoffs (Orquestrador -> Analista de Risco ->
Especialista em Protocolos -> Planejador de Resposta) são de fato
exercitados, não só configurados e ignorados.
=============================================================================
"""

import json

from agents import Runner

from shared.agentes.definicoes import construir_agentes
from shared.agentes.schemas import RecomendacaoFinal


def avaliar_paciente(dados: dict) -> RecomendacaoFinal:
    """Roda o fluxo completo (Orquestrador -> ... -> Planejador de Resposta)
    pra um paciente e devolve a recomendação final estruturada e validada."""
    orquestrador = construir_agentes()
    mensagem = json.dumps(dados, ensure_ascii=False)

    resultado = Runner.run_sync(orquestrador, input=mensagem)
    saida = resultado.final_output

    if not isinstance(saida, RecomendacaoFinal):
        raise TypeError(
            f"Fluxo de agentes não terminou em RecomendacaoFinal (terminou em "
            f"{type(saida).__name__}). Ver resultado.final_output: {saida!r}"
        )
    return saida


def formatar_saida(resultado: RecomendacaoFinal) -> str:
    """Formato de saída pedido pelo enunciado: 'RISCO PREVISTO: 0.91' seguido
    da lista de protocolos sugeridos."""
    linhas_protocolos = "\n".join(f"- {p}" for p in resultado.protocolos)
    return (
        f"RISCO PREVISTO: {resultado.probabilidade:.2f}\n\n"
        f"PROTOCOLOS SUGERIDOS:\n{linhas_protocolos}"
    )
