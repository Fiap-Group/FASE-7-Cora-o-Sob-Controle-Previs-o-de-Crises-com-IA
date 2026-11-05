"""
Testes estruturais do sistema multiagente (Fase 6, Parte 2): wiring dos 4
agentes/handoffs e validação dos esquemas Pydantic. Nenhum teste aqui chama
o Gemini de verdade — usamos uma chave falsa, já que `Agent`/`Runner` não
fazem nenhuma chamada de rede só de serem construídos.

Rodar com: pytest tests/test_agentes_estrutura.py
"""

import sys
from pathlib import Path
from typing import cast

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from agents import Handoff  # noqa: E402

from shared.agentes.schemas import RecomendacaoFinal  # noqa: E402
from shared.preditivo.protocolos import PROTOCOLOS  # noqa: E402


@pytest.fixture(autouse=True)
def chave_gemini_falsa(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "chave-fake-de-teste")
    # construir_agentes()/construir_todos_os_agentes() usam um @lru_cache em
    # obter_modelo_gemini() — limpa entre os testes pra não reaproveitar um
    # cliente construído com outra chave.
    from shared.agentes.llm_config import obter_modelo_gemini
    obter_modelo_gemini.cache_clear()


def test_construir_todos_os_agentes_monta_os_4_agentes_exigidos_pelo_enunciado():
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
    from shared.agentes.definicoes import construir_agentes, construir_todos_os_agentes

    assert construir_agentes().name == construir_todos_os_agentes()["orquestrador"].name


def test_orquestrador_tem_handoff_pro_analista_de_risco():
    from shared.agentes.definicoes import construir_todos_os_agentes

    agentes = construir_todos_os_agentes()
    orquestrador = agentes["orquestrador"]
    assert len(orquestrador.handoffs) == 1
    assert cast(Handoff, orquestrador.handoffs[0]).agent_name == "Agente Analista de Risco"


def test_analista_de_risco_tem_a_ferramenta_de_previsao_e_handoff_pro_especialista():
    from shared.agentes.definicoes import construir_todos_os_agentes

    analista = construir_todos_os_agentes()["analista_risco"]
    assert [tool.name for tool in analista.tools] == ["ferramenta_prever_risco"]
    assert cast(Handoff, analista.handoffs[0]).agent_name == "Agente Especialista em Protocolos"


def test_especialista_em_protocolos_tem_a_ferramenta_de_busca_e_handoff_pro_planejador():
    from shared.agentes.definicoes import construir_todos_os_agentes

    especialista = construir_todos_os_agentes()["especialista_protocolos"]
    assert [tool.name for tool in especialista.tools] == ["ferramenta_buscar_protocolos"]
    assert cast(Handoff, especialista.handoffs[0]).agent_name == "Agente Planejador de Resposta"


def test_planejador_de_resposta_e_o_unico_com_output_type_recomendacao_final():
    from shared.agentes.definicoes import construir_todos_os_agentes

    agentes = construir_todos_os_agentes()
    assert agentes["planejador_resposta"].output_type is RecomendacaoFinal
    assert agentes["planejador_resposta"].handoffs == []
    for nome in ("orquestrador", "analista_risco", "especialista_protocolos"):
        assert agentes[nome].output_type is None


# --- Validação de saída (RecomendacaoFinal) -----------------------------------

def test_recomendacao_final_aceita_protocolos_validos():
    recomendacao = RecomendacaoFinal(
        probabilidade=0.91,
        classificacao="Alto risco",
        protocolos=[PROTOCOLOS[1], PROTOCOLOS[9]],
        recomendacao="Acionar equipe e abrir unidades temporárias.",
    )
    assert recomendacao.protocolos == [PROTOCOLOS[1], PROTOCOLOS[9]]


def test_recomendacao_final_rejeita_protocolo_fora_da_base_conhecida():
    with pytest.raises(ValueError, match="fora da base conhecida"):
        RecomendacaoFinal(
            probabilidade=0.5,
            classificacao="Baixo risco",
            protocolos=["Se o paciente parecer nervoso → chamar um psicólogo"],
            recomendacao="Texto inventado pelo LLM.",
        )
