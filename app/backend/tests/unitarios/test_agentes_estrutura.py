import sys
from pathlib import Path
from typing import cast

import pytest

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from agents import Handoff  # noqa: E402

from shared.agentes.schemas import RecomendacaoFinal  # noqa: E402
from shared.preditivo.protocolos import PROTOCOLOS  # noqa: E402


@pytest.fixture(autouse=True)
def chave_gemini_falsa(monkeypatch: pytest.MonkeyPatch) -> None:
    """Define uma chave Gemini falsa e limpa o cache do cliente entre os testes."""
    monkeypatch.setenv("GEMINI_API_KEY", "chave-fake-de-teste")
    from shared.agentes.llm_config import obter_modelo_gemini
    obter_modelo_gemini.cache_clear()


def test_construir_todos_os_agentes_monta_os_4_agentes_exigidos_pelo_enunciado():
    """Testa que os 4 agentes exigidos são montados com os nomes esperados."""
    from shared.agentes.definicoes import construir_todos_os_agentes

    agentes = construir_todos_os_agentes()
    assert set(agentes) == {
        "orquestrador", "analista_risco", "especialista_protocolos", "planejador_resposta",
    }
    assert agentes["orquestrador"].name == "Agente Orquestrador"
    assert agentes["analista_risco"].name == "Agente Analista de Risco"
    assert agentes["especialista_protocolos"].name == "Agente Especialista em Protocolos"
    assert agentes["planejador_resposta"].name == "Agente Planejador de Resposta"


def test_construir_agentes_devolve_o_orquestrador():
    """Testa que construir_agentes() devolve o mesmo Orquestrador montado por construir_todos_os_agentes()."""
    from shared.agentes.definicoes import construir_agentes, construir_todos_os_agentes

    assert construir_agentes().name == construir_todos_os_agentes()["orquestrador"].name


def test_orquestrador_tem_handoff_pro_analista_de_risco():
    """Testa que o Orquestrador tem um único handoff para o Analista de Risco."""
    from shared.agentes.definicoes import construir_todos_os_agentes

    agentes = construir_todos_os_agentes()
    orquestrador = agentes["orquestrador"]
    assert len(orquestrador.handoffs) == 1
    assert cast(Handoff, orquestrador.handoffs[0]).agent_name == "Agente Analista de Risco"


def test_analista_de_risco_tem_a_ferramenta_de_previsao_e_handoff_pro_especialista():
    """Testa que o Analista de Risco tem a ferramenta de previsão e handoff para o Especialista."""
    from shared.agentes.definicoes import construir_todos_os_agentes

    analista = construir_todos_os_agentes()["analista_risco"]
    assert [tool.name for tool in analista.tools] == ["ferramenta_prever_risco"]
    assert cast(Handoff, analista.handoffs[0]).agent_name == "Agente Especialista em Protocolos"


def test_especialista_em_protocolos_tem_a_ferramenta_de_busca_e_handoff_pro_planejador():
    """Testa que o Especialista em Protocolos tem a ferramenta de busca e handoff para o Planejador."""
    from shared.agentes.definicoes import construir_todos_os_agentes

    especialista = construir_todos_os_agentes()["especialista_protocolos"]
    assert [tool.name for tool in especialista.tools] == ["ferramenta_buscar_protocolos"]
    assert cast(Handoff, especialista.handoffs[0]).agent_name == "Agente Planejador de Resposta"


def test_planejador_de_resposta_e_o_unico_com_output_type_recomendacao_final():
    """Testa que só o Planejador de Resposta tem output_type definido como RecomendacaoFinal."""
    from shared.agentes.definicoes import construir_todos_os_agentes

    agentes = construir_todos_os_agentes()
    assert agentes["planejador_resposta"].output_type is RecomendacaoFinal
    assert agentes["planejador_resposta"].handoffs == []
    for nome in ("orquestrador", "analista_risco", "especialista_protocolos"):
        assert agentes[nome].output_type is None


def test_recomendacao_final_aceita_protocolos_validos():
    """Testa que a RecomendacaoFinal aceita protocolos que pertencem à base conhecida."""
    recomendacao = RecomendacaoFinal(
        probabilidade=0.91,
        classificacao="Alto risco",
        protocolos=[PROTOCOLOS[1], PROTOCOLOS[9]],
        recomendacao="Acionar equipe e abrir unidades temporárias.",
    )
    assert recomendacao.protocolos == [PROTOCOLOS[1], PROTOCOLOS[9]]


def test_recomendacao_final_rejeita_protocolo_fora_da_base_conhecida():
    """Testa que a RecomendacaoFinal rejeita um protocolo fora da base conhecida."""
    with pytest.raises(ValueError, match="fora da base conhecida"):
        RecomendacaoFinal(
            probabilidade=0.5,
            classificacao="Baixo risco",
            protocolos=["Se o paciente parecer nervoso → chamar um psicólogo"],
            recomendacao="Texto inventado pelo LLM.",
        )
