"""Métricas de rendimiento aplicables tanto a la estrategia como al benchmark."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import RISK_FREE_RATE

TRADING_DAYS_PER_YEAR = 252


def annualized_return(equity: pd.Series) -> float:
    """CAGR a partir de la curva de capital inicial y final."""
    n_years = len(equity) / TRADING_DAYS_PER_YEAR
    total_return = equity.iloc[-1] / equity.iloc[0]
    return total_return ** (1 / n_years) - 1


def annualized_volatility(returns: pd.Series) -> float:
    """Desviación típica de los retornos diarios escalada a un año (sqrt(252))."""
    return returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def sharpe_ratio(returns: pd.Series, equity: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """Sharpe Ratio calculado a mano:
    (rentabilidad anualizada - tasa libre de riesgo) / volatilidad anualizada.
    No usa ninguna función de librería de finanzas para el cálculo.
    """
    vol = annualized_volatility(returns)
    if vol == 0:
        return 0.0
    return (annualized_return(equity) - risk_free_rate) / vol


def max_drawdown(equity: pd.Series) -> float:
    """Máxima caída porcentual desde un máximo histórico de la curva de capital."""
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    return drawdown.min()


def performance_summary(returns: pd.Series, equity: pd.Series, label: str) -> dict:
    """Bloque de métricas para una serie (estrategia o benchmark)."""
    return {
        "serie": label,
        "rentabilidad_anualizada": annualized_return(equity),
        "volatilidad_anualizada": annualized_volatility(returns),
        "sharpe_ratio": sharpe_ratio(returns, equity),
        "max_drawdown": max_drawdown(equity),
    }
