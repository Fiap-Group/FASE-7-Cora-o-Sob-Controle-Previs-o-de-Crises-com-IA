import json

from agents import Runner

from shared.agentes.definicoes import construir_agentes
from shared.agentes.schemas import RecomendacaoFinal


def avaliar_paciente(dados: dict) -> RecomendacaoFinal:
    """Roda o fluxo completo de agentes para um paciente e devolve a recomendação final validada."""
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
    """Formata a recomendação final em texto, com o risco previsto e os protocolos sugeridos."""
    linhas_protocolos = "\n".join(f"- {p}" for p in resultado.protocolos)
    return (
        f"RISCO PREVISTO: {resultado.probabilidade:.2f}\n\n"
        f"PROTOCOLOS SUGERIDOS:\n{linhas_protocolos}"
    )
