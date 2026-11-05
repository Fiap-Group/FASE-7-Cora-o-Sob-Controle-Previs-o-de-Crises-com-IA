"""
Testes dos endpoints do módulo risco: POST /api/risco/avaliar e
GET /api/risco/leitura-iot.

Não chamam o Gemini nem o broker MQTT de verdade: o avaliador (fluxo
multiagente) e a leitura de IoT são substituídos por fakes via
`app.dependency_overrides`, igual ao padrão já usado em test_sprint4.py
para o pipeline RAG.
"""

import sys
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from shared.agentes.schemas import RecomendacaoFinal  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.risco.dependencies import get_avaliador_risco  # noqa: E402
from src.modules.risco.mqtt_listener import LeituraIot, get_leitura_iot  # noqa: E402

PACIENTE_EXEMPLO = {
    "idade_media": 60,
    "carga_sistema": 90,
    "tempo_espera": 100,
    "fc_media": 125,
    "spo2_media": 85,
    "pa_sistolica": 85,
    "temperatura": 39,
    "densidade_eventos": 7,
    "eventos_24h": 6,
    "disponibilidade_recursos": 20,
}

RECOMENDACAO_FAKE = RecomendacaoFinal(
    probabilidade=0.91,
    classificacao="Alto risco",
    protocolos=["Se carga do sistema > 85% → abrir unidades temporárias"],
    recomendacao="Abrir unidades temporárias e redistribuir recursos imediatamente.",
)


@pytest.fixture
def cliente() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_avaliador_risco] = lambda: (lambda _dados: RECOMENDACAO_FAKE)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_avaliar_risco_devolve_a_recomendacao_do_avaliador(cliente: TestClient):
    resposta = cliente.post("/api/risco/avaliar", json=PACIENTE_EXEMPLO)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["probabilidade"] == 0.91
    assert corpo["classificacao"] == "Alto risco"
    assert corpo["protocolos"] == RECOMENDACAO_FAKE.protocolos
    assert corpo["recomendacao"] == RECOMENDACAO_FAKE.recomendacao


def test_avaliar_risco_payload_com_campo_faltando_retorna_422(cliente: TestClient):
    payload_incompleto = {k: v for k, v in PACIENTE_EXEMPLO.items() if k != "spo2_media"}

    resposta = cliente.post("/api/risco/avaliar", json=payload_incompleto)

    assert resposta.status_code == 422


def test_avaliar_risco_payload_com_tipo_errado_retorna_422(cliente: TestClient):
    payload_invalido = {**PACIENTE_EXEMPLO, "fc_media": "muito alta"}

    resposta = cliente.post("/api/risco/avaliar", json=payload_invalido)

    assert resposta.status_code == 422


def test_avaliar_risco_erro_do_avaliador_nao_vaza_detalhe_ao_cliente(cliente: TestClient):
    def avaliador_quebrado(_dados: dict) -> RecomendacaoFinal:
        raise ValueError("Cota do Gemini esgotada (detalhe interno)")

    app.dependency_overrides[get_avaliador_risco] = lambda: avaliador_quebrado

    resposta = cliente.post("/api/risco/avaliar", json=PACIENTE_EXEMPLO)

    assert resposta.status_code == 500
    assert resposta.json() == {"error": "Falha ao avaliar risco cardíaco"}


def test_leitura_iot_sem_mensagem_ainda_devolve_desconectado(cliente: TestClient):
    app.dependency_overrides[get_leitura_iot] = lambda: LeituraIot()

    resposta = cliente.get("/api/risco/leitura-iot")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["conectado"] is False
    assert corpo["fc_media"] is None
    assert corpo["pa_sistolica"] is None
    assert corpo["spo2_media"] is None
    assert corpo["recebido_em"] is None


def test_leitura_iot_com_mensagem_recebida_devolve_os_valores(cliente: TestClient):
    agora = datetime(2026, 1, 1, 12, 0, 0)
    leitura_fake = LeituraIot(
        conectado=True, fc_media=125.0, pa_sistolica=85.0, spo2_media=89.0, recebido_em=agora
    )
    app.dependency_overrides[get_leitura_iot] = lambda: leitura_fake

    resposta = cliente.get("/api/risco/leitura-iot")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["conectado"] is True
    assert corpo["fc_media"] == 125.0
    assert corpo["pa_sistolica"] == 85.0
    assert corpo["spo2_media"] == 89.0
    assert corpo["recebido_em"] == agora.isoformat()
