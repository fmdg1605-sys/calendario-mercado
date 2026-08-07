"""
build_data.py
Orquesta todo el pipeline y escribe site/data.json.
"""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from universe import get_all_tickers_flat, EUROPE_PRIMARY_TICKERS
from fetch_finnhub import fetch_earnings_in_chunks, fetch_general_news, fetch_company_details
from fetch_yfinance_earnings import fetch_europe_earnings_yfinance
from macro_calendar import get_macro_events

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"


def normalize_region_str(r: str) -> str:
    if not r:
        return "us"
    s = str(r).strip().lower()
    if s in ["europe", "europa", "eu"]:
        return "europe"
    if s in ["us", "eeuu", "usa"]:
        return "us"
    if s in ["china_adr", "china", "cn", "china adr"]:
        return "china_adr"
    return s


def build(days_ahead: int, include_news: bool, macro_days_ahead: int, max_company_details: int) -> dict:
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        raise SystemExit("Falta FINNHUB_API_KEY en .env")

    print("1/4 Armando universo de tickers...")
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
        
        reg = normalize_region_str(match.get("region"))
        earnings_out.append({
            "ticker": symbol,
            "company": match["name"],
            "region": reg,
            "date": e.get("date"),
            "hour": e.get("hour"),
            "eps_estimate": e.get("epsEstimate"),
            "eps_actual": e.get("epsActual"),
            "revenue_estimate": e.get("revenueEstimate"),
            "revenue_actual": e.get("revenueActual"),
            "quarter": e.get("quarter"),
            "year": e.get("year"),
        })
    print(f"   Earnings relevantes (Finnhub): {len(earnings_out)}")

    print("3.5/6 Trayendo earnings de Europa (listado primario) vía yfinance...")
    try:
        europe_primary_earnings = fetch_europe_earnings_yfinance(
            EUROPE_PRIMARY_TICKERS, date_from, date_to
        )
    except Exception as exc:
        print(f"   [aviso] falló el fetch de yfinance para Europa: {exc}")
        europe_primary_earnings = []
    print(f"   Earnings relevantes (yfinance, Europa primaria): {len(europe_primary_earnings)}")

    earnings_out.extend(europe_primary_earnings)
    earnings_out.sort(key=lambda x: (x["date"] or "", x["ticker"]))
    print(f"   Earnings totales combinados: {len(earnings_out)}")

    print("4/6 Cargando calendario macro curado...")
    macro_date_to = (today + timedelta(days=macro_days_ahead)).strftime("%Y-%m-%d")
    raw_macro = get_macro_events(date_from, macro_date_to)
    
    macro_out = []
    for m in raw_macro:
        m_copy = dict(m)
        m_copy["region"] = normalize_region_str(m.get("region", "us"))
        macro_out.append(m_copy)

    print(f"   Eventos macro dentro de la ventana: {len(macro_out)}")

    print(f"5/6 Trayendo detalle de empresas (máx {max_company_details})...")
    company_details = {}
    tickers_needed = [e["ticker"] for e in earnings_out][:max_company_details]
    for i, ticker in enumerate(tickers_needed, start=1):
        print(f"   [{i}/{len(tickers_needed)}] {ticker}...")
        try:
            company_details[ticker] = fetch_company_details(api_key, ticker)
        except Exception as exc:
            print(f"   [aviso] error en {ticker}: {exc}")

    news_out = []
    if include_news:
        print("6/6 Trayendo noticias generales...")
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
                "datetime": n.get("datetime"),
                "category": n.get("category", "general"),
                "related_tickers": related[:5],
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {"from": date_from, "to": date_to},
        "macro_window": {"from": date_from, "to": macro_date_to},
        "universe_size": {
            "us": len([u for u in universe if normalize_region_str(u["region"]) == "us"]),
            "europe": len([u for u in universe if normalize_region_str(u["region"]) == "europe"]),
            "china_adr": len([u for u in universe if normalize_region_str(u["region"]) == "china_adr"]),
        },
        "earnings": earnings_out,
        "macro": macro_out,
        "company_details": company_details,
        "news": news_out,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--macro-days", type=int, default=180)
    parser.add_argument("--max-company-details", type=int, default=60)
    parser.add_argument("--no-news", action="store_true")
    args = parser.parse_args()

    data = build(
        days_ahead=args.days,
        include_news=not args.no_news,
        macro_days_ahead=args.macro_days,
        max_company_details=args.max_company_details,
    )

    SITE_DIR.mkdir(exist_ok=True)
    out_path = SITE_DIR / "data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo. Se escribió {out_path} con {len(data['earnings'])} earnings y {len(data['macro'])} eventos macro.")


if __name__ == "__main__":
    main()