"""
=============================================================================
Providers do módulo de autenticação
=============================================================================
`get_db` é a dependency que abre/fecha uma Session do SQLAlchemy por
request — mesmo mecanismo de DI já usado em `get_avaliador_risco`
(módulo risco) e `get_estado` (módulo rag). Testes substituem por uma
Session ligada a um SQLite em memória via `app.dependency_overrides`,
sem precisar do Postgres de verdade no ar.
=============================================================================
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from shared.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
