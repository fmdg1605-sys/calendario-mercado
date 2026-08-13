"""
api/news.py
Vercel Python Serverless Function.
Proxea /news de Finnhub en el momento del request, para que el botón de refresh
del frontend traiga noticias reales sin exponer la API key en el cliente.

No requiere dependencias externas (usa urllib de la stdlib) para minimizar el
cold start y no necesitar un requirements.txt propio para esta función.

Vercel detecta este archivo automáticamente por estar en /api y tener
extensión .py (no hace falta vercel.json para esto).
"""

import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key = os.environ.get("FINNHUB_API_KEY")
        if not api_key:
            self._send_json(500, {"error": "Falta FINNHUB_API_KEY en las variables de entorno de Vercel."})
            return

        url = f"{FINNHUB_NEWS_URL}?category=general&token={api_key}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "calendario-mercado/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            self._send_json(exc.code, {"error": f"Finnhub devolvió {exc.code}"})
            return
        except Exception as exc:
            self._send_json(502, {"error": f"No se pudo contactar a Finnhub: {exc}"})
            return

        if not isinstance(raw, list):
            self._send_json(502, {"error": "Respuesta inesperada de Finnhub."})
            return

        news_out = [
            {
                "headline": n.get("headline", ""),
                "summary": n.get("summary", ""),
                "source": n.get("source", ""),
                "url": n.get("url", ""),
                "datetime": n.get("datetime"),
                "category": n.get("category", "general"),
                "related_tickers": [],
            }
            for n in raw[:60]
        ]

        self._send_json(200, {"news": news_out})

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
