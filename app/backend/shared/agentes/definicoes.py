from agents import Agent, handoff

from shared.agentes.llm_config import obter_modelo_gemini
from shared.agentes.schemas import RecomendacaoFinal
from shared.agentes.tools import ferramenta_buscar_protocolos, ferramenta_prever_risco


def construir_todos_os_agentes() -> dict[str, Agent]:
    modelo = obter_modelo_gemini()

    planejador_resposta = Agent(
        name="Agente Planejador de Resposta",
        model=modelo,
        instructions=(
            "Você é o Agente Planejador de Resposta do sistema CardioIA. "
            "No histórico da conversa, o Agente Analista de Risco já informou a "
            "probabilidade e a classificação de risco, e o Agente Especialista "
            "em Protocolos já informou os protocolos aplicáveis. "
            "Consolide essas informações numa RecomendacaoFinal: repita a "
            "probabilidade e a classificação exatamente como foram informadas, "
            "repita a lista de protocolos exatamente como foi informada (nunca "
            "invente um protocolo que não esteja nessa lista), e escreva uma "
            "recomendação operacional curta (1-2 frases) com base nelas."
        ),
        output_type=RecomendacaoFinal,
    )

    especialista_protocolos = Agent(
        name="Agente Especialista em Protocolos",
        model=modelo,
        tools=[ferramenta_buscar_protocolos],
        instructions=(
            "Você é o Agente Especialista em Protocolos do sistema CardioIA. "
            "No histórico da conversa, o Agente Analista de Risco já informou os "
            "dados do paciente e a classificação de risco (Alto risco = 1, "
            "Baixo risco = 0). Use a ferramenta ferramenta_buscar_protocolos com "
            "os dados do paciente e esse valor (pico_risco_previsto). Não invente "
            "protocolos que a ferramenta não retornou. Depois de ter o resultado "
            "da ferramenta, faça handoff para o Agente Planejador de Resposta, "
            "informando a probabilidade, a classificação e os protocolos "
            "encontrados."
        ),
        handoffs=[handoff(planejador_resposta)],
    )

    analista_risco = Agent(
        name="Agente Analista de Risco",
        model=modelo,
        tools=[ferramenta_prever_risco],
        instructions=(
            "Você é o Agente Analista de Risco do sistema CardioIA. Receba os "
            "dados do paciente (JSON) da mensagem do usuário e use a ferramenta "
            "ferramenta_prever_risco com esses dados. Nunca invente uma "
            "probabilidade ou classificação — use sempre o resultado da "
            "ferramenta. Depois, faça handoff para o Agente Especialista em "
            "Protocolos, informando os dados do paciente, a probabilidade e a "
            "classificação obtidas (e o valor 1 para Alto risco ou 0 para Baixo "
            "risco, como pico_risco_previsto)."
        ),
        handoffs=[handoff(especialista_protocolos)],
    )

    orquestrador = Agent(
        name="Agente Orquestrador",
        model=modelo,
        instructions=(
            "Você é o Agente Orquestrador do sistema CardioIA. Receba os dados "
            "de um paciente (JSON) e faça handoff imediato para o Agente "
            "Analista de Risco, passando os dados adiante sem processá-los você "
            "mesmo."
        ),
        handoffs=[handoff(analista_risco)],
    )

    return {
        "orquestrador": orquestrador,
        "analista_risco": analista_risco,
        "especialista_protocolos": especialista_protocolos,
        "planejador_resposta": planejador_resposta,
    }


def construir_agentes() -> Agent:
    """Ponto de entrada do fluxo real: devolve só o Agente Orquestrador."""
    return construir_todos_os_agentes()["orquestrador"]
