"""Medias móviles y señal de cruce dorado / cruce de la muerte."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import SMA_LONG, SMA_SHORT


def moving_averages(prices: pd.Series, short: int = SMA_SHORT, long: int = SMA_LONG) -> pd.DataFrame:
    """Media móvil corta y larga sobre el precio de cierre."""
    return pd.DataFrame(
        {
            "precio": prices,
            "sma_corta": prices.rolling(short).mean(),
            "sma_larga": prices.rolling(long).mean(),
        }
    )


def compute_signal(mas: pd.DataFrame) -> pd.Series:
    """Señal de posición: 1 (dentro de mercado) cuando la SMA corta está por
    encima de la larga (cruce dorado), 0 cuando está por debajo (cruce de la
    muerte). No incluye venta en corto.
    """
    return (mas["sma_corta"] > mas["sma_larga"]).astype(int)


def tradeable_signal(signal: pd.Series) -> pd.Series:
    """Desplaza la señal un día para evitar look-ahead bias: la posición del
    día t se decide con el cierre de t-1, nunca con el cierre del propio día t
    (ese cierre todavía no se conoce cuando se abre la sesión de t).
    """
    return signal.shift(1).fillna(0).astype(int)


def crossover_points(signal: pd.Series) -> pd.Series:
    """Días en los que cambia la señal: +1 = cruce dorado (entrada), -1 = cruce
    de la muerte (salida), 0 = sin cambio. Útil para marcar operaciones en el gráfico.
    """
    return signal.diff().fillna(0).astype(int)
