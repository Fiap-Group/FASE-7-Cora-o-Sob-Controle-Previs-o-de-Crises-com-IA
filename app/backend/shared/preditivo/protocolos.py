from typing import Any

PROTOCOLOS = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência",
]

_CONDICOES = [
    lambda p, _risco: p["spo2_media"] < 88,
    lambda p, _risco: p["carga_sistema"] > 85,
    lambda p, _risco: p["fc_media"] > 120,
    lambda p, _risco: p["eventos_24h"] > 5,
    lambda p, _risco: p["disponibilidade_recursos"] < 30,
    lambda p, _risco: p["tempo_espera"] > 90,
    lambda p, _risco: p["temperatura"] > 38,
    lambda p, _risco: p["densidade_eventos"] > 6,
    lambda p, _risco: p["pa_sistolica"] < 90,
    lambda _p, risco: risco == 1,
]


def avaliar_protocolos(paciente: dict[str, Any], pico_risco_previsto: int) -> list[str]:
    """Devolve os protocolos cuja condição real é verdadeira para o paciente."""
    return [
        protocolo
        for protocolo, condicao in zip(PROTOCOLOS, _CONDICOES)
        if condicao(paciente, pico_risco_previsto)
    ]
