import hashlib
import hmac
import re
import secrets

from sqlalchemy.orm import Session

from shared.models import Usuario

_REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class EmailInvalido(ValueError):
    pass


class EmailDuplicado(ValueError):
    pass


def _hash_senha(senha: str, salt: str) -> str:
    return hashlib.sha256((salt + senha).encode()).hexdigest()


def _criar_senha_hash(senha: str) -> str:
    """Gera um salt aleatório e devolve o hash da senha no formato salt:hash."""
    salt = secrets.token_hex(16)
    return f"{salt}:{_hash_senha(senha, salt)}"


def _senha_confere(senha: str, senha_hash: str) -> bool:
    salt, hash_esperado = senha_hash.split(":", 1)
    return hmac.compare_digest(_hash_senha(senha, salt), hash_esperado)


def criar_usuario(db: Session, email: str, senha: str) -> Usuario:
    if not _REGEX_EMAIL.match(email):
        raise EmailInvalido("E-mail inválido")

    if db.query(Usuario).filter_by(email=email).first():
        raise EmailDuplicado("E-mail já cadastrado")

    usuario = Usuario(email=email, senha_hash=_criar_senha_hash(senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario | None:
    usuario = db.query(Usuario).filter_by(email=email).first()
    if usuario and _senha_confere(senha, usuario.senha_hash):
        return usuario
    return None


def definir_nickname(db: Session, usuario_id: int, nickname: str) -> Usuario | None:
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if not usuario:
        return None

    usuario.nickname = nickname
    db.commit()
    db.refresh(usuario)
    return usuario
