"""Schemas HTTP do módulo `auth` — shape de request/response, não dado de
domínio (esse é `shared/models.py:Usuario`).

E-mail fica como `str` simples (não `EmailStr`) pra não precisar da
dependência extra `email-validator` só pra isso — o formato já é validado
nos dois front-ends antes de chamar a API, e de novo em
`service.py:criar_usuario` (defesa contra chamada direta à API)."""

from pydantic import BaseModel


class CadastroRequest(BaseModel):
    email: str
    senha: str


class LoginRequest(BaseModel):
    email: str
    senha: str


class NicknameRequest(BaseModel):
    usuario_id: int
    nickname: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nickname: str | None

    model_config = {"from_attributes": True}
