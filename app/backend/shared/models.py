from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


class HistoricoRisco(Base):
    __tablename__ = "historico_risco"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    dados_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    probabilidade: Mapped[float] = mapped_column(Float, nullable=False)
    classificacao: Mapped[str] = mapped_column(String, nullable=False)
    protocolos_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    recomendacao: Mapped[str] = mapped_column(String, nullable=False)
