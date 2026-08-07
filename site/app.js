// ============================================================
// Estado y Helper de Normalización
// ============================================================
let DATA = { earnings: [], macro: [], company_details: {}, news: [], generated_at: null };
let state = { region: "all", rangeDays: 9999, query: "", macroOn: true };

function normalizeRegion(r) {
  if (!r) return "us";
  const s = String(r).toLowerCase().trim();
  if (s === "europe" || s === "europa" || s === "eu") return "europe";
  if (s === "us" || s === "eeuu" || s === "usa") return "us";
  if (s === "china_adr" || s === "china" || s === "cn" || s === "china adr") return "china_adr";
  if (s === "all" || s === "todo") return "all";
  return s;
}

const REGION_LABEL = { us: "US", europe: "EUROPA", europa: "EUROPA", china_adr: "CHINA ADR" };
const REGION_DOT_CLASS = { us: "dot--us", europe: "dot--eu", europa: "dot--eu", china_adr: "dot--cn" };
const HOUR_LABEL = { bmo: "ANTES APERTURA", amc: "DESPUÉS CIERRE", dmh: "DURANTE RUEDA" };
const HOUR_BADGE_CLASS = { bmo: "badge--bmo", amc: "badge--amc", dmh: "badge--dmh" };

const DAY_NAMES = ["DOM", "LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"];
const MONTH_NAMES = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"];

// ============================================================
// Carga de datos
// ============================================================
async function loadData() {
  try {
    const res = await fetch("data.json", { cache: "no-store" });
    if (!res.ok) throw new Error("no data.json");
    DATA = await res.json();
    DATA.macro = DATA.macro || [];
    DATA.company_details = DATA.company_details || {};
  } catch (err) {
    console.warn("No se pudo cargar data.json.", err);
    DATA = { earnings: [], macro: [], company_details: {}, news: [], generated_at: null };
  }
  render();
}

// ============================================================
// Reloj + timestamp
// ============================================================
function tickClock() {
  const now = new Date();
  const fmt = new Intl.DateTimeFormat("es-AR", {
    timeZone: "America/Argentina/Buenos_Aires",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
  });
  const el = document.getElementById("clock");
  if (el) el.textContent = fmt.format(now);
}

function renderUpdated() {
  const el = document.getElementById("updated");
  if (!el) return;
  if (!DATA.generated_at) { el.textContent = "sin datos aún — corré build_data.py"; return; }
  const d = new Date(DATA.generated_at);
  const fmt = new Intl.DateTimeFormat("es-AR", {
    timeZone: "America/Argentina/Buenos_Aires",
    day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
  });
  el.textContent = `actualizado ${fmt.format(d)}`;
}

// ============================================================
// Ticker tape
// ============================================================
function renderTape() {
  const tapeEl = document.getElementById("tape");
  if (!tapeEl) return;
  const today = new Date().toISOString().slice(0, 10);

  const upcomingEarnings = DATA.earnings
    .filter(e => e.date >= today)
    .slice(0, 16)
    .map(e => ({
      text: `${e.ticker} · ${e.date} ${HOUR_LABEL[e.hour] || ""}`.trim(),
      type: "earnings",
      ticker: e.ticker,
    }));

  const upcomingMacro = DATA.macro
    .filter(m => m.date >= today)
    .slice(0, 8)
    .map(m => ({ text: `MACRO · ${m.date} · ${m.title}`, type: "macro" }));

  const headlines = DATA.news.slice(0, 10)
    .filter(n => n.url)
    .map(n => ({ text: n.headline, type: "news", url: n.url }));

  const items = [...upcomingEarnings, ...upcomingMacro, ...headlines];
  if (items.length === 0) {
    tapeEl.innerHTML = `<span>ESPERANDO DATOS — CORRÉ scripts/build_data.py PARA GENERAR data.json</span>`;
    return;
  }

  const sequence = items.map(item => {
    const cls = item.type === "macro" ? "tape-item tape-item--macro" : "tape-item";
    let attrs = "";
    if (item.type === "earnings" && item.ticker) attrs = ` data-ticker="${escapeHtml(item.ticker)}"`;
    if (item.type === "news" && item.url) attrs = ` data-url="${escapeHtml(item.url)}"`;
    return `<span class="${cls}"${attrs}>${escapeHtml(item.text)}</span><span class="sep">//</span>`;
  }).join("");
  tapeEl.innerHTML = sequence + sequence;

  const totalChars = items.reduce((acc, i) => acc + i.text.length + 3, 0);
  const CHARS_PER_SECOND = 18;
  const duration = Math.max(60, Math.round(totalChars / CHARS_PER_SECOND));
  tapeEl.style.setProperty("--tape-duration", `${duration}s`);

  tapeEl.querySelectorAll(".tape-item[data-ticker]").forEach(el => {
    el.addEventListener("click", () => openModal(el.dataset.ticker));
  });
  tapeEl.querySelectorAll(".tape-item[data-url]").forEach(el => {
    el.addEventListener("click", () => window.open(el.dataset.url, "_blank", "noopener"));
  });
}

