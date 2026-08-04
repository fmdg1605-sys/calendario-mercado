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
