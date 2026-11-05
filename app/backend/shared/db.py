"""
=============================================================================
Conexão SQLAlchemy — único banco relacional persistente do backend
=============================================================================
Tudo que já existia (RAG, risco, IoT) vive em memória; a conta de usuário
(src/modules/auth) é a primeira coisa que precisa persistir de verdade,
porque mobile e web precisam compartilhar a mesma conta.

Postgres em produção/Docker (ver docker-compose.yml, serviço "db"); os
testes apontam `DATABASE_URL` pra SQLite em memória via
app.dependency_overrides em src/modules/auth/dependencies.py — isso aqui
não precisa saber a diferença.
=============================================================================
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://cardioia:cardioia@localhost:5432/cardioia")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
