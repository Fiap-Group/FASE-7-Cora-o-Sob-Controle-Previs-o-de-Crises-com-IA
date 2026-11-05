import sys
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from shared.agentes.schemas import RecomendacaoFinal  # noqa: E402
from shared.db import Base, get_db  # noqa: E402
from shared.models import HistoricoRisco, Usuario  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.risco.dependencies import get_avaliador_risco  # noqa: E402
from src.modules.risco.mqtt_listener import LeituraIot, get_leitura_iot  # noqa: E402

_engine_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionTeste = sessionmaker(bind=_engine_teste)

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
    """Cria um cliente de teste com um avaliador de risco fake e SQLite em memória."""
    Base.metadata.create_all(_engine_teste)

    def _get_db_teste() -> Generator:
        """Fornece uma sessão do banco de teste."""
        db = _SessionTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_avaliador_risco] = lambda: (lambda _dados: RECOMENDACAO_FAKE)
    app.dependency_overrides[get_db] = _get_db_teste
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(_engine_teste)


def test_avaliar_risco_devolve_a_recomendacao_do_avaliador(cliente: TestClient):
    """Testa que a avaliação de risco devolve a recomendação do avaliador."""
    resposta = cliente.post("/api/risco/avaliar", json=PACIENTE_EXEMPLO)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["probabilidade"] == 0.91
    assert corpo["classificacao"] == "Alto risco"
    assert corpo["protocolos"] == RECOMENDACAO_FAKE.protocolos
    assert corpo["recomendacao"] == RECOMENDACAO_FAKE.recomendacao


def test_avaliar_risco_payload_com_campo_faltando_retorna_422(cliente: TestClient):
    """Testa que um payload sem um campo obrigatório é rejeitado."""
    payload_incompleto = {k: v for k, v in PACIENTE_EXEMPLO.items() if k != "spo2_media"}

    resposta = cliente.post("/api/risco/avaliar", json=payload_incompleto)

    assert resposta.status_code == 422


def test_avaliar_risco_payload_com_tipo_errado_retorna_422(cliente: TestClient):
    """Testa que um payload com um campo de tipo errado é rejeitado."""
    payload_invalido = {**PACIENTE_EXEMPLO, "fc_media": "muito alta"}

    resposta = cliente.post("/api/risco/avaliar", json=payload_invalido)

    assert resposta.status_code == 422


def test_avaliar_risco_erro_do_avaliador_nao_vaza_detalhe_ao_cliente(cliente: TestClient):
    """Testa que um erro interno do avaliador não expõe detalhes ao cliente."""
    def avaliador_quebrado(_dados: dict) -> RecomendacaoFinal:
        """Simula uma falha do avaliador de risco."""
        raise ValueError("Cota do Gemini esgotada (detalhe interno)")

    app.dependency_overrides[get_avaliador_risco] = lambda: avaliador_quebrado

    resposta = cliente.post("/api/risco/avaliar", json=PACIENTE_EXEMPLO)

    assert resposta.status_code == 500
    assert resposta.json() == {"error": "Falha ao avaliar risco cardíaco"}


def test_leitura_iot_sem_mensagem_ainda_devolve_desconectado(cliente: TestClient):
    """Testa que, sem nenhuma mensagem MQTT recebida, a leitura vem desconectada."""
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
    """Testa que a leitura devolve os valores da última mensagem MQTT recebida."""
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


def test_avaliar_risco_com_usuario_id_grava_historico(cliente: TestClient):
    """Testa que avaliar o risco com um usuario_id grava o histórico dessa avaliação."""
    db = _SessionTeste()
    usuario = Usuario(email="paciente@exemplo.com", senha_hash="x:x")
    db.add(usuario)
    db.commit()
    usuario_id = usuario.id
    db.close()

    resposta = cliente.post("/api/risco/avaliar", json={**PACIENTE_EXEMPLO, "usuario_id": usuario_id})
    assert resposta.status_code == 200

    db = _SessionTeste()
    historico = db.query(HistoricoRisco).filter_by(usuario_id=usuario_id).all()
    db.close()

    assert len(historico) == 1
    assert historico[0].probabilidade == 0.91
    assert historico[0].dados_json["fc_media"] == PACIENTE_EXEMPLO["fc_media"]


def test_avaliar_risco_sem_usuario_id_nao_grava_historico(cliente: TestClient):
    """Testa que avaliar o risco sem usuario_id não grava nenhum histórico."""
    cliente.post("/api/risco/avaliar", json=PACIENTE_EXEMPLO)

    db = _SessionTeste()
    historico = db.query(HistoricoRisco).all()
    db.close()

    assert historico == []
