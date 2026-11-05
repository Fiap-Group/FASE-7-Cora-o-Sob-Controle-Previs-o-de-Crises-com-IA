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
    """Cria um cliente de teste com um SQLite em memória no lugar do Postgres."""
    Base.metadata.create_all(_engine_teste)

    def _get_db_teste() -> Generator:
        """Fornece uma sessão do banco de teste."""
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
    """Testa que o cadastro cria a conta com os dados informados."""
    resposta = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == USUARIO_EXEMPLO["email"]
    assert corpo["nickname"] is None
    assert "id" in corpo


def test_cadastro_com_email_invalido_retorna_400(cliente: TestClient):
    """Testa que um e-mail em formato inválido é rejeitado no cadastro."""
    resposta = cliente.post("/api/auth/cadastro", json={"email": "nao-e-email", "senha": "senha123"})

    assert resposta.status_code == 400


def test_cadastro_com_email_duplicado_retorna_409(cliente: TestClient):
    """Testa que cadastrar o mesmo e-mail duas vezes é rejeitado."""
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)
    resposta = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 409


def test_login_com_credenciais_corretas_devolve_o_usuario(cliente: TestClient):
    """Testa que o login com e-mail e senha corretos devolve os dados do usuário."""
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    resposta = cliente.post("/api/auth/login", json=USUARIO_EXEMPLO)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == USUARIO_EXEMPLO["email"]


def test_login_com_senha_errada_retorna_401(cliente: TestClient):
    """Testa que o login com senha errada é rejeitado."""
    cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO)

    resposta = cliente.post("/api/auth/login", json={**USUARIO_EXEMPLO, "senha": "senha_errada"})

    assert resposta.status_code == 401


def test_definir_nickname_atualiza_a_conta(cliente: TestClient):
    """Testa que definir o nickname atualiza a conta do usuário."""
    usuario_id = cliente.post("/api/auth/cadastro", json=USUARIO_EXEMPLO).json()["id"]

    resposta = cliente.post("/api/auth/nickname", json={"usuario_id": usuario_id, "nickname": "Jonathan"})

    assert resposta.status_code == 200
    assert resposta.json()["nickname"] == "Jonathan"


def test_definir_nickname_de_usuario_inexistente_retorna_404(cliente: TestClient):
    """Testa que definir o nickname de um usuário inexistente devolve 404."""
    resposta = cliente.post("/api/auth/nickname", json={"usuario_id": 99999, "nickname": "Jonathan"})

    assert resposta.status_code == 404
