"""Punto de entrada: descarga datos, calcula señales, simula el backtest y genera las visualizaciones."""

from backtest import count_trades, run_backtest
from dashboard import build_dashboard
from data import load_or_download_prices
from metrics import performance_summary
from signals import compute_signal, crossover_points, moving_averages, tradeable_signal
from visualize import plot_equity_curve, plot_price_with_signals


def main() -> None:
    prices = load_or_download_prices()

    mas = moving_averages(prices)
    raw_signal = compute_signal(mas)
    signal = tradeable_signal(raw_signal)
    crossover = crossover_points(signal)

    result = run_backtest(prices, signal)
    n_trades = count_trades(crossover)

    strategy_perf = performance_summary(result["retorno_estrategia"], result["equity_estrategia"], "Estrategia")
    benchmark_perf = performance_summary(result["retorno_activo"], result["equity_benchmark"], "Benchmark")

    print("\n=== Estrategia vs. benchmark ===")
    for perf in (strategy_perf, benchmark_perf):
        print(
            f'{perf["serie"]:>10} | rentabilidad anual.: {perf["rentabilidad_anualizada"]:+.2%} | '
            f'volatilidad: {perf["volatilidad_anualizada"]:.2%} | '
            f'Sharpe: {perf["sharpe_ratio"]:.2f} | '
            f'max drawdown: {perf["max_drawdown"]:.2%}'
        )
    print(f"\nOperaciones ejecutadas (cruces dorados): {n_trades}")

    plot_equity_curve(result)
    plot_price_with_signals(mas, crossover)
    dashboard_path = build_dashboard(result, mas, crossover, strategy_perf, benchmark_perf, n_trades)

    print(f"\nGráficos guardados en outputs/ (dashboard interactivo: {dashboard_path})")


if __name__ == "__main__":
    main()
