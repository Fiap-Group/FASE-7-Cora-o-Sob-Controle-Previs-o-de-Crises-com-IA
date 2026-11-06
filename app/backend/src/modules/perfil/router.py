import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import service
from .dependencies import get_db
from .schemas import PerfilResponse

logger = logging.getLogger("genera_api")

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("/{usuario_id}", response_model=PerfilResponse)
def perfil(usuario_id: int, db: Session = Depends(get_db)) -> PerfilResponse:
    resposta = service.buscar_perfil(db, usuario_id)
    if not resposta:
        logger.warning(
            "Perfil solicitado para usuário inexistente", extra={"evento": "perfil_nao_encontrado"}
        )
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return resposta
