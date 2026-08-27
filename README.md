# 📈 Proyecto 2 — Momentum Backtest Construido Desde Cero

> Una estrategia de cruce de medias móviles, simulada día a día a mano — sin `backtrader` ni `bt` — para entender de verdad el mecanismo de un backtest, no solo su resultado.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-vectorizado-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-dashboard-3F4F75?logo=plotly&logoColor=white)
![yfinance](https://img.shields.io/badge/yfinance-datos%20de%20mercado-blueviolet)

---

## Qué hace

Simula una estrategia de **cruce de medias móviles** (SMA 50 / SMA 200, "cruce dorado" / "cruce de la muerte") sobre el IBEX 35, calcula sus métricas (rentabilidad anualizada, Sharpe Ratio, máximo drawdown) y las compara contra un benchmark **buy & hold** del mismo activo y periodo. Toda la simulación día a día está escrita a mano con `pandas` vectorizado — deliberadamente sin ninguna librería de backtesting, porque el objetivo es poder defender el mecanismo, no solo el resultado.

## Vista previa del dashboard

| Curva de capital | Precio, SMA y señales |
|---|---|
| ![Curva de capital](outputs/curva_capital.png) | ![Precio y señales](outputs/precio_senales.png) |

La versión interactiva completa está en [`outputs/dashboard.html`](outputs/dashboard.html): ábrelo con doble clic, no necesita servidor.

## Estructura del proyecto

A diferencia del [Proyecto 1](../proyecto-1-analisis-mercado), aquí `src/` se organiza por etapas del backtest en lugar de un pipeline plano, y los parámetros de la estrategia viven aparte del código en `config/`:

```
proyecto-2-momentum-backtest/
├── README.md
├── requirements.txt
├── config/
│   └── strategy.py       <- ticker, ventanas SMA, capital inicial, tasa libre de riesgo
├── data/                 <- caché de precios descargados (prices.csv)
├── notebooks/            <- exploración en Jupyter
├── src/
│   ├── data.py             <- descarga y caché de precios (yfinance)
│   ├── signals.py           <- medias móviles y señal de cruce (con desplazamiento anti-look-ahead)
│   ├── backtest.py           <- simulación vectorizada de la cartera, sin librerías de backtesting
│   ├── metrics.py              <- rentabilidad anualizada, Sharpe Ratio a mano, máximo drawdown
│   ├── visualize.py             <- gráficos estáticos (matplotlib) -> outputs/*.png
│   ├── dashboard.py              <- dashboard interactivo (Plotly) -> outputs/dashboard.html
│   └── main.py                    <- orquesta todo el pipeline
└── outputs/              <- gráficos y dashboard generados
```

## Cómo ejecutarlo

```bash
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

Al terminar, la consola imprime la comparativa estrategia vs. benchmark, y se generan en `outputs/`: `curva_capital.png`, `precio_senales.png` y `dashboard.html`.

### Nota sobre certificados SSL
Mismo mecanismo que en el Proyecto 1: si `yfinance` falla con `CERTIFICATE_VERIFY_FAILED` (típico con antivirus que inspeccionan el tráfico HTTPS, p. ej. Norton), `src/data.py` usa automáticamente un bundle de certificados local en `.certs/cacert.pem` si existe.

## Lógica de la estrategia

| Elemento | Detalle |
|---|---|
| Activo | IBEX 35 (`^IBEX`), configurable en `config/strategy.py` |
| Señal | SMA 50 > SMA 200 → dentro de mercado (posición larga); SMA 50 < SMA 200 → fuera de mercado. Sin venta en corto. |
| Anti-look-ahead | La señal calculada con el cierre del día *t* se aplica al retorno del día *t+1* (`signal.shift(1)`) — nunca se usa información que aún no existía al abrir esa sesión. |
| Simulación | `retorno_estrategia = señal_desplazada × retorno_diario_activo`, vectorizado con pandas, sin bucle día a día ni librería de backtesting. |
| Benchmark | Buy & hold del mismo activo, mismo periodo, mismo capital inicial. |

## Resultados
_(sobre los últimos ~3 años de datos, a fecha de ejecución)_

| Métrica | Estrategia | Benchmark |
|---|---|---|
| Rentabilidad anualizada | +20.8% | +28.2% |
| Volatilidad anualizada | 13.8% | 15.2% |
| Sharpe Ratio | 1.50 | 1.85 |
| Máximo drawdown | -12.6% | -12.6% |
| Operaciones ejecutadas | 1 | — |

## Conclusiones clave

- **El benchmark batió a la estrategia** en este periodo concreto (+28.2% vs. +20.8% anualizado): el IBEX 35 estuvo en tendencia alcista sostenida desde el primer día con SMA 200 disponible, así que la estrategia solo ejecutó **una** entrada (cruce dorado) y se quedó fuera de mercado durante los primeros ~200 días de "calentamiento" de la media larga — perdiéndose esa parte de la subida sin ninguna compensación en forma de menor riesgo, porque no hubo corrección lo bastante fuerte como para producir un cruce de la muerte.
- El máximo drawdown es **idéntico** en ambas series (-12.6%): una vez dentro de mercado, la estrategia no volvió a salir, así que replicó exactamente el comportamiento del benchmark durante la caída más fuerte del periodo. Esto ilustra bien un punto que sí hay que saber defender en entrevista: una estrategia de momentum **no elimina el riesgo de mercado mientras está posicionada** — solo decide cuándo entrar y salir.
- Resultado honesto y esperable: en mercados alcistas sin correcciones marcadas, una estrategia de cruce de medias suele quedarse por detrás del buy & hold porque siempre reacciona con retraso (usa datos pasados) y paga el coste de estar fuera al principio. Es exactamente el tipo de comportamiento fuera de muestra que hace peligroso conformarse con backtests sobre un único periodo/activo.

## Conceptos para poder explicar en entrevista

- **Look-ahead bias**: por qué la señal debe desplazarse un día (`shift(1)`) antes de aplicarse al retorno — si no, la estrategia "sabría" al abrir la sesión algo que en la realidad no se conoce hasta el cierre.
- **Sharpe Ratio**: qué mide (rentabilidad ajustada al riesgo total, no solo al riesgo de cola) y sus limitaciones — penaliza igual la volatilidad al alza que a la baja, y no dice nada sobre drawdowns concretos.
- **Por qué un backtest bueno no garantiza resultados futuros**: overfitting a un periodo/activo concreto, sensibilidad a las ventanas SMA elegidas, y el hecho de que una sola combinación de parámetros probada sobre un solo mercado no es evidencia robusta.
