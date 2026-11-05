import sys
from pathlib import Path
from typing import cast

import pandas as pd
import pytest

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from shared.preditivo.dataset import COLUNA_ALVO, COLUNAS_FEATURES, gerar_base_sintetica  # noqa: E402
from shared.preditivo.modelo import prever_risco, treinar_modelo  # noqa: E402
from shared.preditivo.protocolos import PROTOCOLOS, avaliar_protocolos  # noqa: E402

NOVO_CASO = {
    "idade_media": 62,
    "carga_sistema": 92,
    "tempo_espera": 75,
    "fc_media": 118,
    "spo2_media": 89,
    "pa_sistolica": 100,
    "temperatura": 37.5,
    "densidade_eventos": 7,
    "eventos_24h": 5,
    "disponibilidade_recursos": 25,
}


def test_gerar_base_sintetica_tem_5000_linhas_e_as_11_colunas_esperadas():
    """Testa que a base sintética tem o número de linhas e as colunas esperadas."""
    df = gerar_base_sintetica(n=5000, seed=42)
    assert len(df) == 5000
    assert list(df.columns) == [*COLUNAS_FEATURES, COLUNA_ALVO]


def test_pico_risco_nao_fica_todo_numa_classe_so():
    """Testa que o alvo pico_risco não fica concentrado numa única classe."""
    df = gerar_base_sintetica(n=5000, seed=42)
    coluna_alvo = cast(pd.Series, df[COLUNA_ALVO])
    media = float(coluna_alvo.mean())
    assert 0.05 < media < 0.95


def test_gerar_base_sintetica_e_reprodutivel_com_a_mesma_seed():
    """Testa que gerar a base com a mesma seed produz sempre o mesmo resultado."""
    df1 = gerar_base_sintetica(n=200, seed=7)
    df2 = gerar_base_sintetica(n=200, seed=7)
    assert df1.equals(df2)


def test_modelo_treinado_tem_acuracia_alta():
    """Testa que o modelo treinado atinge uma acurácia alta na base sintética."""
    df = gerar_base_sintetica(n=5000, seed=42)
    _, _, _, metricas = treinar_modelo(df, seed=42)
    assert metricas["acuracia"] > 0.90


def test_prever_risco_contra_o_checkpoint_comitado():
    """Testa a predição de risco usando o checkpoint do modelo já salvo no repositório."""
    probabilidade, classe = prever_risco(NOVO_CASO)
    assert 0.0 <= probabilidade <= 1.0
    assert classe in (0, 1)
    assert classe == 1


def test_avaliar_protocolos_para_o_novo_caso_do_enunciado():
    """Testa os protocolos disparados para o paciente de exemplo do enunciado."""
    protocolos = avaliar_protocolos(NOVO_CASO, pico_risco_previsto=1)
    assert protocolos == [
        "Se carga do sistema > 85% → abrir unidades temporárias",
        "Se disponibilidade_recursos < 30% → redistribuir insumos",
        "Se densidade_eventos > 6 → ativar plano de contingência",
        "Se risco sistêmico alto → ativar estado de emergência",
    ]


def _paciente_base() -> dict:
    """Paciente neutro, não deve disparar nenhum protocolo."""
    return {
        "spo2_media": 97, "carga_sistema": 50, "fc_media": 80,
        "eventos_24h": 1, "disponibilidade_recursos": 80, "tempo_espera": 20,
        "temperatura": 25, "densidade_eventos": 2, "pa_sistolica": 120,
    }


@pytest.mark.parametrize("campo,valor,protocolo_esperado", [
    ("spo2_media", 85, PROTOCOLOS[0]),
    ("carga_sistema", 90, PROTOCOLOS[1]),
    ("fc_media", 130, PROTOCOLOS[2]),
    ("eventos_24h", 6, PROTOCOLOS[3]),
    ("disponibilidade_recursos", 10, PROTOCOLOS[4]),
    ("tempo_espera", 100, PROTOCOLOS[5]),
    ("temperatura", 39, PROTOCOLOS[6]),
    ("densidade_eventos", 10, PROTOCOLOS[7]),
    ("pa_sistolica", 70, PROTOCOLOS[8]),
])
def test_cada_condicao_numerica_dispara_seu_proprio_protocolo(campo, valor, protocolo_esperado):
    """Testa que cada condição numérica dispara exatamente o seu próprio protocolo."""
    paciente = _paciente_base()
    paciente[campo] = valor
    protocolos = avaliar_protocolos(paciente, pico_risco_previsto=0)
    assert protocolos == [protocolo_esperado]


def test_risco_sistemico_alto_depende_so_da_predicao_do_modelo():
    """Testa que o protocolo de risco sistêmico alto depende só da predição do modelo."""
    paciente = _paciente_base()
    assert avaliar_protocolos(paciente, pico_risco_previsto=0) == []
    assert avaliar_protocolos(paciente, pico_risco_previsto=1) == [PROTOCOLOS[9]]


def test_paciente_sem_nenhum_risco_nao_recebe_protocolo_nenhum():
    """Testa que um paciente sem nenhum fator de risco não recebe protocolo nenhum."""
    assert avaliar_protocolos(_paciente_base(), pico_risco_previsto=0) == []
