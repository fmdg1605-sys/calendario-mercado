"""
fetch_finnhub.py
Trae del API de Finnhub:
  1. Calendario de earnings (un solo llamado por rango de fechas, cubre TODOS los símbolos
     -> mucho más eficiente que pedir ticker por ticker).
  2. Noticias generales de mercado.

Requiere la variable de entorno FINNHUB_API_KEY (ver .env.example).
Docs: https://finnhub.io/docs/api
"""

import os
import time
import requests

BASE_URL = "https://finnhub.io/api/v1"


def _get(endpoint: str, params: dict, api_key: str) -> dict | list:
    params = {**params, "token": api_key}
    resp = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=20)
    if resp.status_code == 403:
        print(f"  [aviso] {endpoint} devolvió 403 (probablemente requiere plan pago). Se omite.")
        return {}
    resp.raise_for_status()
    return resp.json()


def fetch_earnings_calendar(api_key: str, date_from: str, date_to: str) -> list[dict]:
    """
    Trae earnings de TODOS los símbolos entre date_from y date_to (formato YYYY-MM-DD).
    Finnhub free tier soporta esto en un solo llamado.
    """
    data = _get("/calendar/earnings", {"from": date_from, "to": date_to}, api_key)
    return data.get("earningsCalendar", []) if isinstance(data, dict) else []


def fetch_general_news(api_key: str, category: str = "general") -> list[dict]:
    """Trae noticias generales de mercado. category: general | forex | crypto | merger"""
    data = _get("/news", {"category": category}, api_key)
    return data if isinstance(data, list) else []


def fetch_company_profile(api_key: str, symbol: str) -> dict:
    """Perfil de la empresa: nombre completo, país, industria, market cap, logo, sitio web, etc."""
    data = _get("/stock/profile2", {"symbol": symbol}, api_key)
    return data if isinstance(data, dict) else {}


def fetch_quote(api_key: str, symbol: str) -> dict:
    """Cotización actual: c=precio actual, d=cambio, dp=cambio %, h/l=máx/mín del día, pc=cierre previo."""
    data = _get("/quote", {"symbol": symbol}, api_key)
    return data if isinstance(data, dict) else {}


def fetch_basic_financials(api_key: str, symbol: str) -> dict:
    """Métricas financieras básicas: P/E, P/B, margen, 52w high/low, etc. (metric=all)."""
    data = _get("/stock/metric", {"symbol": symbol, "metric": "all"}, api_key)
    return data.get("metric", {}) if isinstance(data, dict) else {}


def fetch_company_details(api_key: str, symbol: str) -> dict:
    """
    Combina profile2 + quote + metric en un solo dict listo para el modal del frontend.
    Pensado para llamarse una vez por ticker (no por evento), con pausa de cortesía
    para no pasarse del rate limit del tier gratis (60 req/min).
    """
    profile = fetch_company_profile(api_key, symbol)
    time.sleep(1.05)
    quote = fetch_quote(api_key, symbol)
    time.sleep(1.05)
    metric = fetch_basic_financials(api_key, symbol)
    time.sleep(1.05)

    return {
        "ticker": symbol,
        "full_name": profile.get("name"),
        "industry": profile.get("finnhubIndustry"),
        "country": profile.get("country"),
        "exchange": profile.get("exchange"),
        "logo": profile.get("logo"),
        "web_url": profile.get("weburl"),
        "ipo": profile.get("ipo"),
        "market_cap_musd": profile.get("marketCapitalization"),  # en millones de USD
        "shares_outstanding_m": profile.get("shareOutstanding"),
        "currency": profile.get("currency"),
        "price": quote.get("c"),
        "change": quote.get("d"),
        "change_pct": quote.get("dp"),
        "day_high": quote.get("h"),
        "day_low": quote.get("l"),
        "prev_close": quote.get("pc"),
        "pe_ttm": metric.get("peBasicExclExtraTTM") or metric.get("peExclExtraTTM") or metric.get("peTTM"),
        "pb": metric.get("pbAnnual"),
        "eps_ttm": metric.get("epsBasicExclExtraItemsTTM") or metric.get("epsTTM"),
        "week52_high": metric.get("52WeekHigh"),
        "week52_low": metric.get("52WeekLow"),
        "dividend_yield": metric.get("currentDividendYieldTTM"),
        "beta": metric.get("beta"),
        "roe_ttm": metric.get("roeTTM"),
        "revenue_growth_ttm": metric.get("revenueGrowthTTMYoy"),
    }


def fetch_earnings_in_chunks(api_key: str, date_from: str, date_to: str, chunk_days: int = 7) -> list[dict]:
    """
    Finnhub a veces limita el rango por llamada en el tier gratis. Partimos el pedido
    en chunks de `chunk_days` para evitar respuestas vacías o truncadas.
    """
    from datetime import datetime, timedelta

    start = datetime.strptime(date_from, "%Y-%m-%d")
    end = datetime.strptime(date_to, "%Y-%m-%d")

    all_earnings = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), end)
        f = cursor.strftime("%Y-%m-%d")
        t = chunk_end.strftime("%Y-%m-%d")
        print(f"  Trayendo earnings {f} -> {t}...")
        all_earnings.extend(fetch_earnings_calendar(api_key, f, t))
        cursor = chunk_end + timedelta(days=1)
        time.sleep(1.1)  # cortesía con el rate limit (60 req/min en tier gratis)

    return all_earnings