// ============================================================
// Filtros
// ============================================================
function setupFilters() {
  document.querySelectorAll("[data-region]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-region]").forEach(b => b.classList.remove("chip--active"));
      btn.classList.add("chip--active");
      state.region = normalizeRegion(btn.dataset.region);
      render();
    });
  });

  document.querySelectorAll("[data-range]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-range]").forEach(b => b.classList.remove("chip--active"));
      btn.classList.add("chip--active");
      const raw = String(btn.dataset.range || "").toLowerCase();
      
      if (raw === "all" || raw === "todo" || raw === "9999" || raw === "365") {
        state.rangeDays = 9999;
      } else {
        const parsed = parseInt(raw, 10);
        state.rangeDays = Number.isNaN(parsed) ? 9999 : parsed;
      }
      render();
    });
  });

  const macroBtn = document.getElementById("macroToggle");
  if (macroBtn) {
    macroBtn.addEventListener("click", (e) => {
      state.macroOn = !state.macroOn;
      e.currentTarget.classList.toggle("chip--active", state.macroOn);
      e.currentTarget.dataset.macro = state.macroOn ? "on" : "off";
      render();
    });
  }

  const searchInp = document.getElementById("searchInput");
  if (searchInp) {
    searchInp.addEventListener("input", (e) => {
      state.query = e.target.value.trim().toLowerCase();
      render();
    });
  }
}

function dateRangeBounds() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const limit = new Date(today);
  
  const days = Number(state.rangeDays);
  if (Number.isNaN(days) || days >= 365) {
    limit.setFullYear(limit.getFullYear() + 10);
  } else {
    limit.setDate(limit.getDate() + days);
  }
  return { today, limit };
}

function filteredEarnings() {
  const { today, limit } = dateRangeBounds();
  const selectedRegion = normalizeRegion(state.region);

  return DATA.earnings.filter(e => {
    if (!e.date) return false;
    const d = new Date(e.date + "T00:00:00");
    if (d < today || d > limit) return false;
    
    if (selectedRegion !== "all") {
      const eRegion = normalizeRegion(e.region);
      if (eRegion !== selectedRegion) return false;
    }

    if (state.query) {
      const hay = `${e.ticker} ${e.company}`.toLowerCase();
      if (!hay.includes(state.query)) return false;
    }
    return true;
  });
}

function filteredMacro() {
  if (!state.macroOn) return [];
  const selectedRegion = normalizeRegion(state.region);

  if (selectedRegion === "china_adr") return [];
  if (state.query) return [];

  const { today, limit } = dateRangeBounds();
  return DATA.macro.filter(m => {
    if (!m.date) return false;
    
    if (selectedRegion !== "all") {
      const mRegion = normalizeRegion(m.region || "us");
      if (mRegion !== selectedRegion) return false;
    }

    const d = new Date(m.date + "T00:00:00");
    return d >= today && d <= limit;
  });
}

