"""Dashboard HTML interactivo con Plotly: un único archivo autocontenido en outputs/.

Mismo sistema de diseño que el Proyecto 1 (paleta ya validada con el script de
accesibilidad del skill dataviz): reutilizar los tokens de color evita tener que
re-validar una paleta nueva y da continuidad visual entre proyectos del portfolio.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import SMA_LONG, SMA_SHORT, TICKER_NAME

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
RED = "#e34948"

SURFACE = "#fcfcfb"
PAGE_PLANE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
GOOD = "#006300"
CRITICAL = "#d03b3b"
BORDER = "rgba(11,11,11,0.10)"

FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def _base_layout(title: str, **extra) -> dict:
    layout = dict(
        title=dict(text=title, font=dict(family=FONT_FAMILY, size=15, color=INK_PRIMARY)),
        font=dict(family=FONT_FAMILY, size=12, color=INK_SECONDARY),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        legend=dict(font=dict(color=INK_SECONDARY, size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=30, t=50, b=40),
    )
    layout.update(extra)
    return layout


def _axis(**extra) -> dict:
    axis = dict(
        gridcolor=GRIDLINE,
        gridwidth=1,
        linecolor=BASELINE,
        tickfont=dict(color=INK_MUTED, size=11),
        title_font=dict(color=INK_SECONDARY, size=12),
        zeroline=False,
    )
    axis.update(extra)
    return axis


def _equity_curve_figure(result: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=result.index,
            y=result["equity_estrategia"],
            mode="lines",
            name="Estrategia (momentum SMA)",
            line=dict(color=BLUE, width=2),
            hovertemplate="%{y:,.0f} €<extra>Estrategia</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.index,
            y=result["equity_benchmark"],
            mode="lines",
            name="Benchmark (buy & hold)",
            line=dict(color=INK_SECONDARY, width=2, dash="dash"),
            hovertemplate="%{y:,.0f} €<extra>Benchmark</extra>",
        )
    )
    fig.update_layout(
        **_base_layout(
            "Curva de capital: estrategia vs. benchmark",
            xaxis=_axis(),
            yaxis=_axis(title="Capital (€)"),
            hovermode="x unified",
            hoverlabel=dict(bgcolor=SURFACE, font=dict(color=INK_PRIMARY, family=FONT_FAMILY)),
        )
    )
    return fig


def _price_signals_figure(mas: pd.DataFrame, crossover: pd.Series) -> go.Figure:
    buys = mas.index[crossover == 1]
    sells = mas.index[crossover == -1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=mas.index, y=mas["precio"], mode="lines", name=TICKER_NAME,
            line=dict(color=INK_MUTED, width=1.5),
            hovertemplate="%{y:.0f}<extra>" + TICKER_NAME + "</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=mas.index, y=mas["sma_corta"], mode="lines", name=f"SMA {SMA_SHORT}",
            line=dict(color=BLUE, width=2),
            hovertemplate="%{y:.0f}<extra>SMA " + str(SMA_SHORT) + "</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=mas.index, y=mas["sma_larga"], mode="lines", name=f"SMA {SMA_LONG}",
            line=dict(color=ORANGE, width=2),
            hovertemplate="%{y:.0f}<extra>SMA " + str(SMA_LONG) + "</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=buys, y=mas.loc[buys, "precio"], mode="markers", name="Compra",
            marker=dict(symbol="triangle-up", size=11, color=GOOD, line=dict(width=1.5, color=SURFACE)),
            hovertemplate="Compra: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sells, y=mas.loc[sells, "precio"], mode="markers", name="Venta",
            marker=dict(symbol="triangle-down", size=11, color=CRITICAL, line=dict(width=1.5, color=SURFACE)),
            hovertemplate="Venta: %{y:.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        **_base_layout(
            "Precio, medias móviles y señales de cruce",
            xaxis=_axis(),
            yaxis=_axis(title="Precio"),
            hovermode="closest",
            hoverlabel=dict(bgcolor=SURFACE, font=dict(color=INK_PRIMARY, family=FONT_FAMILY)),
        )
    )
    return fig


def _delta_html(value: float, as_pct: bool = True) -> str:
    color = GOOD if value >= 0 else CRITICAL
    arrow = "▲" if value >= 0 else "▼"
    text = f"{value * 100:+.1f}%" if as_pct else f"{value:+.2f}"
    return f'<span style="color:{color}; font-variant-numeric: tabular-nums;">{arrow} {text}</span>'


def _summary_table_html(strategy: dict, benchmark: dict) -> str:
    rows = [
        ("Rentabilidad anualizada", _delta_html(strategy["rentabilidad_anualizada"]), _delta_html(benchmark["rentabilidad_anualizada"])),
        ("Volatilidad anualizada", f'{strategy["volatilidad_anualizada"] * 100:.1f}%', f'{benchmark["volatilidad_anualizada"] * 100:.1f}%'),
        ("Sharpe Ratio", f'{strategy["sharpe_ratio"]:.2f}', f'{benchmark["sharpe_ratio"]:.2f}'),
        ("Máximo drawdown", f'{strategy["max_drawdown"] * 100:.1f}%', f'{benchmark["max_drawdown"] * 100:.1f}%'),
    ]
    body = "".join(
        f"<tr><td class='asset-cell'>{label}</td><td class='num'>{s}</td><td class='num'>{b}</td></tr>"
        for label, s, b in rows
    )
    return (
        '<table class="summary-table"><thead><tr>'
        "<th>Métrica</th><th>Estrategia</th><th>Benchmark</th>"
        "</tr></thead><tbody>" + body + "</tbody></table>"
    )


def _stat_tile(label: str, value: str, sublabel: str) -> str:
    return f"""<div class="tile">
  <div class="tile-label">{label}</div>
  <div class="tile-value">{value}</div>
  <div class="tile-sublabel">{sublabel}</div>
