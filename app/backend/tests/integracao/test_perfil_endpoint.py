import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from shared.agentes.schemas import RecomendacaoFinal  # noqa: E402
from shared.db import Base  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.auth.dependencies import get_db  # noqa: E402
from src.modules.risco.dependencies import get_avaliador_risco  # noqa: E402

_engine_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionTeste = sessionmaker(bind=_engine_teste)

USUARIO_EXEMPLO = {"email": "jogador@exemplo.com", "senha": "senha123"}

RECOMENDACAO_FAKE = RecomendacaoFinal(
    probabilidade=0.91,
    classificacao="Alto risco",
    protocolos=["Se carga do sistema > 85% → abrir unidades temporárias"],
    recomendacao="Abrir unidades temporárias e redistribuir recursos imediatamente.",
)

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


@pytest.fixture
def cliente() -> Generator[TestClient, None, None]:
    """Cria um cliente de teste com um SQLite em memória e um avaliador de risco fake."""
    Base.metadata.create_all(_engine_teste)

    def _get_db_teste() -> Generator:
        """Fornece uma sessão do banco de teste."""
        db = _SessionTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db_teste
    app.dependency_overrides[get_avaliador_risco] = lambda: (lambda _dados: RECOMENDACAO_FAKE)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(_engine_teste)


def _criar_usuario(cliente: TestClient) -> int:
    """Cadastra um usuário de exemplo e devolve seu id."""
    return cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO).json()["id"]


def test_perfil_de_usuario_sem_avaliacoes(cliente: TestClient):
    """Testa o perfil de um usuário que ainda não tem nenhuma avaliação."""
    usuario_id = _criar_usuario(cliente)

    resposta = cliente.get(f"/api/perfil/{usuario_id}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["usuario"]["email"] == USUARIO_EXEMPLO["email"]
    assert corpo["avaliacao_mais_recente"] is None
    assert corpo["historico"] == []


def test_perfil_com_avaliacoes_devolve_a_mais_recente_em_destaque(cliente: TestClient):
    """Testa que o perfil destaca a avaliação mais recente do usuário."""
    usuario_id = _criar_usuario(cliente)

    cliente.post("/api/risco/avaliar", json={**PACIENTE_EXEMPLO, "usuario_id": usuario_id})
    cliente.post(
        "/api/risco/avaliar",
        json={**PACIENTE_EXEMPLO, "fc_media": 70, "spo2_media": 97, "usuario_id": usuario_id},
    )

    resposta = cliente.get(f"/api/perfil/{usuario_id}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["avaliacao_mais_recente"]["dados"]["fc_media"] == 70
    assert len(corpo["historico"]) == 2


def test_perfil_de_usuario_inexistente_retorna_404(cliente: TestClient):
    """Testa que buscar o perfil de um usuário inexistente devolve 404."""
    resposta = cliente.get("/api/perfil/99999")

    assert resposta.status_code == 404
