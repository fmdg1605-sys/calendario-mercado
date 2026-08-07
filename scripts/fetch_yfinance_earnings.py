"""
fetch_yfinance_earnings.py
Trae fechas de earnings para tickers europeos de listado primario (.L, .DE, .PA, .AS, .SW)
que Finnhub free tier NO cubre en /calendar/earnings.

yfinance sí tiene esta cobertura porque scrapea Yahoo Finance, que indexa las bolsas
locales directamente (no solo listados US). A cambio, el dato es más pobre que el de
Finnhub: no siempre trae EPS estimado, y nunca trae hora de reporte (BMO/AMC) porque
Yahoo no expone ese campo de forma confiable para plazas no-US.
"""

import time
from datetime import datetime, date

import yfinance as yf


def _parse_earnings_date(ts) -> date | None:
    """Normaliza un timestamp de yfinance (puede venir con o sin tz) a date naive."""
    if ts is None:
        return None
    try:
        if getattr(ts, "tzinfo", None) is not None:
            ts = ts.tz_convert("UTC").tz_localize(None)
        return ts.date()
    except Exception:
        return None


def fetch_europe_earnings_yfinance(tickers: list[dict], date_from: str, date_to: str) -> list[dict]:
    """
    tickers: lista de dicts con al menos {"ticker": ..., "name": ...} (formato de
             universe.EUROPE_PRIMARY_TICKERS).
    Devuelve earnings en el mismo shape que fetch_finnhub, para poder mezclarlos
    directo en build_data.py.
    """
    d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(date_to, "%Y-%m-%d").date()

    out = []
    for i, item in enumerate(tickers, start=1):
        symbol = item["ticker"]
        print(f"  [{i}/{len(tickers)}] {symbol} (yfinance)...")
        try:
            yft = yf.Ticker(symbol)
            df = yft.get_earnings_dates(limit=12)
        except Exception as exc:
            print(f"   [aviso] error trayendo earnings de {symbol}: {exc}")
            time.sleep(0.5)
            continue

        if df is None or df.empty:
            time.sleep(0.5)
            continue

        for ts, row in df.iterrows():
            ev_date = _parse_earnings_date(ts)
            if ev_date is None or not (d_from <= ev_date <= d_to):
                continue

            eps_estimate = row.get("EPS Estimate")
            eps_actual = row.get("Reported EPS")

            out.append({
                "ticker": symbol,
                "company": item["name"],
                "region": "europe",
                "date": ev_date.strftime("%Y-%m-%d"),
                # Yahoo no expone BMO/AMC de forma confiable para plazas no-US.
                "hour": None,
                "eps_estimate": None if _is_nan(eps_estimate) else eps_estimate,
                "eps_actual": None if _is_nan(eps_actual) else eps_actual,
                "revenue_estimate": None,
                "revenue_actual": None,
                "quarter": None,
                "year": ev_date.year,
                "source": "yfinance",
            })

        # Cortesía con Yahoo (no es una API oficial, mejor no golpearla fuerte).
        time.sleep(0.5)

    return out


def _is_nan(x) -> bool:
    try:
        return x != x  # NaN != NaN es True
    except Exception:
        return False