// ============================================================
// Render agenda (a prueba de fallos de plantilla)
// ============================================================
function formatDayHeader(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  const today = new Date(); today.setHours(0,0,0,0);
  const isToday = d.getTime() === today.getTime();
  const label = `${DAY_NAMES[d.getDay()]} ${d.getDate()} ${MONTH_NAMES[d.getMonth()]}`;
  return { label: isToday ? `${label} · HOY` : label, isToday };
}

function renderAgenda() {
  const agendaEl = document.getElementById("agenda");
  const emptyEl = document.getElementById("agendaEmpty");
  if (!agendaEl || !emptyEl) return;
  agendaEl.querySelectorAll(".day-group").forEach(el => el.remove());

  const earnings = filteredEarnings();
  const macro = filteredMacro();

  if (earnings.length === 0 && macro.length === 0) {
    emptyEl.hidden = false;
    return;
  }
  emptyEl.hidden = true;

  const byDate = {};
  for (const e of earnings) {
    (byDate[e.date] ??= { earnings: [], macro: [] }).earnings.push(e);
  }
  for (const m of macro) {
    (byDate[m.date] ??= { earnings: [], macro: [] }).macro.push(m);
  }

  const eventTpl = document.getElementById("eventCardTpl");
  const macroTpl = document.getElementById("macroCardTpl");

  Object.keys(byDate).sort().forEach(date => {
    const group = document.createElement("div");
    group.className = "day-group";

    const dayItems = byDate[date];
    const count = dayItems.earnings.length + dayItems.macro.length;
    const { label, isToday } = formatDayHeader(date);
    const header = document.createElement("div");
    header.className = "day-group__header";
    header.innerHTML = `
      <span class="day-group__date ${isToday ? "day-group__today" : ""}">${label}</span>
      <span class="day-group__count">${count} evento${count === 1 ? "" : "s"}</span>
    `;
    group.appendChild(header);

    // Eventos macro a prueba de errores de clases CSS
    dayItems.macro.forEach(m => {
      if (!macroTpl) return;
      const node = macroTpl.content.cloneNode(true);
      
      const tickerEl = node.querySelector(".event__ticker--macro") || node.querySelector(".event__ticker") || node.querySelector(".badge");
      if (tickerEl) tickerEl.textContent = m.type;
      
      const compEl = node.querySelector(".event__company");
      if (compEl) compEl.textContent = `${m.title}${m.confirmed ? "" : " (fecha proyectada)"}`;
      
      const hourEl = node.querySelector(".event__hour");
      if (hourEl) hourEl.textContent = m.label || "";
      
      group.appendChild(node);
    });

    // Earnings
    dayItems.earnings.forEach(e => {
      if (!eventTpl) return;
      const node = eventTpl.content.cloneNode(true);
      const article = node.querySelector(".event");
      if (article) article.dataset.ticker = e.ticker;
      
      const normReg = normalizeRegion(e.region);
      const regDot = node.querySelector(".event__region");
      if (regDot) regDot.classList.add(REGION_DOT_CLASS[normReg] || "dot--us");
      
      const tickEl = node.querySelector(".event__ticker");
      if (tickEl) tickEl.textContent = e.ticker;
      
      const compEl = node.querySelector(".event__company");
      if (compEl) compEl.textContent = `${e.company} · ${REGION_LABEL[normReg] || normReg.toUpperCase()}`;
      
      const hourClass = HOUR_BADGE_CLASS[e.hour] || "badge--dmh";
      const hourEl = node.querySelector(".event__hour");
      if (hourEl) {
        hourEl.innerHTML = e.hour
          ? `<span class="badge ${hourClass}">${HOUR_LABEL[e.hour] || e.hour}</span>`
          : "";
      }
      
      const epsText = (e.eps_estimate !== null && e.eps_estimate !== undefined)
        ? `EPS est. ${e.eps_estimate}`
        : "";
      const epsEl = node.querySelector(".event__eps");
      if (epsEl) epsEl.textContent = epsText;
      
      group.appendChild(node);
    });

    agendaEl.appendChild(group);
  });

  agendaEl.querySelectorAll(".event[data-ticker]").forEach(el => {
    el.addEventListener("click", () => openModal(el.dataset.ticker));
    el.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); openModal(el.dataset.ticker); }
    });
  });
}

