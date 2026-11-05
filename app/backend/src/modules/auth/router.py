import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import service
from .dependencies import get_db
from .schemas import CadastroRequest, LoginRequest, NicknameRequest, UsuarioResponse

logger = logging.getLogger("genera_api")

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/cadastro", response_model=UsuarioResponse, status_code=201)
def cadastro(body: CadastroRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    """Cria uma nova conta de usuário a partir de e-mail e senha."""
    try:
        usuario = service.criar_usuario(db, body.email, body.senha)
    except service.EmailInvalido as e:
        raise HTTPException(status_code=400, detail=str(e))
    except service.EmailDuplicado as e:
        raise HTTPException(status_code=409, detail=str(e))

    logger.info("Conta criada", extra={"evento": "auth_cadastro"})
    return UsuarioResponse.model_validate(usuario)


@router.post("/login", response_model=UsuarioResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    """Autentica o usuário pelo e-mail e senha e devolve seus dados."""
    usuario = service.autenticar(db, body.email, body.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    return UsuarioResponse.model_validate(usuario)


@router.post("/nickname", response_model=UsuarioResponse)
def nickname(body: NicknameRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    """Define o nickname de uma conta já criada."""
    usuario = service.definir_nickname(db, body.usuario_id, body.nickname)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return UsuarioResponse.model_validate(usuario)
