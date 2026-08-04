# Calendario económico — Earnings & Noticias

Calendario de resultados trimestrales de S&P500 + principales europeas + ADRs chinos, con
noticias de mercado. Sitio estático (para Vercel/Netlify) alimentado por un `data.json`
que genera un script de Python.

## Estructura

```
econ-calendar/
├── scripts/
│   ├── universe.py        # arma el universo de tickers (S&P500 vía Wikipedia + Europa/China curados)
│   ├── fetch_finnhub.py   # llama a la API de Finnhub (earnings + noticias)
│   ├── build_data.py      # orquesta todo y escribe site/data.json
│   └── requirements.txt
├── site/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data.json          # generado por build_data.py (viene con datos de MUESTRA)
├── .github/workflows/refresh.yml   # actualiza data.json automáticamente todos los días
├── .env.example
└── .gitignore
```

## 1. Setup local (primera vez)

```bash
cd econ-calendar/scripts
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt

cd ..
cp .env.example .env
# Editá .env y pegá tu API key real de Finnhub (finnhub.io/dashboard)
```

## 2. Generar los datos

```bash
cd scripts
python build_data.py                 # trae los próximos 21 días (default)
python build_data.py --days 45        # ventana más larga
python build_data.py --no-news        # más rápido, sin noticias (para probar)
```

Esto sobreescribe `site/data.json`. Los datos de muestra que vienen en el repo son solo
para que veas el sitio andando antes de correr el script con tu propia key.

## 3. Ver el sitio localmente

El sitio es HTML/CSS/JS puro, no necesita build. Alcanza con un servidor estático simple
porque `fetch("data.json")` no funciona abriendo el archivo directo con `file://`:

```bash
cd site
python -m http.server 8000
# abrí http://localhost:8000
```

## 4. Deploy a Vercel o Netlify

Ambos funcionan igual: apuntás el hosting a la carpeta `site/` como root del proyecto
estático (sin build command, sin output directory especial — es HTML plano).

**Vercel:**
1. Subí este repo a GitHub.
2. En Vercel → "Add New Project" → importá el repo.
3. En "Root Directory" elegí `site`.
4. Framework preset: "Other". Sin build command. Deploy.

**Netlify:**
1. Subí este repo a GitHub.
2. En Netlify → "Add new site" → "Import an existing project".
3. Base directory: `site`. Build command: (vacío). Publish directory: `site`.
4. Deploy.

## 5. Automatizar la actualización diaria (recomendado)

El workflow en `.github/workflows/refresh.yml` corre todos los días a las 09:00 UTC
(~06:00 Buenos Aires), regenera `data.json` y lo commitea. Como Vercel/Netlify se
redeployan solo al detectar un push, el sitio queda actualizado sin que hagas nada.

Para que funcione:
1. Subí el repo a GitHub (con `.env` afuera — ya está en `.gitignore`, no te preocupes).
2. En GitHub → Settings → Secrets and variables → Actions → **New repository secret**:
   - Name: `FINNHUB_API_KEY`
   - Value: tu API key de Finnhub
3. Listo. También podés dispararlo a mano desde la pestaña "Actions" → "Actualizar calendario" → "Run workflow".

Si preferís no automatizarlo, corré `python build_data.py` manualmente cuando quieras
y pusheá el `data.json` actualizado — el resultado es el mismo, solo que a mano.

## Notas y limitaciones

- **A-shares chinas** (Shanghai/Shenzhen) no están incluidas — su cobertura en Finnhub/Yahoo
  es muy pobre. Se usan los ADRs que cotizan en NYSE/NASDAQ (Alibaba, JD, Baidu, etc.), que
  sí tienen datos confiables.
- **Europa** es una lista curada a mano (principales de FTSE100, DAX, CAC40 + algunas suizas
  y ASML), no el índice completo — se puede ampliar editando `EUROPE_TICKERS` en `universe.py`.
- El endpoint de **calendario económico** (tasas, inflación, PBI, etc.) de Finnhub es de pago
  en el tier gratis, así que no está incluido acá. Si en algún momento lo contratás, agregar
  ese llamado en `fetch_finnhub.py` es directo — avisame y lo sumamos.
- El tier gratis de Finnhub tiene rate limit de 60 llamadas/minuto — `fetch_earnings_in_chunks`
  ya respeta eso con un `sleep` entre llamadas.
