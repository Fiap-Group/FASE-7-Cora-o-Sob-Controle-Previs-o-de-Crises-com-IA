"""
=============================================================================
Definição dos 4 agentes — Fase 6, Parte 2
=============================================================================
Cadeia linear de handoffs (cada agente só encaminha pro próximo, nunca
volta pro anterior — mais fácil de um LLM seguir de forma confiável do que
um hub-and-spoke que teria que voltar pro Orquestrador):

    Orquestrador
        -> Agente Analista de Risco        (tool: ferramenta_prever_risco)
        -> Agente Especialista em Protocolos (tool: ferramenta_buscar_protocolos)
        -> Agente Planejador de Resposta     (output_type: RecomendacaoFinal)

Isso é diferente de uma entrega anterior, que criava o Orquestrador com
handoffs configurados mas nunca de fato chamava `Runner.run` nele — aqui
`orquestracao.py` chama `Runner.run` só no Orquestrador, então os handoffs
sempre são exercitados de verdade.
=============================================================================
"""

from agents import Agent, handoff

from shared.agentes.llm_config import obter_modelo_gemini
from shared.agentes.schemas import RecomendacaoFinal
from shared.agentes.tools import ferramenta_buscar_protocolos, ferramenta_prever_risco


def construir_todos_os_agentes() -> dict[str, Agent]:
    """Monta os 4 agentes e devolve todos eles, nomeados — útil pra testes
    estruturais, que não têm como inspecionar o agente de destino de dentro
    de um `Handoff` (a SDK não expõe isso como atributo público). Quem só
    precisa rodar o fluxo usa `construir_agentes()`, que devolve só o
    Orquestrador."""
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
    """Ponto de entrada do fluxo real: só o Orquestrador (os outros 3
    agentes são alcançados por handoff, a partir dele)."""
    return construir_todos_os_agentes()["orquestrador"]
