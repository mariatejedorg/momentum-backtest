"""Visualizaciones estáticas: curva de capital vs. benchmark, y precio con SMA + señales."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import TICKER_NAME

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


def plot_equity_curve(result: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(result.index, result["equity_estrategia"], label="Estrategia (momentum SMA)", linewidth=1.8)
    ax.plot(result.index, result["equity_benchmark"], label="Benchmark (buy & hold)", linewidth=1.8, linestyle="--")

    ax.set_title(f"Curva de capital: estrategia vs. benchmark ({TICKER_NAME})")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Capital")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    OUTPUTS_DIR.mkdir(exist_ok=True)
    fig.savefig(OUTPUTS_DIR / "curva_capital.png", dpi=150)
    plt.close(fig)


def plot_price_with_signals(mas: pd.DataFrame, crossover: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(mas.index, mas["precio"], label=TICKER_NAME, color="grey", alpha=0.6, linewidth=1)
    ax.plot(mas.index, mas["sma_corta"], label="SMA 50", linewidth=1.5)
    ax.plot(mas.index, mas["sma_larga"], label="SMA 200", linewidth=1.5)

    buys = mas.index[crossover == 1]
    sells = mas.index[crossover == -1]
    ax.scatter(buys, mas.loc[buys, "precio"], marker="^", color="green", s=80, label="Compra", zorder=5)
    ax.scatter(sells, mas.loc[sells, "precio"], marker="v", color="red", s=80, label="Venta", zorder=5)

    ax.set_title(f"Precio, medias móviles y señales de cruce ({TICKER_NAME})")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precio")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    OUTPUTS_DIR.mkdir(exist_ok=True)
    fig.savefig(OUTPUTS_DIR / "precio_senales.png", dpi=150)
    plt.close(fig)
