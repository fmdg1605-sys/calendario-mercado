"""
macro_calendar.py
Calendario macroeconómico curado: EEUU (FOMC, CPI, PMI/ISM, PBI) + Eurozona (BCE, HICP, PMI).

Finnhub free tier NO trae calendario macro, así que estas fechas se cargan a mano.
Fuentes oficiales EEUU:
  - FOMC: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
  - CPI:  https://www.bls.gov/schedule/news_release/cpi.htm
  - ISM Manufacturing/Services PMI: https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/
  - PBI (GDP): https://www.bea.gov/news/schedule
Fuentes oficiales Eurozona:
  - BCE: https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html
  - HICP: https://ec.europa.eu/eurostat/web/products-euro-indicators
  - PMI compuesto: https://www.pmi.spglobal.com (HCOB Eurozone Composite PMI)

Cada evento tiene "region": "us" o "europe", usado por app.js para no mezclar
eventos macro de EEUU cuando el filtro de región está en EUROPA (y viceversa).

Convención de "hour" (igual que earnings, para reusar el mismo render):
  "dmh" = durante el día/rueda (no hay antes/después de apertura para datos macro)

Cada evento incluye "confirmed": True si la fecha está publicada oficialmente por la
fuente, False si es una proyección basada en el patrón habitual de publicación
(ej. "primer día hábil del mes" para ISM, o "último día hábil del mes" para HICP)
que todavía no fue confirmada por la fuente.

Revisar y actualizar esta lista cuando la fuente oficial publique el calendario 2027.
Última revisión: agosto 2026.
"""

