"""`get_db` mora em `shared/db.py` (infraestrutura genérica de sessão,
reusada por `auth` e `risco` também) — isso aqui só reexporta."""

from shared.db import get_db

__all__ = ["get_db"]
