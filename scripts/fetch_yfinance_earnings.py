"""
fetch_yfinance_earnings.py
Trae fechas de earnings para tickers europeos de listado primario (.L, .DE, .PA, .AS, .SW)
que Finnhub free tier NO cubre en /calendar/earnings.

v2: usa Ticker.calendar en vez de Ticker.get_earnings_dates(). La primera versión
usaba get_earnings_dates(), que scrapea el HTML de la página web de Yahoo Finance
buscando un <table> — Yahoo cambió esa página (ahora la tabla se renderiza con JS)
y el método devuelve None sin avisar. Ticker.calendar en cambio pega contra la API
JSON interna de Yahoo (quoteSummary?modules=calendarEvents), mucho más estable.

Contras de este approach: Yahoo suele dar la próxima fecha de earnings como una
ventana estimada de 1-2 días (no siempre confirmada) hasta que se acerca el reporte,
y no da hora (BMO/AMC) ni EPS actual, solo el estimado.
"""

import time
from datetime import datetime, date

import yfinance as yf


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
            cal = yft.calendar
        except Exception as exc:
            print(f"   [aviso] error trayendo calendar de {symbol}: {exc}")
            time.sleep(0.3)
            continue

        if not cal:
            time.sleep(0.3)
            continue

        earnings_dates = cal.get("Earnings Date") or []
        eps_estimate = cal.get("Earnings Average")
        revenue_estimate = cal.get("Revenue Average")

        # Yahoo a veces da una ventana de 2 fechas (estimado) en vez de una sola
        # confirmada. Nos quedamos con la primera que caiga dentro de la ventana
        # pedida, para no duplicar el mismo evento dos veces.
        in_window = [d for d in earnings_dates if isinstance(d, date) and d_from <= d <= d_to]
        if in_window:
            ev_date = min(in_window)
            out.append({
                "ticker": symbol,
                "company": item["name"],
                "region": "europe",
                "date": ev_date.strftime("%Y-%m-%d"),
                # Yahoo no expone BMO/AMC de forma confiable para plazas no-US.
                "hour": None,
                "eps_estimate": eps_estimate,
                "eps_actual": None,
                "revenue_estimate": revenue_estimate,
                "revenue_actual": None,
                "quarter": None,
                "year": ev_date.year,
                "source": "yfinance",
            })

        # Cortesía con Yahoo (no es una API oficial pública, mejor no golpearla fuerte).
        time.sleep(0.3)

    return out