</div>"""


def _kpi_tiles_html(strategy: dict, benchmark: dict, n_trades: int) -> str:
    outperformance = strategy["rentabilidad_anualizada"] - benchmark["rentabilidad_anualizada"]
    tiles = [
        _stat_tile("Rentabilidad anualizada — estrategia", f'{strategy["rentabilidad_anualizada"] * 100:+.1f}%', "momentum SMA"),
        _stat_tile("Rentabilidad anualizada — benchmark", f'{benchmark["rentabilidad_anualizada"] * 100:+.1f}%', "buy & hold"),
        _stat_tile("Sharpe Ratio — estrategia", f'{strategy["sharpe_ratio"]:.2f}', f'benchmark: {benchmark["sharpe_ratio"]:.2f}'),
        _stat_tile("Diferencia vs. benchmark", f'{outperformance * 100:+.1f} pp', "rentabilidad anualizada"),
        _stat_tile("Operaciones ejecutadas", str(n_trades), "cruces dorados en el periodo"),
    ]
    return '<div class="tiles">' + "".join(tiles) + "</div>"


def build_dashboard(
    result: pd.DataFrame,
    mas: pd.DataFrame,
    crossover: pd.Series,
    strategy_perf: dict,
    benchmark_perf: dict,
    n_trades: int,
) -> Path:
    equity_html = pio.to_html(
        _equity_curve_figure(result), full_html=False, include_plotlyjs="cdn", config={"displaylogo": False}
    )
    signals_html = pio.to_html(
        _price_signals_figure(mas, crossover), full_html=False, include_plotlyjs=False, config={"displaylogo": False}
    )
    table_html = _summary_table_html(strategy_perf, benchmark_perf)
    tiles_html = _kpi_tiles_html(strategy_perf, benchmark_perf, n_trades)

    date_start = result.index.min().strftime("%b %Y")
    date_end = result.index.max().strftime("%b %Y")

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proyecto 2 — Momentum Backtest</title>
<style>
  :root {{
    --surface: {SURFACE};
    --page-plane: {PAGE_PLANE};
    --ink-primary: {INK_PRIMARY};
    --ink-secondary: {INK_SECONDARY};
    --ink-muted: {INK_MUTED};
    --gridline: {GRIDLINE};
    --border: {BORDER};
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: {FONT_FAMILY};
    margin: 0;
    background: var(--page-plane);
    color: var(--ink-primary);
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px 64px; }}

  .hero {{
    background: linear-gradient(135deg, #5e1630 0%, #d6472a 100%);
    color: #ffffff;
    padding: 48px 24px 40px;
    margin-bottom: 28px;
  }}
  .hero-inner {{ max-width: 1080px; margin: 0 auto; }}
  .hero h1 {{ font-size: 1.75rem; margin: 0 0 8px; font-weight: 700; }}
  .hero p {{ margin: 0; color: rgba(255,255,255,0.85); font-size: 0.95rem; }}
  .hero .meta {{ margin-top: 18px; font-size: 0.8rem; color: rgba(255,255,255,0.65); letter-spacing: 0.02em; }}

  .tiles {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin: 0 0 28px;
  }}
  .tile {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
  }}
  .tile-label {{ font-size: 0.72rem; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.04em; }}
  .tile-value {{ font-size: 1.55rem; font-weight: 700; color: var(--ink-primary); margin: 6px 0 2px; }}
  .tile-sublabel {{ font-size: 0.8rem; color: var(--ink-secondary); }}

  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 22px;
  }}
  .card h2 {{ font-size: 1.05rem; margin: 0 0 16px; color: var(--ink-primary); font-weight: 600; }}

  .summary-table {{ border-collapse: collapse; width: 100%; font-size: 0.88rem; }}
  .summary-table th {{
    text-align: right; padding: 8px 12px; color: var(--ink-muted);
    font-weight: 500; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.03em;
    border-bottom: 1px solid var(--gridline);
  }}
  .summary-table td {{
    padding: 10px 12px; text-align: right; border-bottom: 1px solid var(--gridline);
    color: var(--ink-primary); font-variant-numeric: tabular-nums;
  }}
  .summary-table th:first-child, .summary-table td:first-child {{ text-align: left; }}
  .summary-table tbody tr:hover {{ background: var(--page-plane); }}
  .asset-cell {{ font-weight: 600; }}

  footer {{ text-align: center; font-size: 0.78rem; color: var(--ink-muted); padding-top: 8px; }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-inner">
    <h1>Momentum Backtest — Cruce de Medias Móviles</h1>
    <p>Estrategia SMA {SMA_SHORT}/{SMA_LONG} sobre {TICKER_NAME}, simulada a mano y comparada contra buy &amp; hold.</p>
    <div class="meta">{date_start} — {date_end} · datos diarios vía yfinance</div>
  </div>
</div>

<div class="wrap">

{tiles_html}

<div class="card">
  <h2>Estrategia vs. benchmark</h2>
  {table_html}
</div>

<div class="card">
  <h2>Curva de capital</h2>
  {equity_html}
</div>

<div class="card">
  <h2>Precio, medias móviles y señales</h2>
  {signals_html}
</div>

<footer>Proyecto 2 · Roadmap Quant · Python (pandas, numpy, yfinance, Plotly)</footer>

</div>
</body>
</html>"""

    OUTPUTS_DIR.mkdir(exist_ok=True)
    out_path = OUTPUTS_DIR / "dashboard.html"
    out_path.write_text(page, encoding="utf-8")
    return out_path
