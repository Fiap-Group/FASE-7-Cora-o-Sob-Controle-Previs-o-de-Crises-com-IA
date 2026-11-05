"""
Testes dos endpoints do módulo auth: cadastro, login e nickname.

Não tocam no Postgres de verdade: `get_db` é substituído por uma Session
ligada a um SQLite em memória (StaticPool — uma conexão só, compartilhada
entre threads, porque as rotas são `def` síncronas e o FastAPI despacha
pro threadpool; sem isso, duas chamadas no mesmo teste podiam cair em
threads diferentes e ver bancos em memória diferentes). Mesmo princípio
de "sem depender de serviço externo" já seguido em test_risco_endpoint.py
(sem chamar o Gemini) e no listener MQTT (sem o broker real).
"""

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

from shared.db import Base  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.auth.dependencies import get_db  # noqa: E402

_engine_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionTeste = sessionmaker(bind=_engine_teste)

USUARIO_EXEMPLO = {"email": "paciente@exemplo.com", "senha": "senha123"}


@pytest.fixture
def cliente() -> Generator[TestClient, None, None]:
    Base.metadata.create_all(_engine_teste)

    def _get_db_teste() -> Generator:
        db = _SessionTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db_teste
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(_engine_teste)


def test_cadastro_cria_a_conta(cliente: TestClient):
    resposta = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == USUARIO_EXEMPLO["email"]
    assert corpo["nickname"] is None
    assert "id" in corpo


def test_cadastro_com_email_invalido_retorna_400(cliente: TestClient):
    resposta = cliente.post("/api/auth/cadastro", json={"email": "nao-e-email", "senha": "senha123"})

    assert resposta.status_code == 400


def test_cadastro_com_email_duplicado_retorna_409(cliente: TestClient):
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)
    resposta = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 409


def test_login_com_credenciais_corretas_devolve_o_usuario(cliente: TestClient):
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    resposta = cliente.post("/api/auth/login", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == USUARIO_EXEMPLO["email"]


def test_login_com_senha_errada_retorna_401(cliente: TestClient):
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    resposta = cliente.post("/api/auth/login", json={**USUARIO_EXEMPLO, "senha": "senha_errada"})

    assert resposta.status_code == 401


def test_definir_nickname_atualiza_a_conta(cliente: TestClient):
    usuario_id = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO).json()["id"]

    resposta = cliente.post("/api/auth/nickname", json={"usuario_id": usuario_id, "nickname": "Jonathan"})

    assert resposta.status_code == 200
    assert resposta.json()["nickname"] == "Jonathan"


def test_definir_nickname_de_usuario_inexistente_retorna_404(cliente: TestClient):
    resposta = cliente.post("/api/auth/nickname", json={"usuario_id": 99999, "nickname": "Jonathan"})

    assert resposta.status_code == 404
