"""Descarga de precios históricos con yfinance para un único activo."""

import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.strategy import PERIOD, TICKER

# Algunos equipos con antivirus que inspecciona el tráfico HTTPS (p. ej. Norton)
# rompen la verificación del certificado que usa yfinance por defecto. Si existe
# un bundle de certificados local (ver README), se usa aquí; si no, se usa la
# verificación estándar. Mismo mecanismo que en Proyecto 1.
_CUSTOM_CA_BUNDLE = Path(__file__).resolve().parent.parent / ".certs" / "cacert.pem"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _build_session():
    if not _CUSTOM_CA_BUNDLE.exists():
        return None
    from curl_cffi import requests as curl_requests

    return curl_requests.Session(impersonate="chrome", verify=str(_CUSTOM_CA_BUNDLE))


def download_prices(ticker: str = TICKER, period: str = PERIOD) -> pd.Series:
    """Descarga el precio de cierre ajustado diario de un único activo."""
    raw = yf.download(ticker, period=period, auto_adjust=True, progress=False, session=_build_session())
    prices = raw["Close"][ticker]
    return prices.dropna()


def load_or_download_prices(ticker: str = TICKER, period: str = PERIOD) -> pd.Series:
    """Usa la caché en data/prices.csv si existe; si no, descarga y la guarda."""
    DATA_DIR.mkdir(exist_ok=True)
    cache_path = DATA_DIR / "prices.csv"

    if cache_path.exists():
        cached = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if ticker in cached.columns:
            return cached[ticker].dropna()

    prices = download_prices(ticker, period=period)
    prices.to_frame(name=ticker).to_csv(cache_path)
    return prices


if __name__ == "__main__":
    s = download_prices()
    print(s.tail())
