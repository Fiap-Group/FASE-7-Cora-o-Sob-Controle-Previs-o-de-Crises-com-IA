"""
=============================================================================
Controller do módulo de autenticação (equivalente a um @Controller do Nest)
=============================================================================
Conta de usuário compartilhada entre mobile e web — a única coisa dos
dois front-ends que precisa de um banco de verdade (Postgres), em vez de
ficar em memória como o resto do backend. Ver shared/db.py e
shared/models.py.

Endpoints:
    POST /api/auth/cadastro    cria a conta (e-mail + senha)
    POST /api/auth/login       autentica e devolve o usuário
    POST /api/auth/nickname    define o nickname de uma conta já criada
=============================================================================
"""

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
    usuario = service.autenticar(db, body.email, body.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    return UsuarioResponse.model_validate(usuario)


@router.post("/nickname", response_model=UsuarioResponse)
def nickname(body: NicknameRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = service.definir_nickname(db, body.usuario_id, body.nickname)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return UsuarioResponse.model_validate(usuario)
