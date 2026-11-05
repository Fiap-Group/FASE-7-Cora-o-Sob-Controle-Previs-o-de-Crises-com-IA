"""
=============================================================================
Controller do módulo de perfil (equivalente a um @Controller do Nest)
=============================================================================
A "ficha de jogador" do usuário: dados da conta + a avaliação de risco
mais recente em destaque + um histórico curto — alimentado por
src/modules/risco/router.py (avaliar_risco grava um HistoricoRisco a
cada avaliação concluída com usuario_id).

Endpoints:
    GET /api/perfil/{usuario_id}
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import service
from .dependencies import get_db
from .schemas import PerfilResponse

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("/{usuario_id}", response_model=PerfilResponse)
def perfil(usuario_id: int, db: Session = Depends(get_db)) -> PerfilResponse:
    resposta = service.buscar_perfil(db, usuario_id)
    if not resposta:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return resposta
