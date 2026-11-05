"""
=============================================================================
Base sintética — predição de pico de risco cardíaco (Fase 6)
=============================================================================
Gera a base de dados sintética usada para treinar o modelo preditivo de
`pico_risco`. O código abaixo é o do enunciado da atividade, verbatim (só
parametrizado por `n`/`seed` em vez de constantes fixas) — não inventamos
nem simplificamos as 10 features nem a regra de `pico_risco`, pra manter o
treino fiel ao que foi pedido.
=============================================================================
"""

import numpy as np
import pandas as pd

# As 10 features usadas no treino, na ordem em que o modelo espera recebê-las.
# Fonte única de verdade: `modelo.py`, `protocolos.py` e `agentes/schemas.py`
# reaproveitam esta lista em vez de retypar os nomes das colunas.
COLUNAS_FEATURES = [
    "idade_media",
    "carga_sistema",
    "tempo_espera",
    "fc_media",
    "spo2_media",
    "pa_sistolica",
    "temperatura",
    "densidade_eventos",
    "eventos_24h",
    "disponibilidade_recursos",
]

COLUNA_ALVO = "pico_risco"


def gerar_base_sintetica(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Gera `n` pacientes sintéticos com as 10 features e o alvo `pico_risco`.

    Fórmula do enunciado: `pico_risco = 1` quando pelo menos 2 das 6 condições
    de risco abaixo são verdadeiras (carga do sistema alta, espera longa,
    SPO2 baixo, FC alta, muitos eventos nas últimas 24h, poucos recursos
    disponíveis).
    """
    rng = np.random.RandomState(seed)
    df = pd.DataFrame({
        "idade_media": rng.normal(55, 12, n).clip(18, 90),
        "carga_sistema": rng.uniform(30, 100, n),
        "tempo_espera": rng.normal(45, 20, n).clip(5, 180),
        "fc_media": rng.normal(85, 15, n).clip(50, 150),
        "spo2_media": rng.normal(95, 3, n).clip(70, 100),
        "pa_sistolica": rng.normal(125, 20, n).clip(80, 200),
        "temperatura": rng.normal(24, 5, n).clip(10, 40),
        "densidade_eventos": rng.poisson(3, n),
        "eventos_24h": rng.poisson(2, n),
        "disponibilidade_recursos": rng.uniform(20, 100, n),
    })

    risk_score = (
        (df["carga_sistema"] > 80).astype(int)
        + (df["tempo_espera"] > 60).astype(int)
        + (df["spo2_media"] < 92).astype(int)
        + (df["fc_media"] > 110).astype(int)
        + (df["eventos_24h"] > 4).astype(int)
        + (df["disponibilidade_recursos"] < 40).astype(int)
    )

    df[COLUNA_ALVO] = (risk_score >= 2).astype(int)
    return df
