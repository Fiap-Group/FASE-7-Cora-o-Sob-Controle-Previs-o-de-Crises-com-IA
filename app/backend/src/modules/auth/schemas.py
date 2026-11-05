from pydantic import BaseModel


class CadastroRequest(BaseModel):
    """Dados recebidos para criar uma nova conta."""

    email: str
    senha: str


class LoginRequest(BaseModel):
    """Dados recebidos para autenticar um usuário."""

    email: str
    senha: str


class NicknameRequest(BaseModel):
    """Dados recebidos para definir o nickname de uma conta."""

    usuario_id: int
    nickname: str


class UsuarioResponse(BaseModel):
    """Dados do usuário devolvidos pela API."""

    id: int
    email: str
    nickname: str | None

    model_config = {"from_attributes": True}
