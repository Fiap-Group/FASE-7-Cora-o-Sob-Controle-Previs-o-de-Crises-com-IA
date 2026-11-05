"""Modelos SQLAlchemy — dado de domínio persistente, por isso fica em
`shared/` (mesmo motivo de `shared/agentes/schemas.py`), não dentro de
`src/modules/auth/`, que só tem o shape HTTP."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
