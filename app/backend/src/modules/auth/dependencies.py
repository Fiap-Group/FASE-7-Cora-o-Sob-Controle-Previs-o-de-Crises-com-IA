"""
`get_db` em si mora em `shared/db.py` (infraestrutura genérica de
sessão, reusada por `risco` e `perfil` também) — isso aqui só reexporta,
pra manter o padrão de cada módulo importar sua dependency a partir do
próprio `.dependencies` (igual `get_avaliador_risco`/`get_leitura_iot`).
"""

from shared.db import get_db

__all__ = ["get_db"]
