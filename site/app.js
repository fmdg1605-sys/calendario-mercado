// ============================================================
// Estado
// ============================================================
let DATA = { earnings: [], news: [], generated_at: null };
let state = { region: "all", rangeDays: 7, query: "" };

const REGION_LABEL = { us: "US", europe: "EUROPA", china_adr: "CHINA ADR" };
const REGION_DOT_CLASS = { us: "dot--us", europe: "dot--eu", china_adr: "dot--cn" };
const HOUR_LABEL = { bmo: "ANTES APERTURA", amc: "DESPUÉS CIERRE", dmh: "DURANTE RUEDA" };

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
  } catch (err) {
    console.warn("No se pudo cargar data.json todavía. Corré scripts/build_data.py.", err);
    DATA = { earnings: [], news: [], generated_at: null };
  }
  render();
}

// ============================================================
// Reloj (hora Buenos Aires) + timestamp de actualización
// ============================================================
function tickClock() {
  const now = new Date();
  const fmt = new Intl.DateTimeFormat("es-AR", {
    timeZone: "America/Argentina/Buenos_Aires",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
  });
  document.getElementById("clock").textContent = fmt.format(now);
}

function renderUpdated() {
  const el = document.getElementById("updated");
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
  const today = new Date().toISOString().slice(0, 10);

  const upcoming = DATA.earnings
    .filter(e => e.date >= today)
    .slice(0, 20)
    .map(e => `${e.ticker} · ${e.date} ${HOUR_LABEL[e.hour] || ""}`.trim());

  const headlines = DATA.news.slice(0, 10).map(n => n.headline);

  const items = [...upcoming, ...headlines];
  if (items.length === 0) {
    tapeEl.innerHTML = `<span>ESPERANDO DATOS — CORRÉ scripts/build_data.py PARA GENERAR data.json</span>`;
    return;
  }

  // Duplicamos la secuencia para que el loop de scroll sea continuo sin salto visible.
  const sequence = items.map(t => `<span>${escapeHtml(t)}</span><span class="sep">//</span>`).join("");
  tapeEl.innerHTML = sequence + sequence;
}

// ============================================================
// Filtros
// ============================================================
function setupFilters() {
  document.querySelectorAll("[data-region]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-region]").forEach(b => b.classList.remove("chip--active"));
      btn.classList.add("chip--active");
      state.region = btn.dataset.region;
      render();
    });
  });

  document.querySelectorAll("[data-range]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-range]").forEach(b => b.classList.remove("chip--active"));
      btn.classList.add("chip--active");
      state.rangeDays = parseInt(btn.dataset.range, 10);
      render();
    });
  });

  document.getElementById("searchInput").addEventListener("input", (e) => {
    state.query = e.target.value.trim().toLowerCase();
    render();
  });
}

function filteredEarnings() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const limit = new Date(today);
  limit.setDate(limit.getDate() + state.rangeDays);

  return DATA.earnings.filter(e => {
    if (!e.date) return false;
    const d = new Date(e.date + "T00:00:00");
    if (d < today || d > limit) return false;
    if (state.region !== "all" && e.region !== state.region) return false;
    if (state.query) {
      const hay = `${e.ticker} ${e.company}`.toLowerCase();
      if (!hay.includes(state.query)) return false;
    }
    return true;
  });
}

// ============================================================
// Render agenda (agrupado por día)
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
  agendaEl.querySelectorAll(".day-group").forEach(el => el.remove());

  const events = filteredEarnings();
  if (events.length === 0) {
    emptyEl.hidden = false;
    return;
  }
  emptyEl.hidden = true;

  const byDate = {};
  for (const e of events) {
    (byDate[e.date] ??= []).push(e);
  }

  const tpl = document.getElementById("eventCardTpl");

  Object.keys(byDate).sort().forEach(date => {
    const group = document.createElement("div");
    group.className = "day-group";

    const { label, isToday } = formatDayHeader(date);
    const header = document.createElement("div");
    header.className = "day-group__header";
    header.innerHTML = `
      <span class="day-group__date ${isToday ? "day-group__today" : ""}">${label}</span>
      <span class="day-group__count">${byDate[date].length} evento${byDate[date].length === 1 ? "" : "s"}</span>
    `;
    group.appendChild(header);

    byDate[date].forEach(e => {
      const node = tpl.content.cloneNode(true);
      node.querySelector(".event__region").classList.add(REGION_DOT_CLASS[e.region] || "dot--us");
      node.querySelector(".event__ticker").textContent = e.ticker;
      node.querySelector(".event__company").textContent = `${e.company} · ${REGION_LABEL[e.region] || ""}`;
      node.querySelector(".event__hour").textContent = HOUR_LABEL[e.hour] || "—";
      const epsText = (e.eps_estimate !== null && e.eps_estimate !== undefined)
        ? `EPS est. ${e.eps_estimate}`
        : "";
      node.querySelector(".event__eps").textContent = epsText;
      group.appendChild(node);
    });

    agendaEl.appendChild(group);
  });
}

// ============================================================
// Render noticias
// ============================================================
function renderNews() {
  const listEl = document.getElementById("newsList");
  listEl.innerHTML = "";
  const tpl = document.getElementById("newsCardTpl");
  const news = DATA.news.slice(0, 40);

  document.getElementById("newsCount").textContent = news.length ? `${news.length}` : "";

  if (news.length === 0) {
    listEl.innerHTML = `<p style="color: var(--text-faint); font-family: var(--font-mono); font-size: 0.75rem;">Sin noticias todavía.</p>`;
    return;
  }

  news.forEach(n => {
    const node = tpl.content.cloneNode(true);
    const a = node.querySelector(".newsitem");
    a.href = n.url || "#";
    node.querySelector(".newsitem__source").textContent = n.source || "FUENTE";
    node.querySelector(".newsitem__headline").textContent = n.headline || "";
    node.querySelector(".newsitem__time").textContent = n.datetime ? timeAgo(n.datetime) : "";
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
  return str.replace(/[&<>"']/g, m => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[m]));
}

// ============================================================
// Init
// ============================================================
function render() {
  renderAgenda();
  renderNews();
}

document.addEventListener("DOMContentLoaded", () => {
  setupFilters();
  tickClock();
  setInterval(tickClock, 1000);
  loadData().then(() => {
    renderTape();
    renderUpdated();
  });
});
