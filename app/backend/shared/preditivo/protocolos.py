"""
=============================================================================
Base de protocolos simulada — Fase 6
=============================================================================
Os 10 protocolos do enunciado, verbatim, e a lógica que decide quais deles
se aplicam a um paciente. Diferente de uma entrega anterior (que tinha só
duas listas genéricas por rótulo "Alto risco"/"Baixo risco"), aqui cada
protocolo é avaliado contra a condição numérica real que o enunciado
descreve.
=============================================================================
"""

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

# Cada condição recebe o paciente (dict com as 10 features) e o
# `pico_risco_previsto` (0/1) que o modelo já calculou. A condição 10
# ("risco sistêmico alto") não tem um campo numérico próprio no enunciado —
# decisão explícita: amarramos ela à própria predição do modelo, não a uma
# nova fórmula reinventada por nós.
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
    """Retorna os protocolos cuja condição real é verdadeira pro paciente.

    `pico_risco_previsto` é a classe (0 ou 1) que o modelo preditivo já
    calculou pra esse paciente — usada só na condição 10 (ver `_CONDICOES`).
    """
    return [
        protocolo
        for protocolo, condicao in zip(PROTOCOLOS, _CONDICOES)
        if condicao(paciente, pico_risco_previsto)
    ]
