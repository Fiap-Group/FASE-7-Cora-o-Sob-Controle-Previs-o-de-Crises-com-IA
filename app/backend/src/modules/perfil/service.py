"""Lógica do "Perfil" — separada do router, mesmo espírito de
`src/modules/auth/service.py`."""

from sqlalchemy.orm import Session

from shared.models import HistoricoRisco, Usuario

from .schemas import AvaliacaoResumo, PerfilResponse

HISTORICO_LIMITE = 10


def _resumo(h: HistoricoRisco) -> AvaliacaoResumo:
    return AvaliacaoResumo(
        criado_em=h.criado_em,
        probabilidade=h.probabilidade,
        classificacao=h.classificacao,
        dados=h.dados_json,
        protocolos=h.protocolos_json,
        recomendacao=h.recomendacao,
    )


def buscar_perfil(db: Session, usuario_id: int) -> PerfilResponse | None:
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if not usuario:
        return None

    historico = (
        db.query(HistoricoRisco)
        .filter_by(usuario_id=usuario_id)
        .order_by(HistoricoRisco.criado_em.desc())
        .limit(HISTORICO_LIMITE)
        .all()
    )

    return PerfilResponse(
        usuario=usuario,
        avaliacao_mais_recente=_resumo(historico[0]) if historico else None,
        historico=[_resumo(h) for h in historico],
    )
