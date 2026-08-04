"""
universe.py
Arma el universo de tickers para el calendario: S&P500 + principales europeas + ADRs chinos.

S&P500 se scrapea en vivo de Wikipedia (la lista cambia con el tiempo, así que no la hardcodeamos).
Europa y China son listas curadas a mano porque no hay una fuente única y confiable para scrapear
sin fricción (y porque "principales" es una decisión editorial, no un dato objetivo).
"""

import io

import pandas as pd
import requests

WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Wikipedia devuelve 403 si el pedido no trae un User-Agent que parezca un navegador.
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; econ-calendar-script/1.0)"}

# Principales europeas con sufijo de bolsa que usa yfinance/Yahoo Finance.
# .L = Londres, .DE = Frankfurt/Xetra, .PA = París, .AS = Ámsterdam, .MI = Milán, .SW = Suiza
EUROPE_TICKERS = [
    # Reino Unido (FTSE 100 - principales)
    {"ticker": "SHEL.L", "name": "Shell", "country": "UK"},
    {"ticker": "AZN.L", "name": "AstraZeneca", "country": "UK"},
    {"ticker": "HSBA.L", "name": "HSBC Holdings", "country": "UK"},
    {"ticker": "ULVR.L", "name": "Unilever", "country": "UK"},
    {"ticker": "BP.L", "name": "BP", "country": "UK"},
    {"ticker": "GSK.L", "name": "GSK", "country": "UK"},
    {"ticker": "DGE.L", "name": "Diageo", "country": "UK"},
    {"ticker": "RIO.L", "name": "Rio Tinto", "country": "UK"},
    {"ticker": "BATS.L", "name": "British American Tobacco", "country": "UK"},
    {"ticker": "REL.L", "name": "RELX", "country": "UK"},
    # Alemania (DAX - principales)
    {"ticker": "SAP.DE", "name": "SAP", "country": "DE"},
    {"ticker": "SIE.DE", "name": "Siemens", "country": "DE"},
    {"ticker": "ALV.DE", "name": "Allianz", "country": "DE"},
    {"ticker": "DTE.DE", "name": "Deutsche Telekom", "country": "DE"},
    {"ticker": "MBG.DE", "name": "Mercedes-Benz Group", "country": "DE"},
    {"ticker": "BMW.DE", "name": "BMW", "country": "DE"},
    {"ticker": "BAS.DE", "name": "BASF", "country": "DE"},
    {"ticker": "VOW3.DE", "name": "Volkswagen", "country": "DE"},
    {"ticker": "MUV2.DE", "name": "Munich Re", "country": "DE"},
    {"ticker": "IFX.DE", "name": "Infineon Technologies", "country": "DE"},
    # Francia (CAC 40 - principales)
    {"ticker": "MC.PA", "name": "LVMH", "country": "FR"},
    {"ticker": "OR.PA", "name": "L'Oréal", "country": "FR"},
    {"ticker": "TTE.PA", "name": "TotalEnergies", "country": "FR"},
    {"ticker": "SAN.PA", "name": "Sanofi", "country": "FR"},
    {"ticker": "AI.PA", "name": "Air Liquide", "country": "FR"},
    {"ticker": "SU.PA", "name": "Schneider Electric", "country": "FR"},
    {"ticker": "BNP.PA", "name": "BNP Paribas", "country": "FR"},
    {"ticker": "AIR.PA", "name": "Airbus", "country": "FR"},
    {"ticker": "EL.PA", "name": "EssilorLuxottica", "country": "FR"},
    {"ticker": "DG.PA", "name": "Vinci", "country": "FR"},
    # Otros mercados europeos relevantes
    {"ticker": "ASML.AS", "name": "ASML Holding", "country": "NL"},
    {"ticker": "NESN.SW", "name": "Nestlé", "country": "CH"},
    {"ticker": "ROG.SW", "name": "Roche Holding", "country": "CH"},
    {"ticker": "NOVN.SW", "name": "Novartis", "country": "CH"},
    {"ticker": "UBSG.SW", "name": "UBS Group", "country": "CH"},
]

# ADRs chinos que cotizan en NYSE/NASDAQ (cobertura buena en yfinance/Finnhub, a diferencia
# de las A-shares de Shanghai/Shenzhen que casi no tienen cobertura confiable).
CHINA_ADR_TICKERS = [
    {"ticker": "BABA", "name": "Alibaba Group", "country": "CN"},
    {"ticker": "JD", "name": "JD.com", "country": "CN"},
    {"ticker": "PDD", "name": "PDD Holdings (Pinduoduo)", "country": "CN"},
    {"ticker": "BIDU", "name": "Baidu", "country": "CN"},
    {"ticker": "NIO", "name": "NIO Inc.", "country": "CN"},
    {"ticker": "LI", "name": "Li Auto", "country": "CN"},
    {"ticker": "XPEV", "name": "XPeng", "country": "CN"},
    {"ticker": "BILI", "name": "Bilibili", "country": "CN"},
    {"ticker": "NTES", "name": "NetEase", "country": "CN"},
    {"ticker": "TME", "name": "Tencent Music Entertainment", "country": "CN"},
    {"ticker": "YMM", "name": "Full Truck Alliance", "country": "CN"},
    {"ticker": "BEKE", "name": "KE Holdings (Beike)", "country": "CN"},
    {"ticker": "ZTO", "name": "ZTO Express", "country": "CN"},
    {"ticker": "TCOM", "name": "Trip.com Group", "country": "CN"},
    {"ticker": "YUMC", "name": "Yum China Holdings", "country": "CN"},
    {"ticker": "HTHT", "name": "H World Group", "country": "CN"},
    {"ticker": "TAL", "name": "TAL Education Group", "country": "CN"},
    {"ticker": "IQ", "name": "iQIYI", "country": "CN"},
]


def get_sp500() -> list[dict]:
    """Scrapea la lista actual del S&P500 desde Wikipedia. Requiere internet (correr en tu máquina)."""
    resp = requests.get(WIKI_SP500_URL, headers=_HEADERS, timeout=20)
    resp.raise_for_status()
    tables = pd.read_html(io.StringIO(resp.text))
    df = tables[0]  # la primera tabla es la de constituyentes
    out = []
    for _, row in df.iterrows():
        ticker = str(row["Symbol"]).strip().replace(".", "-")  # BRK.B -> BRK-B (formato Yahoo)
        out.append({
            "ticker": ticker,
            "name": str(row["Security"]).strip(),
            "country": "US",
            "sector": str(row.get("GICS Sector", "")).strip(),
        })
    return out


def get_universe() -> dict:
    """Devuelve el universo completo agrupado por región."""
    sp500 = get_sp500()
    return {
        "us": sp500,
        "europe": EUROPE_TICKERS,
        "china_adr": CHINA_ADR_TICKERS,
    }


def get_all_tickers_flat() -> list[dict]:
    """Devuelve una lista plana de todos los tickers con su región, para usar como filtro."""
    universe = get_universe()
    flat = []
    for region, items in universe.items():
        for item in items:
            flat.append({**item, "region": region})
    return flat


if __name__ == "__main__":
    universe = get_universe()
    print(f"S&P500: {len(universe['us'])} tickers")
    print(f"Europa: {len(universe['europe'])} tickers")
    print(f"China ADRs: {len(universe['china_adr'])} tickers")