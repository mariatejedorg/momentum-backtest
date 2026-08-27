"""Simulación de la cartera aplicando la señal, vectorizada con pandas (sin
librerías de backtesting: la lógica día a día está escrita a mano)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import INITIAL_CAPITAL


def daily_returns(prices: pd.Series) -> pd.Series:
    """Retorno simple diario del activo: P_t / P_t-1 - 1."""
    return prices.pct_change().fillna(0)


def run_backtest(prices: pd.Series, tradeable_signal: pd.Series, capital: float = INITIAL_CAPITAL) -> pd.DataFrame:
    """Simula día a día la estrategia (dentro/fuera de mercado según la señal)
    y el benchmark buy & hold, ambos partiendo del mismo capital inicial.

    retorno_estrategia_t = señal_t * retorno_activo_t
    Estar fuera de mercado (señal = 0) da retorno 0 ese día — no hay short.
    """
    asset_returns = daily_returns(prices)
    strategy_returns = tradeable_signal * asset_returns

    strategy_equity = capital * (1 + strategy_returns).cumprod()
    benchmark_equity = capital * (1 + asset_returns).cumprod()

    return pd.DataFrame(
        {
            "precio": prices,
            "retorno_activo": asset_returns,
            "retorno_estrategia": strategy_returns,
            "equity_estrategia": strategy_equity,
            "equity_benchmark": benchmark_equity,
        }
    )


def count_trades(crossover: pd.Series) -> int:
    """Número de entradas (cruces dorados) ejecutadas durante el periodo."""
    return int((crossover == 1).sum())
