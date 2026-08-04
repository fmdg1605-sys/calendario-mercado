"""
build_data.py
Orquesta todo el pipeline y escribe site/data.json, que es lo único que lee el sitio estático.

Uso:
    python build_data.py                     # próximos 21 días de earnings (default)
    python build_data.py --days 45            # ventana más larga
    python build_data.py --no-news            # saltea noticias (más rápido para pruebas)

Requiere FINNHUB_API_KEY en el entorno o en un archivo .env en la raíz del proyecto.
"""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from universe import get_all_tickers_flat
from fetch_finnhub import fetch_earnings_in_chunks, fetch_general_news

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"


def build(days_ahead: int, include_news: bool) -> dict:
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        raise SystemExit(
            "Falta FINNHUB_API_KEY. Copiá .env.example a .env y pegá tu key ahí "
            "(NUNCA la pegues en el código ni la subas a git)."
        )

    print("1/4 Armando universo de tickers (S&P500 + Europa + China ADRs)...")
    universe = get_all_tickers_flat()
    ticker_lookup = {item["ticker"]: item for item in universe}
    print(f"   Universo total: {len(universe)} tickers")

    today = datetime.now(timezone.utc).date()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    print(f"2/4 Trayendo calendario de earnings de Finnhub ({date_from} -> {date_to})...")
    raw_earnings = fetch_earnings_in_chunks(api_key, date_from, date_to)
    print(f"   Earnings totales devueltos por Finnhub: {len(raw_earnings)}")

    print("3/4 Filtrando earnings contra nuestro universo...")
    earnings_out = []
    for e in raw_earnings:
        symbol = e.get("symbol")
        match = ticker_lookup.get(symbol)
        if not match:
            continue
        earnings_out.append({
            "ticker": symbol,
            "company": match["name"],
            "region": match["region"],
            "date": e.get("date"),
            "hour": e.get("hour"),  # "bmo" (before market open) | "amc" (after close) | "dmh"
            "eps_estimate": e.get("epsEstimate"),
            "eps_actual": e.get("epsActual"),
            "revenue_estimate": e.get("revenueEstimate"),
            "revenue_actual": e.get("revenueActual"),
            "quarter": e.get("quarter"),
            "year": e.get("year"),
        })
    earnings_out.sort(key=lambda x: (x["date"] or "", x["ticker"]))
    print(f"   Earnings relevantes (dentro del universo): {len(earnings_out)}")

    news_out = []
    if include_news:
        print("4/4 Trayendo noticias generales de mercado...")
        raw_news = fetch_general_news(api_key, category="general")
        universe_names = {item["ticker"]: item["name"] for item in universe}
        for n in raw_news[:150]:
            headline = n.get("headline", "")
            related = [
                t for t, name in universe_names.items()
                if t in headline.split() or name.split()[0] in headline
            ]
            news_out.append({
                "headline": headline,
                "summary": n.get("summary", ""),
                "source": n.get("source", ""),
                "url": n.get("url", ""),
                "datetime": n.get("datetime"),  # unix timestamp
                "category": n.get("category", "general"),
                "related_tickers": related[:5],
            })
    else:
        print("4/4 Noticias salteadas (--no-news)")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {"from": date_from, "to": date_to},
        "universe_size": {
            "us": len([u for u in universe if u["region"] == "us"]),
            "europe": len([u for u in universe if u["region"] == "europe"]),
            "china_adr": len([u for u in universe if u["region"] == "china_adr"]),
        },
        "earnings": earnings_out,
        "news": news_out,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=21, help="Días hacia adelante a traer (default 21)")
    parser.add_argument("--no-news", action="store_true", help="Saltear noticias")
    args = parser.parse_args()

    data = build(days_ahead=args.days, include_news=not args.no_news)

    SITE_DIR.mkdir(exist_ok=True)
    out_path = SITE_DIR / "data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo. Escribí {out_path} con {len(data['earnings'])} earnings y {len(data['news'])} noticias.")


if __name__ == "__main__":
    main()