// ============================================================
// Render noticias
// ============================================================
function renderNews() {
  const listEl = document.getElementById("newsList");
  if (!listEl) return;
  listEl.innerHTML = "";
  const tpl = document.getElementById("newsCardTpl");
  const news = DATA.news.slice(0, 40);

  const countEl = document.getElementById("newsCount");
  if (countEl) countEl.textContent = news.length ? `${news.length}` : "";

  if (news.length === 0) {
    listEl.innerHTML = `<p style="color: var(--text-faint); font-family: var(--font-sans); font-size: 0.8rem;">Sin noticias todavía.</p>`;
    return;
  }

  news.forEach(n => {
    if (!tpl) return;
    const node = tpl.content.cloneNode(true);
    const a = node.querySelector(".newsitem");
    if (a) a.href = n.url || "#";
    const srcEl = node.querySelector(".newsitem__source");
    if (srcEl) srcEl.textContent = n.source || "FUENTE";
    const headEl = node.querySelector(".newsitem__headline");
    if (headEl) headEl.textContent = n.headline || "";
    const timeEl = node.querySelector(".newsitem__time");
    if (timeEl) timeEl.textContent = n.datetime ? timeAgo(n.datetime) : "";
    listEl.appendChild(node);
  });
}

function timeAgo(unixTs) {
  const diffMin = Math.floor((Date.now() / 1000 - unixTs) / 60);
  if (diffMin < 60) return `hace ${diffMin}m`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `hace ${diffH}h`;
  return `hace ${Math.floor(diffH / 24)}d`;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, m => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[m]));
}

// ============================================================
// Toast, Modal, Theme, Init
// ============================================================
function showToast(message) {
  const toastEl = document.getElementById("toast");
  if (!toastEl) return;
  document.getElementById("toastMessage").textContent = message;
  toastEl.classList.add("is-visible");
  setTimeout(() => toastEl.classList.remove("is-visible"), 2600);
}

function fmtMoney(n, currency = "USD") {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("es-AR", { style: "currency", currency, maximumFractionDigits: 2 }).format(n);
}

function fmtMarketCap(musd) {
  if (musd === null || musd === undefined || Number.isNaN(musd)) return "—";
  if (musd >= 1_000_000) return `US$ ${(musd / 1_000_000).toFixed(2)}T`;
  if (musd >= 1_000) return `US$ ${(musd / 1_000).toFixed(2)}B`;
  return `US$ ${musd.toFixed(0)}M`;
}

function fmtNum(n, decimals = 2) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toFixed(decimals);
}

function fmtPct(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return `${n.toFixed(2)}%`;
}

function findNextEarnings(ticker) {
  const today = new Date().toISOString().slice(0, 10);
  return DATA.earnings
    .filter(e => e.ticker === ticker && e.date >= today)
    .sort((a, b) => (a.date > b.date ? 1 : -1))[0];
}