MACRO_EVENTS = [
    # =====================================================================
    # FOMC — Reuniones de política monetaria (decisión de tasas)
    # Fuente: Federal Reserve Board, calendario oficial 2026
    # Todas las reuniones: comunicado 2:00pm ET, conferencia de prensa 2:30pm ET
    # =====================================================================
    {"date": "2026-01-28", "type": "FOMC", "title": "Decisión de tasas FOMC (ene)",
     "description": "Reunión de dos días (27-28 ene). Comunicado y conferencia de prensa.",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-03-18", "type": "FOMC", "title": "Decisión de tasas FOMC (mar) + SEP",
     "description": "Reunión de dos días (17-18 mar). Incluye Summary of Economic Projections (dot plot).",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-04-29", "type": "FOMC", "title": "Decisión de tasas FOMC (abr)",
     "description": "Reunión de dos días (28-29 abr). Comunicado y conferencia de prensa.",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-06-17", "type": "FOMC", "title": "Decisión de tasas FOMC (jun) + SEP",
     "description": "Reunión de dos días (16-17 jun). Incluye Summary of Economic Projections (dot plot).",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-07-29", "type": "FOMC", "title": "Decisión de tasas FOMC (jul)",
     "description": "Reunión de dos días (28-29 jul). Comunicado y conferencia de prensa.",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-09-16", "type": "FOMC", "title": "Decisión de tasas FOMC (sep) + SEP",
     "description": "Reunión de dos días (15-16 sep). Incluye Summary of Economic Projections (dot plot).",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-10-28", "type": "FOMC", "title": "Decisión de tasas FOMC (oct)",
     "description": "Reunión de dos días (27-28 oct). Comunicado y conferencia de prensa.",
     "source": "federalreserve.gov", "confirmed": True},
    {"date": "2026-12-09", "type": "FOMC", "title": "Decisión de tasas FOMC (dic) + SEP",
     "description": "Reunión de dos días (8-9 dic). Incluye Summary of Economic Projections (dot plot).",
     "source": "federalreserve.gov", "confirmed": True},

    # =====================================================================
    # CPI — Índice de Precios al Consumidor (inflación)
    # Fuente: BLS, calendario oficial (algunas fechas fueron reprogramadas por
    # el cierre de gobierno de oct-nov 2025)
    # =====================================================================
    {"date": "2026-01-13", "type": "CPI", "title": "CPI diciembre 2025",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-02-13", "type": "CPI", "title": "CPI enero 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET. Reprogramado del 11 al 13 de feb.",
     "source": "bls.gov", "confirmed": True},
    {"date": "2026-03-11", "type": "CPI", "title": "CPI febrero 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-04-10", "type": "CPI", "title": "CPI marzo 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-05-12", "type": "CPI", "title": "CPI abril 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-06-10", "type": "CPI", "title": "CPI mayo 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-07-14", "type": "CPI", "title": "CPI junio 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-08-12", "type": "CPI", "title": "CPI julio 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-09-11", "type": "CPI", "title": "CPI agosto 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-10-14", "type": "CPI", "title": "CPI septiembre 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-11-10", "type": "CPI", "title": "CPI octubre 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},
    {"date": "2026-12-10", "type": "CPI", "title": "CPI noviembre 2026",
     "description": "Índice de Precios al Consumidor, 8:30am ET.", "source": "bls.gov", "confirmed": True},

    # =====================================================================
    # ISM Manufacturing PMI — 1er día hábil del mes (excepción: 2do en enero), 10am ET
    # Fuente: ismworld.org
    # =====================================================================
    {"date": "2026-01-05", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (dic)",
     "description": "PMI manufactura, 10:00am ET. Excepción de calendario en enero.",
     "source": "ismworld.org", "confirmed": True},
    {"date": "2026-02-02", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (ene)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-03-02", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (feb)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": False},
    {"date": "2026-04-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (mar)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": False},
    {"date": "2026-05-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (abr)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-06-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (may)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-07-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (jun)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-08-03", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (jul)",
     "description": "PMI manufactura, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-09-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (ago)",
     "description": "PMI manufactura, 10:00am ET (proyectado: 1er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-10-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (sep)",
     "description": "PMI manufactura, 10:00am ET (proyectado: 1er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-11-02", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (oct)",
     "description": "PMI manufactura, 10:00am ET (proyectado: 1er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-12-01", "type": "PMI_MFG", "title": "ISM Manufacturing PMI (nov)",
     "description": "PMI manufactura, 10:00am ET (proyectado: 1er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},

    # =====================================================================
    # ISM Services PMI — 3er día hábil del mes, 10am ET
    # Fuente: ismworld.org
    # =====================================================================
    {"date": "2026-08-05", "type": "PMI_SVC", "title": "ISM Services PMI (jul)",
     "description": "PMI servicios, 10:00am ET.", "source": "ismworld.org", "confirmed": True},
    {"date": "2026-09-03", "type": "PMI_SVC", "title": "ISM Services PMI (ago)",
     "description": "PMI servicios, 10:00am ET (proyectado: 3er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-10-05", "type": "PMI_SVC", "title": "ISM Services PMI (sep)",
     "description": "PMI servicios, 10:00am ET (proyectado: 3er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-11-04", "type": "PMI_SVC", "title": "ISM Services PMI (oct)",
     "description": "PMI servicios, 10:00am ET (proyectado: 3er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},
    {"date": "2026-12-03", "type": "PMI_SVC", "title": "ISM Services PMI (nov)",
     "description": "PMI servicios, 10:00am ET (proyectado: 3er día hábil del mes).",
     "source": "ismworld.org", "confirmed": False},

    # =====================================================================
    # PBI (GDP) — BEA, 8:30am ET
    # =====================================================================
    {"date": "2026-07-30", "type": "GDP", "title": "PBI T2 2026 (estimación avance)",
     "description": "Real GDP, estimación avance del 2do trimestre 2026, 8:30am ET.",
     "source": "bea.gov", "confirmed": True},
    {"date": "2026-08-26", "type": "GDP", "title": "PBI T2 2026 (2da estimación)",
     "description": "Real GDP, segunda estimación del 2do trimestre + corporate profits, 8:30am ET.",
     "source": "bea.gov", "confirmed": True},
    {"date": "2026-09-24", "type": "GDP", "title": "PBI T2 2026 (3ra estimación)",
     "description": "Real GDP, tercera estimación del 2do trimestre 2026, 8:30am ET (fecha proyectada).",
     "source": "bea.gov", "confirmed": False},
    {"date": "2026-10-29", "type": "GDP", "title": "PBI T3 2026 (estimación avance)",
     "description": "Real GDP, estimación avance del 3er trimestre 2026, 8:30am ET (fecha proyectada).",
     "source": "bea.gov", "confirmed": False},
    {"date": "2026-11-25", "type": "GDP", "title": "PBI T3 2026 (2da estimación)",
     "description": "Real GDP, segunda estimación del 3er trimestre 2026, 8:30am ET (fecha proyectada).",
     "source": "bea.gov", "confirmed": False},
    {"date": "2026-12-22", "type": "GDP", "title": "PBI T3 2026 (3ra estimación)",
     "description": "Real GDP, tercera estimación del 3er trimestre 2026, 8:30am ET (fecha proyectada).",
     "source": "bea.gov", "confirmed": False},
]

# Todo lo de arriba es EEUU. Lo taggeamos acá en vez de repetir "region": "us" en
# cada uno de los ~43 dicts de arriba.
for _e in MACRO_EVENTS:
    _e.setdefault("region", "us")

# =====================================================================
# EUROZONA — BCE (tasas), HICP (inflación) y PMI compuesto (HCOB/S&P Global)
# Se agregó esta sección porque la pestaña EUROPA quedaba vacía cuando Finnhub
# no traía earnings en la ventana de días elegida: ahora la región EUROPA
# siempre tiene contenido propio, no depende de que haya balances esa semana.
# Fuentes oficiales:
#   - BCE: https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html
#   - HICP: https://ec.europa.eu/eurostat/web/products-euro-indicators
#   - PMI compuesto: https://www.pmi.spglobal.com (HCOB Eurozone Composite PMI)
# =====================================================================
EUROPE_MACRO_EVENTS = [
    # --- BCE: decisión de tasas, 14:15 CET + conferencia de prensa 14:45 CET ---
    {"date": "2026-09-10", "type": "ECB", "title": "Decisión de tasas BCE (sep)",
     "description": "Reunión del Consejo de Gobierno en Fráncfort. Comunicado 14:15 CET, conferencia 14:45 CET.",
     "source": "ecb.europa.eu", "confirmed": True, "region": "europe"},
    {"date": "2026-10-29", "type": "ECB", "title": "Decisión de tasas BCE (oct)",
     "description": "Reunión del Consejo de Gobierno en Fráncfort. Comunicado 14:15 CET, conferencia 14:45 CET.",
     "source": "ecb.europa.eu", "confirmed": True, "region": "europe"},
    {"date": "2026-12-17", "type": "ECB", "title": "Decisión de tasas BCE (dic) + proyecciones",
     "description": "Reunión del Consejo de Gobierno en Fráncfort. Incluye proyecciones macroeconómicas trimestrales.",
     "source": "ecb.europa.eu", "confirmed": True, "region": "europe"},

    # --- HICP: inflación de la Eurozona (flash estimate, Eurostat) ---
    {"date": "2026-08-31", "type": "CPI_EZ", "title": "HICP Eurozona agosto 2026 (flash)",
     "description": "Estimación preliminar de inflación (HICP) de la Eurozona, Eurostat (fecha proyectada: último día hábil del mes).",
     "source": "eurostat", "confirmed": False, "region": "europe"},
    {"date": "2026-09-30", "type": "CPI_EZ", "title": "HICP Eurozona septiembre 2026 (flash)",
     "description": "Estimación preliminar de inflación (HICP) de la Eurozona, Eurostat (fecha proyectada: último día hábil del mes).",
     "source": "eurostat", "confirmed": False, "region": "europe"},
    {"date": "2026-10-30", "type": "CPI_EZ", "title": "HICP Eurozona octubre 2026 (flash)",
     "description": "Estimación preliminar de inflación (HICP) de la Eurozona, Eurostat (fecha proyectada: último día hábil del mes).",
     "source": "eurostat", "confirmed": False, "region": "europe"},
    {"date": "2026-11-30", "type": "CPI_EZ", "title": "HICP Eurozona noviembre 2026 (flash)",
     "description": "Estimación preliminar de inflación (HICP) de la Eurozona, Eurostat (fecha proyectada: último día hábil del mes).",
     "source": "eurostat", "confirmed": False, "region": "europe"},

    # --- PMI compuesto Eurozona (flash, HCOB/S&P Global) ---
    {"date": "2026-08-21", "type": "PMI_EZ", "title": "PMI Compuesto Eurozona agosto 2026 (flash)",
     "description": "HCOB Flash Eurozone Composite PMI, S&P Global (fecha proyectada, suele salir ~día 22-24 del mes).",
     "source": "pmi.spglobal.com", "confirmed": False, "region": "europe"},
    {"date": "2026-09-23", "type": "PMI_EZ", "title": "PMI Compuesto Eurozona septiembre 2026 (flash)",
     "description": "HCOB Flash Eurozone Composite PMI, S&P Global (fecha proyectada, suele salir ~día 22-24 del mes).",
     "source": "pmi.spglobal.com", "confirmed": False, "region": "europe"},
    {"date": "2026-10-23", "type": "PMI_EZ", "title": "PMI Compuesto Eurozona octubre 2026 (flash)",
     "description": "HCOB Flash Eurozone Composite PMI, S&P Global (fecha proyectada, suele salir ~día 22-24 del mes).",
     "source": "pmi.spglobal.com", "confirmed": False, "region": "europe"},
    {"date": "2026-11-23", "type": "PMI_EZ", "title": "PMI Compuesto Eurozona noviembre 2026 (flash)",
     "description": "HCOB Flash Eurozone Composite PMI, S&P Global (fecha proyectada, suele salir ~día 22-24 del mes).",
     "source": "pmi.spglobal.com", "confirmed": False, "region": "europe"},
    {"date": "2026-12-16", "type": "PMI_EZ", "title": "PMI Compuesto Eurozona diciembre 2026 (flash)",
     "description": "HCOB Flash Eurozone Composite PMI, S&P Global (fecha proyectada, suele salir un poco antes por las fiestas).",
     "source": "pmi.spglobal.com", "confirmed": False, "region": "europe"},
]

MACRO_EVENTS = MACRO_EVENTS + EUROPE_MACRO_EVENTS

# Etiquetas legibles para el frontend
MACRO_TYPE_LABEL = {
    "FOMC": "FOMC · Tasa de interés",
    "CPI": "CPI · Inflación",
    "PMI_MFG": "ISM PMI Manufactura",
    "PMI_SVC": "ISM PMI Servicios",
    "GDP": "PBI (GDP)",
    "ECB": "BCE · Tasa de interés",
    "CPI_EZ": "HICP · Inflación Eurozona",
    "PMI_EZ": "PMI Compuesto Eurozona",
}


def get_macro_events(date_from: str, date_to: str) -> list[dict]:
    """Devuelve los eventos macro curados dentro del rango [date_from, date_to] (YYYY-MM-DD)."""
    return [
        {**e, "label": MACRO_TYPE_LABEL.get(e["type"], e["type"])}
        for e in MACRO_EVENTS
        if date_from <= e["date"] <= date_to
    ]


if __name__ == "__main__":
    events = get_macro_events("2026-01-01", "2026-12-31")
    print(f"Eventos macro cargados: {len(events)}")
    for e in events:
        flag = "OK" if e["confirmed"] else "proyectado"
        print(f"  {e['date']} [{e['type']:8s}] {e['title']} ({flag})")
