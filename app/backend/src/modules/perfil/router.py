from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import service
from .dependencies import get_db
from .schemas import PerfilResponse

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("/{usuario_id}", response_model=PerfilResponse)
def perfil(usuario_id: int, db: Session = Depends(get_db)) -> PerfilResponse:
    """Devolve a ficha de jogador do usuário: conta, avaliação mais recente e histórico."""
    resposta = service.buscar_perfil(db, usuario_id)
    if not resposta:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return resposta
