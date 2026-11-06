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
