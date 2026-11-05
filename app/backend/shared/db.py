"""
=============================================================================
Conexão SQLAlchemy — único banco relacional persistente do backend
=============================================================================
Tudo que já existia (RAG, risco, IoT) vive em memória; a conta de usuário
(src/modules/auth) é a primeira coisa que precisa persistir de verdade,
porque mobile e web precisam compartilhar a mesma conta.

Postgres em produção/Docker (ver docker-compose.yml, serviço "db"); os
testes apontam pra uma Session de SQLite em memória via
app.dependency_overrides[get_db] — isso aqui não precisa saber a
diferença.

`get_db` fica aqui (não dentro de um módulo específico) porque é
infraestrutura genérica de sessão, usada por `auth`, `risco` e `perfil` —
nenhum módulo deveria depender de outro só pra conseguir uma Session.
=============================================================================
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://cardioia:cardioia@localhost:5432/cardioia")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
