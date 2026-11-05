"""
=============================================================================
Modelo preditivo de pico de risco cardíaco (Fase 6) — PyTorch
=============================================================================
Rede neural simples (MLP) treinada pra prever `pico_risco` a partir das 10
features da base sintética (ver `dataset.py`). O scikit-learn aparece aqui
só como utilitário (split estratificado, normalização, métricas) — quem
aprende e prevê é a rede em `RedeRiscoCardiaco`.

Nota sobre a acurácia: `pico_risco` é uma função determinística das próprias
features de treino (ver `dataset.py`), então o modelo tende a acertar quase
tudo — isso é esperado pela natureza da base sintética do enunciado, não é
vazamento de dados nem sinal de que o modelo generalizaria assim tão bem
numa base real.
=============================================================================
"""

from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn

from shared.preditivo.dataset import COLUNA_ALVO, COLUNAS_FEATURES

CAMINHO_MODELO = Path(__file__).resolve().parent / "modelo_risco.pt"


class RedeRiscoCardiaco(nn.Module):
    """MLP pequena: 10 features → 16 → 16 → 1 logit (sem sigmoid aqui —
    aplicada na inferência, junto com `BCEWithLogitsLoss` no treino).

    Tamanho escolhido empiricamente: redes maiores (32/64/128) convergiram
    pior nessa base (ficam entre 85-91% de acurácia); com 16 neurônios por
    camada + mais épocas, a rede aproxima melhor a regra de contagem de
    limiares do enunciado (ver módulo `treinar.py`)."""

    def __init__(self, n_features: int = len(COLUNAS_FEATURES)):
        super().__init__()
        self.camadas = nn.Sequential(
            nn.Linear(n_features, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.camadas(x)


def treinar_modelo(
    df: Any,
    seed: int = 42,
    epocas: int = 1500,
    lr: float = 3e-3,
) -> tuple[RedeRiscoCardiaco, np.ndarray, np.ndarray, dict[str, Any]]:
    """Treina a rede e devolve (modelo, media_scaler, desvio_scaler, métricas)."""
    torch.manual_seed(seed)

    X = df[COLUNAS_FEATURES].to_numpy(dtype=np.float32)
    y = df[COLUNA_ALVO].to_numpy(dtype=np.float32)

    # `cast`: o stub de train_test_split tipa o retorno de forma genérica
    # demais pra esse unpacking de 4 valores (vira uma união com str/tuple
    # que não reflete a realidade em runtime — sempre são os 4 ndarrays).
    divisao = cast(
        "tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]",
        train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y),
    )
    X_treino, X_teste, y_treino, y_teste = divisao

    scaler = StandardScaler().fit(X_treino)
    # cast: mesmo motivo do train_test_split acima — o stub do scikit-learn
    # tipa `transform`/`mean_`/`scale_` de forma genérica demais.
    X_treino_norm = cast(np.ndarray, scaler.transform(X_treino))
    X_teste_norm = cast(np.ndarray, scaler.transform(X_teste))

    tensor_X_treino = torch.from_numpy(X_treino_norm.astype(np.float32))
    tensor_y_treino = torch.from_numpy(y_treino).unsqueeze(1)
    tensor_X_teste = torch.from_numpy(X_teste_norm.astype(np.float32))

    modelo = RedeRiscoCardiaco()
    proporcao_positivos = max(y_treino.mean(), 1e-6)
    pos_weight = torch.tensor([(1 - proporcao_positivos) / proporcao_positivos])
    funcao_perda = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    otimizador = torch.optim.Adam(modelo.parameters(), lr=lr)

    modelo.train()
    for _epoca in range(epocas):
        otimizador.zero_grad()
        logits = modelo(tensor_X_treino)
        perda = funcao_perda(logits, tensor_y_treino)
        perda.backward()
        otimizador.step()

    modelo.eval()
    with torch.no_grad():
        logits_teste = modelo(tensor_X_teste).squeeze(1)
        probabilidades_teste = torch.sigmoid(logits_teste).numpy()
    previsoes_teste = (probabilidades_teste >= 0.5).astype(int)
    y_teste_int = y_teste.astype(int)  # evita chaves "0.0"/"1.0" no relatório

    metricas = {
        "acuracia": accuracy_score(y_teste_int, previsoes_teste),
        "matriz_confusao": confusion_matrix(y_teste_int, previsoes_teste),
        "relatorio": classification_report(y_teste_int, previsoes_teste, output_dict=True),
    }
    return modelo, cast(np.ndarray, scaler.mean_), cast(np.ndarray, scaler.scale_), metricas


def salvar_modelo(
    modelo: RedeRiscoCardiaco,
    scaler_mean: np.ndarray,
    scaler_scale: np.ndarray,
    caminho: Path = CAMINHO_MODELO,
) -> None:
    torch.save(
        {
            "state_dict": modelo.state_dict(),
            "colunas": list(COLUNAS_FEATURES),
            "scaler_mean": torch.from_numpy(np.asarray(scaler_mean, dtype=np.float32)),
            "scaler_scale": torch.from_numpy(np.asarray(scaler_scale, dtype=np.float32)),
        },
        caminho,
    )


def carregar_modelo(caminho: Path = CAMINHO_MODELO) -> dict[str, Any]:
    if not caminho.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {caminho}. Rode "
            "`python -m shared.preditivo.treinar` primeiro."
        )
    checkpoint = torch.load(caminho, weights_only=False)
    modelo = RedeRiscoCardiaco(n_features=len(checkpoint["colunas"]))
    modelo.load_state_dict(checkpoint["state_dict"])
    modelo.eval()
    return {
        "modelo": modelo,
        "colunas": checkpoint["colunas"],
        "scaler_mean": checkpoint["scaler_mean"],
        "scaler_scale": checkpoint["scaler_scale"],
    }


def prever_risco(paciente: dict[str, Any], caminho: Path = CAMINHO_MODELO) -> tuple[float, int]:
    """Devolve (probabilidade, classe) de `pico_risco` pra um paciente."""
    checkpoint = carregar_modelo(caminho)
    colunas: list[str] = checkpoint["colunas"]
    valores = torch.tensor([[float(paciente[coluna]) for coluna in colunas]], dtype=torch.float32)
    normalizado = (valores - checkpoint["scaler_mean"]) / checkpoint["scaler_scale"]

    modelo: RedeRiscoCardiaco = checkpoint["modelo"]
    with torch.no_grad():
        logit = modelo(normalizado)
        probabilidade = torch.sigmoid(logit).item()

    classe = int(probabilidade >= 0.5)
    return probabilidade, classe