function openModal(ticker) {
  if (!ticker) return;
  const details = DATA.company_details[ticker];
  const earningsEntry = DATA.earnings.find(e => e.ticker === ticker);
  const nextEarnings = findNextEarnings(ticker);
  const companyName = details?.full_name || earningsEntry?.company || ticker;
  const region = normalizeRegion(earningsEntry?.region);
  const yahooUrl = `https://finance.yahoo.com/quote/${encodeURIComponent(ticker)}`;
  const tradingViewUrl = `https://www.tradingview.com/symbols/${encodeURIComponent(ticker)}/`;

  const tickEl = document.getElementById("modalTicker");
  const nameEl = document.getElementById("modalName");
  if (tickEl) tickEl.textContent = ticker;
  if (nameEl) nameEl.textContent = companyName;

  const modalEl = document.getElementById("companyModal");
  if (!modalEl) return;

  if (!details) {
    const priceEl = modalEl.querySelector(".modal__price");
    if (priceEl) priceEl.innerHTML = "";
    const tagsEl = document.getElementById("modalTags");
    if (tagsEl) {
      tagsEl.innerHTML = region
        ? `<span class="tag">${escapeHtml(REGION_LABEL[region] || region.toUpperCase())}</span>`
        : "";
    }
    const gridEl = document.getElementById("modalGrid");
    if (gridEl) {
      gridEl.outerHTML = `
        <div class="modal__research" id="modalGrid">
          <div class="modal__research-icon">🔎</div>
          <div class="modal__research-title">Todavía no tenemos la ficha financiera de ${escapeHtml(ticker)}</div>
          <div class="modal__research-desc">
            Traemos precio, market cap y múltiplos para los próximos earnings dentro del límite gratuito de la API.
            Mientras tanto, investigalo directo en estas fuentes:
          </div>
          <div class="modal__research-links">
            <a class="is-primary" href="${yahooUrl}" target="_blank" rel="noopener">Yahoo Finance ↗</a>
            <a class="is-secondary" href="${tradingViewUrl}" target="_blank" rel="noopener">TradingView ↗</a>
          </div>
        </div>
      `;
    }
    const earningsEl = document.getElementById("modalEarnings");
    if (earningsEl) {
      if (nextEarnings) {
        earningsEl.innerHTML = `
          Próximo reporte: <strong>${nextEarnings.date}</strong> · ${HOUR_LABEL[nextEarnings.hour] || "hora sin confirmar"}
          ${nextEarnings.eps_estimate != null ? ` · EPS estimado ${nextEarnings.eps_estimate}` : ""}
        `;
      } else {
        earningsEl.innerHTML = "";
      }
    }
    const linksEl = document.getElementById("modalLinks");
    if (linksEl) linksEl.innerHTML = "";

    modalEl.hidden = false;
    document.body.style.overflow = "hidden";
    return;
  }

  const currentGrid = document.getElementById("modalGrid");
  if (currentGrid && !currentGrid.classList.contains("modal__grid")) {
    currentGrid.outerHTML = `<div class="modal__grid" id="modalGrid"></div>`;
  }

  const priceEl = document.getElementById("modalPrice");
  if (priceEl) {
    if (details.price !== null && details.price !== undefined) {
      const up = (details.change ?? 0) >= 0;
      const arrow = up ? "▲" : "▼";
      priceEl.innerHTML = `
        ${fmtMoney(details.price, details.currency || "USD")}
        <small class="modal__change--${up ? "up" : "down"}">${arrow} ${fmtNum(details.change, 2)} (${fmtPct(details.change_pct)})</small>
      `;
    } else {
      priceEl.innerHTML = `<small>cotización no disponible</small>`;
    }
  }

  const tags = [];
  if (details.industry) tags.push(details.industry);
  if (details.country) tags.push(details.country);
  if (details.exchange) tags.push(details.exchange);
  if (region) tags.push(REGION_LABEL[region] || region.toUpperCase());
  const tagsEl = document.getElementById("modalTags");
  if (tagsEl) {
    tagsEl.innerHTML = tags.length
      ? tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("")
      : "";
  }

  const metrics = [
    ["Market Cap", fmtMarketCap(details.market_cap_musd)],
    ["P/E (TTM)", fmtNum(details.pe_ttm)],
    ["EPS (TTM)", fmtNum(details.eps_ttm)],
    ["P/B", fmtNum(details.pb)],
    ["Máx. 52 sem.", details.week52_high != null ? fmtMoney(details.week52_high, details.currency || "USD") : "—"],
    ["Mín. 52 sem.", details.week52_low != null ? fmtMoney(details.week52_low, details.currency || "USD") : "—"],
    ["Dividend Yield", fmtPct(details.dividend_yield)],
    ["Beta", fmtNum(details.beta)],
  ];
  const gridEl = document.getElementById("modalGrid");
  if (gridEl) {
    gridEl.innerHTML = metrics.map(([label, value]) => `
      <div class="modal__metric">
        <span class="modal__metric-label">${label}</span>
        <span class="modal__metric-value">${value}</span>
      </div>
    `).join("");
  }

  const earningsEl = document.getElementById("modalEarnings");
  if (earningsEl) {
    if (nextEarnings) {
      earningsEl.innerHTML = `
        Próximo reporte: <strong>${nextEarnings.date}</strong> · ${HOUR_LABEL[nextEarnings.hour] || "hora sin confirmar"}
        ${nextEarnings.eps_estimate != null ? ` · EPS estimado ${nextEarnings.eps_estimate}` : ""}
      `;
    } else {
      earningsEl.innerHTML = "";
    }
  }

  const links = [{ label: "Yahoo Finance", url: yahooUrl }];
  if (details.web_url) links.push({ label: "Sitio oficial", url: details.web_url });
  links.push({ label: "TradingView", url: tradingViewUrl });
  const linksEl = document.getElementById("modalLinks");
  if (linksEl) {
    linksEl.innerHTML = links
      .map(l => `<a href="${l.url}" target="_blank" rel="noopener">${escapeHtml(l.label)} ↗</a>`)
      .join("");
  }

  modalEl.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeModal() {
  const modalEl = document.getElementById("companyModal");
  if (modalEl) modalEl.hidden = true;
  document.body.style.overflow = "";
}

function setupModal() {
  const closeBtn = document.getElementById("modalClose");
  const modalEl = document.getElementById("companyModal");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (modalEl) {
    modalEl.addEventListener("click", (e) => {
      if (e.target.id === "companyModal") closeModal();
    });
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

function setupThemeToggle() {
  const btn = document.getElementById("themeToggle");
  const icon = document.getElementById("themeToggleIcon");
  if (!btn || !icon) return;
  const applyIcon = (theme) => { icon.textContent = theme === "dark" ? "🌙" : "☀️"; };

  applyIcon(document.documentElement.getAttribute("data-theme") || "dark");

  btn.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("calendario-theme", next); } catch (err) {}
    applyIcon(next);
  });
}

function setupNewsRefresh() {
  const btn = document.getElementById("newsRefresh");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    if (btn.classList.contains("is-loading")) return;
    btn.classList.add("is-loading");
    const minSpin = new Promise(r => setTimeout(r, 550));
    try {
      const [res] = await Promise.all([
        fetch(`/api/news?t=${Date.now()}`, { cache: "no-store" }),
        minSpin,
      ]);
      const payload = await res.json();
      if (!res.ok) throw new Error(payload?.error || "no se pudo traer noticias en vivo");
      DATA.news = Array.isArray(payload.news) ? payload.news : [];
      renderNews();
      renderTape();
      showToast("Noticias actualizadas");
    } catch (err) {
      console.warn("No se pudieron refrescar las noticias en vivo.", err);
      await minSpin;
      showToast("No se pudo actualizar.");
    } finally {
      btn.classList.remove("is-loading");
    }
  });
}

function render() {
  renderAgenda();
  renderNews();
}

document.addEventListener("DOMContentLoaded", () => {
  setupFilters();
  setupModal();
  setupThemeToggle();
  setupNewsRefresh();
  tickClock();
  setInterval(tickClock, 1000);
  loadData().then(() => {
    renderTape();
    renderUpdated();
  });
});