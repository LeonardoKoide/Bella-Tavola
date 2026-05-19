import numpy as np
import pandas as pd
from typing import Tuple


def gerar_dataset(
    n_samples: int = 1000, seed: int = 42, proporcao_positivos: float = 0.3
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Gera dataset sintético de detecção de fraude.

    Parâmetros
    ----------
    n_samples : int
        Número de amostras a gerar.
    seed : int
        Seed para reprodutibilidade.
    proporcao_positivos : float
        Proporção da classe positiva. Deve estar entre 0.05 e 0.95.

    Retorna
    -------
    df : pd.DataFrame
    X : np.ndarray
    y : np.ndarray

    Exemplo
    -------
    >>> df, X, y = gerar_dataset(n_samples=500, seed=0)
    >>> df.shape
    (500, 6)
    """
    if not (0.05 <= proporcao_positivos <= 0.95):
        raise ValueError(
            f"proporcao_positivos deve estar entre 0.05 e 0.95, " f"recebido: {proporcao_positivos}"
        )

    rng = np.random.default_rng(seed)
    fraude = rng.choice([0, 1], size=n_samples, p=[1 - proporcao_positivos, proporcao_positivos])

    valor_transacao = np.where(
        fraude, rng.uniform(500, 10000, n_samples), rng.uniform(10, 800, n_samples)
    ).round(2)

    hora_transacao = np.where(fraude, rng.integers(0, 6, n_samples), rng.integers(7, 23, n_samples))

    distancia_ultima_compra = np.where(
        fraude, rng.uniform(100, 5000, n_samples), rng.uniform(0, 50, n_samples)
    ).round(1)

    tentativas_senha = np.where(
        fraude, rng.integers(2, 10, n_samples), rng.integers(1, 2, n_samples)
    )

    pais_diferente = (rng.random(n_samples) < np.where(fraude, 0.4, 0.05)).astype(int)

    df = pd.DataFrame(
        {
            "valor_transacao": valor_transacao,
            "hora_transacao": hora_transacao,
            "distancia_ultima_compra": distancia_ultima_compra,
            "tentativas_senha": tentativas_senha,
            "pais_diferente": pais_diferente,
            "target": fraude,
        }
    )

    X = df.drop(columns=["target"]).values
    y = df["target"].values
    return df, X, y
