import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import io
import os
from init_db import init_db, get_connection

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Autoinspección Locatel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* ── Layout ── */
.main { background: #f0f4f8; }
.block-container { padding: 1rem 2rem 3rem; max-width: 1440px; margin-top: 56px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* ══════════════════════════════════════
   SIDEBAR → styled as hamburger drawer
══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid #1a2744 !important;
    top: 56px !important;
    height: calc(100vh - 56px) !important;
    position: fixed !important;
    z-index: 9990 !important;
    transition: transform .28s cubic-bezier(.4,0,.2,1),
                margin-left .28s cubic-bezier(.4,0,.2,1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,.45) !important;
    overflow-y: auto !important;
    width: 18rem !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
    width: 18rem !important;
}
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
/* Push main content right when sidebar open */
[data-testid="stMain"] { transition: margin-left .28s cubic-bezier(.4,0,.2,1) !important; }

/* Nav buttons inside sidebar */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #7a95b4 !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    margin-bottom: 3px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(56,139,253,0.1) !important;
    border-color: rgba(56,139,253,0.25) !important;
    color: #93c5fd !important;
    transform: translateX(2px) !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important; outline: none !important;
}
div.nav-active [data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] div.nav-active .stButton > button {
    background: rgba(37,99,235,0.22) !important;
    border-color: rgba(59,130,246,0.55) !important;
    color: #60a5fa !important;
    font-weight: 700 !important;
}

/* Selectbox in sidebar */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #0d1829 !important;
    border-color: #1a2744 !important;
    color: #c8d6e5 !important;
    border-radius: 9px !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #2d4a6b !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stSelectbox svg { color: #3b5270 !important; }

/* Sidebar section labels */
.sdiv-lbl {
    font-size: .62rem; font-weight: 700; color: #2d4a6b;
    text-transform: uppercase; letter-spacing: .1em;
    padding: .75rem 1rem .3rem;
}
.sdiv { border: none; border-top: 1px solid #1a2744; margin: .6rem .5rem; }

/* ══════════════════════════════════════
   TOPBAR (fixed)
══════════════════════════════════════ */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: #0a0f1e;
    border-bottom: 1px solid #1a2744;
    height: 56px;
    display: flex; align-items: center;
    padding: 0 1.25rem; gap: .9rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.3);
}
.tb-logo { font-size: 1rem; font-weight: 800; color: #f0f6ff; letter-spacing: -.02em; }
.tb-sub  { font-size: .6rem; color: #2d4a6b; text-transform: uppercase; letter-spacing: .1em; font-weight: 600; }
.tb-space { flex: 1; }
.tb-chip {
    background: rgba(255,255,255,.05); border: 1px solid #1a2744;
    border-radius: 100px; padding: .3rem .85rem;
    font-size: .75rem; color: #4b7094; white-space: nowrap;
}
.tb-page { color: #60a5fa !important; font-weight: 600; }

/* Hamburger button */
.ham {
    width: 38px; height: 38px;
    background: rgba(255,255,255,.04);
    border: 1px solid #1a2744;
    border-radius: 9px; cursor: pointer;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 5px;
    transition: border-color .2s, background .2s; flex-shrink: 0;
}
.ham:hover { border-color: #3b82f6; background: rgba(59,130,246,.08); }
.ham span {
    display: block; width: 18px; height: 1.5px;
    background: #7a95b4; border-radius: 2px;
    transition: all .25s cubic-bezier(.4,0,.2,1);
    transform-origin: center;
}
/* open state set via JS */
.ham.is-open span:nth-child(1) { transform: translateY(6.5px) rotate(45deg); background: #60a5fa; width: 20px; }
.ham.is-open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
.ham.is-open span:nth-child(3) { transform: translateY(-6.5px) rotate(-45deg); background: #60a5fa; width: 20px; }

/* ══════════════════════════════════════
   PAGE CONTENT CARDS, KPIs, etc.
══════════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, #0d1b2e 0%, #0f2847 40%, #0e3a6e 100%);
    border-radius: 14px; padding: 1.75rem 2rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 32px rgba(10,25,60,.3), inset 0 1px 0 rgba(255,255,255,.05);
    border: 1px solid rgba(56,139,253,.15); position: relative; overflow: hidden;
}
.page-header::before {
    content:''; position:absolute; top:-40%; right:-5%;
    width:300px; height:300px;
    background:radial-gradient(circle,rgba(56,139,253,.12) 0%,transparent 70%);
    pointer-events:none;
}
.ph-title { color:#f0f6ff; font-size:1.6rem; font-weight:800; letter-spacing:-.02em; }
.ph-sub   { color:#6b8fba; font-size:.85rem; margin-top:4px; }
.ph-badges { display:flex; gap:.6rem; flex-wrap:wrap; align-items:center; }
.ph-badge {
    padding:.35rem .9rem; border-radius:100px; font-size:.78rem; font-weight:600;
    border:1px solid rgba(255,255,255,.12); color:#c8d6e5; background:rgba(255,255,255,.06);
}
.ph-badge.favorable   { background:rgba(16,185,129,.15); border-color:rgba(16,185,129,.35); color:#34d399; }
.ph-badge.desfavorable{ background:rgba(239,68,68,.15);  border-color:rgba(239,68,68,.35);  color:#f87171; }

.kpi {
    background:white; border-radius:14px; padding:1.25rem 1.5rem;
    border:1px solid #e8eef5; box-shadow:0 2px 8px rgba(0,0,0,.04);
    position:relative; overflow:hidden;
}
.kpi::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:14px 14px 0 0; }
.kpi.blue::after  { background:linear-gradient(90deg,#1a56db,#60a5fa); }
.kpi.green::after { background:linear-gradient(90deg,#059669,#34d399); }
.kpi.red::after   { background:linear-gradient(90deg,#dc2626,#f87171); }
.kpi.amber::after { background:linear-gradient(90deg,#b45309,#fbbf24); }
.kpi.purple::after{ background:linear-gradient(90deg,#7c3aed,#a78bfa); }
.kpi-lbl { font-size:.7rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.07em; margin-bottom:.5rem; }
.kpi-val { font-size:1.75rem; font-weight:800; color:#0f172a; line-height:1.1; letter-spacing:-.01em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.kpi-sub { font-size:.76rem; color:#94a3b8; margin-top:4px; }
.kpi-val.val-green  { color:#059669; }
.kpi-val.val-amber  { color:#b45309; }
.kpi-val.val-red    { color:#dc2626; }
.kpi-val.val-blue   { color:#1a56db; }
.kpi-val.val-purple { color:#7c3aed; }

.card { background:white; border-radius:14px; padding:1.5rem; border:1px solid #e8eef5; box-shadow:0 2px 8px rgba(0,0,0,.04); margin-bottom:1.25rem; }
.card-hd { font-size:.78rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.07em; margin-bottom:1rem; padding-bottom:.75rem; border-bottom:1px solid #f1f5f9; display:flex; align-items:center; justify-content:space-between; }

.audit-item-row { display:grid; grid-template-columns:1fr 140px 1fr; gap:.75rem; align-items:start; padding:.75rem 1rem; border-radius:10px; border:1px solid #f1f5f9; margin-bottom:.5rem; background:#fafbfc; transition:border-color .15s,box-shadow .15s; }
.audit-item-row:hover { border-color:#c7d7f0; box-shadow:0 2px 8px rgba(26,86,219,.06); }
.audit-item-row.fail { border-color:#fecdd3; background:#fff8f8; }
.audit-item-row.pass { border-color:#bbf7d0; background:#f8fff9; }
.item-name { font-size:.82rem; font-weight:500; color:#334155; line-height:1.4; }

.badge { display:inline-flex; align-items:center; gap:.25rem; padding:.22rem .65rem; border-radius:100px; font-size:.71rem; font-weight:700; letter-spacing:.02em; }
.b-ok    { background:#dcfce7; color:#15803d; }
.b-fail  { background:#fee2e2; color:#b91c1c; }
.b-warn  { background:#fef3c7; color:#92400e; }
.b-info  { background:#dbeafe; color:#1d4ed8; }
.b-gray  { background:#f1f5f9; color:#475569; }
.b-fav   { background:#d1fae5; color:#065f46; }
.b-desfav{ background:#fee2e2; color:#991b1b; }
.b-cond  { background:#fef3c7; color:#78350f; }

.pb-wrap { background:#f1f5f9; border-radius:100px; height:7px; overflow:hidden; }
.pb-fill { height:100%; border-radius:100px; transition:width .4s ease; }

.stExpander { border:1px solid #e2e8f0 !important; border-radius:12px !important; overflow:hidden !important; margin-bottom:.75rem !important; }

div[data-testid="stForm"] { background:white; border:1px solid #e2e8f0; border-radius:14px; padding:1.75rem; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
    border-radius:9px !important; border-color:#d1dde8 !important; font-size:.875rem !important; background:#f8fafc !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color:#3b82f6 !important; box-shadow:0 0 0 3px rgba(59,130,246,.12) !important; background:white !important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,.stDateInput label {
    font-size:.75rem !important; font-weight:600 !important; color:#64748b !important;
    text-transform:uppercase; letter-spacing:.05em !important;
}

.stButton>button { border-radius:9px !important; font-weight:600 !important; font-size:.875rem !important; transition:all .15s !important; }
.stButton>button[kind="primary"] { background:linear-gradient(135deg,#1d4ed8,#2563eb) !important; border:none !important; box-shadow:0 2px 8px rgba(37,99,235,.3) !important; }
.stButton>button[kind="primary"]:hover { transform:translateY(-1px) !important; box-shadow:0 4px 16px rgba(37,99,235,.4) !important; }

.stDownloadButton>button { border-radius:9px !important; font-weight:600 !important; font-size:.82rem !important; background:white !important; border:1.5px solid #e2e8f0 !important; color:#475569 !important; }
.stDownloadButton>button:hover { border-color:#3b82f6 !important; color:#1d4ed8 !important; background:#eff6ff !important; }

div[data-testid="stRadio"]>label { display:none !important; }
div[data-testid="stRadio"]>div { display:flex; flex-direction:row; gap:.4rem; background:#f1f5f9; border-radius:8px; padding:3px; }
div[data-testid="stRadio"]>div>label { flex:1; text-align:center !important; padding:.35rem .6rem !important; border-radius:6px !important; font-size:.8rem !important; font-weight:600 !important; cursor:pointer !important; border:1px solid transparent !important; margin:0 !important; }
div[data-testid="stRadio"]>div>label[aria-checked="true"] { background:white !important; box-shadow:0 1px 4px rgba(0,0,0,.1) !important; }

.stTabs [data-baseweb="tab-list"] { background:#f1f5f9; border-radius:10px; padding:3px; gap:0; border:none; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:.45rem 1.2rem; font-weight:500; font-size:.85rem; color:#64748b; background:transparent; border:none; }
.stTabs [aria-selected="true"] { background:white !important; color:#1d4ed8 !important; box-shadow:0 1px 4px rgba(0,0,0,.1); }

.info-banner { background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:1rem 1.25rem; color:#1e40af; font-size:.85rem; display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; }
.success-banner { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:1rem 1.25rem; color:#15803d; font-size:.85rem; display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; }
.form-section-label { font-size:.7rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.08em; margin:1.25rem 0 .75rem; padding-top:.75rem; border-top:1px solid #f1f5f9; }
</style>
""", unsafe_allow_html=True)

# ── INIT DB ───────────────────────────────────────────────────────────────────
init_db()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def resultado_badge(r):
    cls = {"FAVORABLE":"b-fav","DESFAVORABLE":"b-desfav","CONDICIONADO":"b-cond"}.get(r,"b-gray")
    return f"<span class='badge {cls}'>{r or 'N/D'}</span>"

def pct_color(p):
    if p >= 0.95: return "#10b981"
    if p >= 0.85: return "#f59e0b"
    return "#ef4444"

def gauge_html(value, title, label, threshold_color):
    """
    Pure SVG ring gauge embedded as HTML — renders perfectly in Streamlit st.markdown.
    value: 0.0–1.0 (percentage) or a raw score depending on display_val
    threshold_color: result of pct_color()
    label: subtitle shown below value (e.g. '111/117 ítems')
    """
    import math

    pct = max(0.0, min(1.0, value))
    display_val = f"{pct*100:.0f}%"

    # Color theme
    if threshold_color == "#10b981":
        arc_col, txt_col, track_col, status_txt = "#1D9E75", "#085041", "#E1F5EE", "Muy favorable"
    elif threshold_color == "#f59e0b":
        arc_col, txt_col, track_col, status_txt = "#EF9F27", "#854F0B", "#FAEEDA", "Aceptable"
    else:
        arc_col, txt_col, track_col, status_txt = "#E24B4A", "#791F1F", "#FCEBEB", "Desfavorable"

    # SVG arc geometry — 240° sweep, starts at 210°
    cx, cy, r = 100, 100, 70
    stroke_w = 16
    sweep = 240
    start = 210

    def pt(deg):
        rad = math.radians(deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def arc(d1, d2):
        x1, y1 = pt(d1); x2, y2 = pt(d2)
        diff = d2 - d1
        laf = 1 if diff > 180 else 0
        return f"M {x1:.3f} {y1:.3f} A {r} {r} 0 {laf} 1 {x2:.3f} {y2:.3f}"

    track   = arc(start, start + sweep)
    end_deg = start + sweep * pct
    fill    = arc(start, end_deg) if pct > 0.005 else ""

    # Circumference trick: use stroke-dasharray on a full circle for crisp rendering
    # Instead, render path directly — works fine in browsers
    fill_svg = f'<path d="{fill}" fill="none" stroke="{arc_col}" stroke-width="{stroke_w}" stroke-linecap="round"/>' if fill else ""

    # End-cap dot for fill arc
    ex, ey = pt(end_deg)
    cap_svg = f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{stroke_w//2}" fill="{arc_col}"/>' if pct > 0.02 else ""

    svg = f"""
    <div style="background:white;border-radius:14px;border:1px solid #e8eef5;
                box-shadow:0 2px 8px rgba(0,0,0,.04);padding:1.25rem 1rem 1rem;text-align:center;">
      <div style="font-size:.72rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
                  letter-spacing:.07em;margin-bottom:.5rem;">{title}</div>
      <svg width="200" height="165" viewBox="0 0 200 145" xmlns="http://www.w3.org/2000/svg"
           style="display:block;margin:0 auto;overflow:visible;">
        <!-- track -->
        <path d="{track}" fill="none" stroke="{track_col}" stroke-width="{stroke_w}" stroke-linecap="round"/>
        <!-- fill -->
        {fill_svg}
        {cap_svg}
        <!-- start cap -->
        <circle cx="{pt(start)[0]:.2f}" cy="{pt(start)[1]:.2f}" r="{stroke_w//2}" fill="{track_col}"/>
        <!-- value -->
        <text x="100" y="95" text-anchor="middle" dominant-baseline="middle"
              font-family="Inter,sans-serif" font-size="30" font-weight="700" fill="{arc_col}">{display_val}</text>
        <!-- status -->
        <text x="100" y="118" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="11" fill="{txt_col}">{status_txt}</text>
        <!-- label -->
        <text x="100" y="134" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="10" fill="#94a3b8">{label}</text>
        <!-- scale ticks -->
        <text x="{pt(start)[0]-6:.1f}" y="{pt(start)[1]+4:.1f}" text-anchor="end"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">0%</text>
        <text x="{pt(start+sweep)[0]+6:.1f}" y="{pt(start+sweep)[1]+4:.1f}" text-anchor="start"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">100%</text>
      </svg>
    </div>"""
    return svg

def generate_excel_report(aud_row, items_farma, items_tienda, hallazgos, botiquin, tienda_name):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Resumen
        resumen = pd.DataFrame({
            "Campo": ["Tienda","Fecha","Auditor","Calificación Global","Resultado"],
            "Valor": [tienda_name, aud_row["fecha"], aud_row["auditor"],
                      f"{aud_row['calificacion_global']:.0%}", aud_row["resultado"]]
        })
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

        # Farma
        if len(items_farma):
            items_farma[["seccion_nombre","item","puntaje","observacion"]].rename(columns={
                "seccion_nombre":"Sección","item":"Ítem","puntaje":"Puntaje","observacion":"Observación"
            }).to_excel(writer, sheet_name="Auditoría Farma", index=False)

        # Tienda
        if len(items_tienda):
            items_tienda[["criterio","minimo","superior","meta","calificacion"]].rename(columns={
                "criterio":"Criterio","minimo":"Mínimo","superior":"Superior",
                "meta":"Meta","calificacion":"Calificación"
            }).to_excel(writer, sheet_name="Auditoría Tienda", index=False)

        # Hallazgos
        if len(hallazgos):
            hallazgos[["proceso_afectado","hallazgo","observaciones","estado"]].rename(columns={
                "proceso_afectado":"Proceso","hallazgo":"Hallazgo",
                "observaciones":"Observaciones","estado":"Estado"
            }).to_excel(writer, sheet_name="Hallazgos", index=False)

        # Botiquín
        if len(botiquin):
            botiquin[["item","unidades","fecha_vencimiento"]].rename(columns={
                "item":"Elemento","unidades":"Unidades","fecha_vencimiento":"Vencimiento"
            }).to_excel(writer, sheet_name="Botiquín", index=False)

    buf.seek(0)
    return buf

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "📊  Dashboard"

# ── TOPBAR — fixed HTML bar with hamburger that toggles native sidebar ────────
page       = st.session_state["page"]
page_short = page.split("  ", 1)[1] if "  " in page else page
today_str  = date.today().strftime("%d/%m/%Y")

st.markdown(f"""
<div class="topbar" id="topbar">
  <button class="ham" id="hamBtn" onclick="hamToggle(this)" aria-label="Abrir menú">
    <span></span><span></span><span></span>
  </button>
  <div style="display:flex;flex-direction:column;justify-content:center;line-height:1.2;">
    <div class="tb-logo">🏥 Locatel</div>
    <div class="tb-sub">Autoinspección · v2.0</div>
  </div>
  <div class="tb-space"></div>
  <div class="tb-chip"><span class="tb-page">{page_short}</span>&nbsp;·&nbsp;{today_str}</div>
</div>

<script>
(function(){{
  var open = true; // sidebar starts expanded

  function hamToggle(btn) {{
    var p = window.parent.document;
    var sb = p.querySelector('[data-testid="stSidebar"]');
    if (!sb) return;
    open = !open;
    if (open) {{
      sb.style.marginLeft = '0';
      sb.style.transform  = 'translateX(0)';
      sb.style.visibility = 'visible';
      sb.style.width      = '18rem';
      btn.classList.add('is-open');
    }} else {{
      sb.style.marginLeft = '-18rem';
      sb.style.transform  = 'translateX(-100%)';
      btn.classList.remove('is-open');
    }}
    // also shift main content
    var main = p.querySelector('.main') || p.querySelector('[data-testid="stMain"]');
    if (main) main.style.marginLeft = open ? '18rem' : '0';
  }}

  // expose globally so the button onclick fires correctly across iframe boundary
  window.hamToggle = hamToggle;

  // run on every Streamlit rerender to keep sidebar state consistent
  function applyState() {{
    var p   = window.parent.document;
    var sb  = p.querySelector('[data-testid="stSidebar"]');
    var btn = document.getElementById('hamBtn');
    if (!sb || !btn) return;
    if (open) {{
      sb.style.marginLeft = '0';
      sb.style.transform  = 'translateX(0)';
      sb.style.visibility = 'visible';
      sb.style.width      = '18rem';
      btn.classList.add('is-open');
    }} else {{
      sb.style.marginLeft = '-18rem';
      sb.style.transform  = 'translateX(-100%)';
      btn.classList.remove('is-open');
    }}
  }}
  setTimeout(applyState, 300);
  setTimeout(applyState, 800);
}})();
</script>
""", unsafe_allow_html=True)

# ── SIDEBAR — real Streamlit sidebar acting as the drawer ─────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem .25rem 1rem;'>
      <div style='font-size:.6rem;font-weight:700;color:#2d4a6b;text-transform:uppercase;
                  letter-spacing:.1em;margin-bottom:.75rem;'>Navegación</div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("📊", "Dashboard",        "📊  Dashboard"),
        ("💊", "Auditoría Farma",  "💊  Auditoría Farma"),
        ("🏪", "Auditoría Tienda", "🏪  Auditoría Tienda"),
        ("⚠️", "Hallazgos",        "⚠️  Hallazgos"),
        ("🩺", "Botiquín",         "🩺  Botiquín"),
        ("➕", "Nueva Auditoría",  "➕  Nueva Auditoría"),
    ]

    for icon, label, key in nav_items:
        is_active = st.session_state["page"] == key
        # Inject active class wrapper via markdown
        if is_active:
            st.markdown("""<style>
            [data-testid="stSidebar"] div:has(> div > div > button[data-active="true"]) button {
                background: rgba(37,99,235,.22) !important;
                border-color: rgba(59,130,246,.55) !important;
                color: #60a5fa !important; font-weight: 700 !important;
            }</style>""", unsafe_allow_html=True)
        btn_label = f"{'▶  ' if is_active else '    '}{icon}  {label}"
        if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
            st.session_state["page"] = key
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #1a2744;margin:.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.6rem;font-weight:700;color:#2d4a6b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;'>Configuración</div>", unsafe_allow_html=True)

    conn = get_connection()
    tiendas_df = pd.read_sql("SELECT id, nombre FROM tiendas ORDER BY id", conn)
    conn.close()
    t_opts = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in tiendas_df.iterrows()}
    sel_label = st.selectbox("Tienda", list(t_opts.keys()), index=2)
    sel_tienda = t_opts[sel_label]

    conn = get_connection()
    auds = pd.read_sql(
        "SELECT id,fecha,auditor,calificacion_global,resultado FROM auditorias WHERE tienda_id=? ORDER BY fecha DESC",
        conn, params=(sel_tienda,))
    conn.close()

    if len(auds):
        a_opts = {f"{r['fecha']}  ·  {r['auditor']}": r['id'] for _, r in auds.iterrows()}
        sel_aud_label = st.selectbox("Auditoría", list(a_opts.keys()))
        sel_aud_id = a_opts[sel_aud_label]
    else:
        st.markdown("<div style='font-size:.78rem;color:#3b5270;padding:.5rem 0;'>Sin auditorías registradas</div>", unsafe_allow_html=True)
        sel_aud_id = None

    st.markdown(f"<div style='font-size:.62rem;color:#2d4a6b;padding:1rem 0 .5rem;font-weight:600;'>Hoy · {today_str}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════
if page == "📊  Dashboard":
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona o crea una auditoría en el panel lateral para comenzar.</div>", unsafe_allow_html=True)
        st.stop()

    conn = get_connection()
    aud = conn.execute("SELECT * FROM auditorias WHERE id=?", (sel_aud_id,)).fetchone()
    items_f = pd.read_sql("SELECT if.*, sf.nombre as seccion_nombre FROM items_farma if JOIN secciones_farma sf ON sf.id=if.seccion_id WHERE if.auditoria_id=?", conn, params=(sel_aud_id,))
    items_t = pd.read_sql("SELECT * FROM items_tienda WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    hall    = pd.read_sql("SELECT * FROM hallazgos WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    boti    = pd.read_sql("SELECT * FROM botiquin WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    conn.close()

    tienda_name = sel_label.split(" - ",1)[1]
    audit_date  = datetime.strptime(aud["fecha"],"%Y-%m-%d").strftime("%d %b %Y")
    resultado   = aud["resultado"] or "N/D"
    calif       = aud["calificacion_global"] or 0

    res_cls = "favorable" if resultado=="FAVORABLE" else "desfavorable" if resultado=="DESFAVORABLE" else ""

    # ── Header
    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>📊 Dashboard — {tienda_name}</div>
        <div class='ph-sub'>📅 {audit_date} &nbsp;·&nbsp; 👤 {aud['auditor']}</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>ID #{sel_aud_id}</span>
        <span class='ph-badge {res_cls}'>{resultado}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Download buttons
    dc1, dc2, dc3 = st.columns([1,1,3])
    with dc1:
        xl = generate_excel_report(dict(aud), items_f, items_t, hall, boti, tienda_name)
        st.download_button("⬇️ Descargar Excel", xl, file_name=f"auditoria_{tienda_name.replace(' ','_')}_{aud['fecha']}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with dc2:
        csv_data = items_f[["seccion_nombre","item","puntaje","observacion"]].to_csv(index=False)
        st.download_button("⬇️ Descargar CSV", csv_data, file_name=f"items_{aud['fecha']}.csv", mime="text/csv", use_container_width=True)

    # ── KPIs
    tf = len(items_f); cf = int(items_f["puntaje"].sum()) if tf else 0
    pf = cf/tf if tf else 0
    pt = items_t["calificacion"].mean()/10 if len(items_t) else 0
    avg_t = items_t["calificacion"].mean() if len(items_t) else 0
    h_pend = len(hall[hall["estado"]=="Pendiente"]) if len(hall) else 0

    # ── Color helpers for KPI values
    def _val_color(pct):
        if pct >= 0.95: return "val-green"
        if pct >= 0.85: return "val-amber"
        return "val-red"

    res_val_color = "val-green" if resultado=="FAVORABLE" else ("val-amber" if resultado=="CONDICIONADO" else "val-red")
    res_accent    = "green"     if resultado=="FAVORABLE" else ("amber"     if resultado=="CONDICIONADO" else "red")
    hall_accent   = "red" if h_pend > 0 else "green"
    hall_val_col  = "val-red" if h_pend > 0 else "val-green"

    k1,k2,k3,k4,k5 = st.columns(5)

    k1.markdown(f"""<div class='kpi blue'>
      <div class='kpi-lbl'>Calificación Global</div>
      <div class='kpi-val {_val_color(calif)}'>{calif:.0%}</div>
      <div class='kpi-sub'>Score consolidado</div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""<div class='kpi green'>
      <div class='kpi-lbl'>Cumplimiento Farma</div>
      <div class='kpi-val {_val_color(pf)}'>{pf:.0%}</div>
      <div class='kpi-sub'>{cf}/{tf} ítems</div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""<div class='kpi purple'>
      <div class='kpi-lbl'>Promedio Tienda</div>
      <div class='kpi-val {_val_color(pt)}'>{avg_t:.1f}</div>
      <div class='kpi-sub'>Meta: 9.5 / 10</div>
    </div>""", unsafe_allow_html=True)

    k4.markdown(f"""<div class='kpi {hall_accent}'>
      <div class='kpi-lbl'>Hallazgos Pendientes</div>
      <div class='kpi-val {hall_val_col}'>{h_pend}</div>
      <div class='kpi-sub'>sin resolver</div>
    </div>""", unsafe_allow_html=True)

    k5.markdown(f"""<div class='kpi {res_accent}'>
      <div class='kpi-lbl'>Estado</div>
      <div class='kpi-val {res_val_color}' style='font-size:1.15rem;'>{resultado}</div>
      <div class='kpi-sub'>{audit_date}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauges (pure SVG, renders natively in Streamlit)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(gauge_html(pf,  "Farmacia",  f"{cf}/{tf} ítems",        pct_color(pf)),   unsafe_allow_html=True)
    with g2:
        st.markdown(gauge_html(pt,  "Tienda",    f"Prom. {avg_t:.1f} / 10", pct_color(pt)),   unsafe_allow_html=True)
    with g3:
        st.markdown(gauge_html(calif,"Global",   resultado,                  pct_color(calif)), unsafe_allow_html=True)

    # ── Charts
    cl, cr = st.columns([1.3,1])
    with cl:
        st.markdown("<div class='card'><div class='card-hd'>Cumplimiento por Sección</div>", unsafe_allow_html=True)
        conn2 = get_connection()
        secs = pd.read_sql("SELECT * FROM secciones_farma", conn2); conn2.close()
        sec_data = []
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"]==s["id"]]
            if len(si):
                cum = int(si["puntaje"].sum()); tot = len(si); pct = cum/tot
                sec_data.append({"seccion": s["nombre"], "cum": cum, "tot": tot, "pct": pct})

        if sec_data:
            for d in sec_data:
                p   = d["pct"]
                bar_color = "#1D9E75" if p>=0.95 else ("#EF9F27" if p>=0.85 else "#E24B4A")
                txt_color = "#085041" if p>=0.95 else ("#854F0B" if p>=0.85 else "#791F1F")
                bg_color  = "#E1F5EE" if p>=0.95 else ("#FAEEDA" if p>=0.85 else "#FCEBEB")
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
                  <div style='font-size:.78rem;color:#475569;min-width:220px;max-width:220px;
                              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' title='{d["seccion"]}'>
                    {d["seccion"]}
                  </div>
                  <div style='flex:1;height:22px;background:{bg_color};border-radius:5px;overflow:hidden;position:relative;'>
                    <div style='width:{p*100:.0f}%;height:100%;background:{bar_color};border-radius:5px;
                                display:flex;align-items:center;justify-content:flex-end;padding-right:8px;
                                font-size:.72rem;font-weight:600;color:white;min-width:40px;'>
                      {d["cum"]}/{d["tot"]}
                    </div>
                  </div>
                  <div style='font-size:.78rem;font-weight:700;color:{txt_color};min-width:36px;text-align:right;'>{p:.0%}</div>
                </div>""", unsafe_allow_html=True)

            # Legend
            st.markdown("""
            <div style='display:flex;gap:14px;margin-top:10px;padding-top:10px;
                        border-top:1px solid #f1f5f9;font-size:.72rem;color:#94a3b8;flex-wrap:wrap;'>
              <span style='display:flex;align-items:center;gap:5px;'>
                <span style='width:9px;height:9px;border-radius:2px;background:#1D9E75;display:inline-block;'></span>≥ 95% · Muy favorable
              </span>
              <span style='display:flex;align-items:center;gap:5px;'>
                <span style='width:9px;height:9px;border-radius:2px;background:#EF9F27;display:inline-block;'></span>85–94% · Aceptable
              </span>
              <span style='display:flex;align-items:center;gap:5px;'>
                <span style='width:9px;height:9px;border-radius:2px;background:#E24B4A;display:inline-block;'></span>&lt; 85% · Desfavorable
              </span>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with cr:
        st.markdown("<div class='card'><div class='card-hd'>Criterios de Tienda</div>", unsafe_allow_html=True)
        for _, row in items_t.iterrows():
            cal = row["calificacion"]; color = "#10b981" if cal>=row["superior"] else ("#f59e0b" if cal>=row["minimo"] else "#ef4444")
            st.markdown(f"""
            <div style='margin-bottom:.55rem;'>
              <div style='display:flex;justify-content:space-between;font-size:.77rem;color:#475569;margin-bottom:3px;'>
                <span>{row['criterio']}</span><span style='font-weight:700;color:{color};'>{cal}</span>
              </div>
              <div class='pb-wrap'><div class='pb-fill' style='width:{cal/10*100:.0f}%;background:{color};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Hallazgos
    if len(hall):
        st.markdown("<div class='card'><div class='card-hd'>⚠️ Hallazgos Activos</div>", unsafe_allow_html=True)
        for _, h in hall.iterrows():
            ok = h["estado"]=="Resuelto"
            bc = "#10b981" if ok else "#ef4444"; bg = "#f0fdf4" if ok else "#fff5f5"
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {bc};border-left:4px solid {bc};
                 border-radius:9px;padding:.9rem 1.1rem;margin-bottom:.4rem;'>
              <div style='display:flex;justify-content:space-between;'>
                <span style='font-weight:600;font-size:.83rem;color:#0f172a;'>{h['proceso_afectado']}</span>
                <span class='badge {"b-ok" if ok else "b-fail"}'>{h['estado']}</span>
              </div>
              <div style='color:#64748b;font-size:.79rem;margin-top:2px;'>{h['hallazgo']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: AUDITORÍA FARMA (EDITABLE)
# ═══════════════════════════════════════════════════════════
elif page == "💊  Auditoría Farma":
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría en el panel lateral.</div>", unsafe_allow_html=True)
        st.stop()

    conn = get_connection()
    items_f = pd.read_sql("""
        SELECT if.*, sf.nombre as seccion_nombre
        FROM items_farma if
        JOIN secciones_farma sf ON sf.id=if.seccion_id
        WHERE if.auditoria_id=?
        ORDER BY if.seccion_id, if.id""", conn, params=(sel_aud_id,))
    conn.close()

    tf = len(items_f); cf = int(items_f["puntaje"].sum()) if tf else 0
    pf = cf/tf if tf else 0

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>💊 Auditoría Farmacéutica</div>
        <div class='ph-sub'>Edita el puntaje y observación de cada ítem. Los cambios se guardan automáticamente.</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>{cf}/{tf} cumplidos</span>
        <span class='ph-badge' style='background:rgba({"16,185,129" if pf>=.95 else "245,158,11" if pf>=.85 else "239,68,68"},.15);color:{"#34d399" if pf>=.95 else "#fbbf24" if pf>=.85 else "#f87171"};border-color:rgba({"16,185,129" if pf>=.95 else "245,158,11" if pf>=.85 else "239,68,68"},.35);'>{pf:.0%}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Filters + download
    fc1, fc2, fc3 = st.columns([2,1,1])
    with fc1:
        search = st.text_input("🔍 Buscar ítem", placeholder="Filtra por nombre...", label_visibility="collapsed")
    with fc2:
        filt = st.selectbox("Estado", ["Todos","✓ Cumplidos","✗ Incumplidos"], label_visibility="collapsed")
    with fc3:
        csv_f = items_f[["seccion_nombre","item","puntaje","observacion"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_f, file_name="farma.csv", mime="text/csv", use_container_width=True)

    df_view = items_f.copy()
    if search: df_view = df_view[df_view["item"].str.contains(search, case=False, na=False)]
    if filt == "✓ Cumplidos": df_view = df_view[df_view["puntaje"]==1]
    elif filt == "✗ Incumplidos": df_view = df_view[df_view["puntaje"]==0]

    secciones = df_view["seccion_nombre"].unique()
    changes_made = False

    for seccion in secciones:
        sec_df = df_view[df_view["seccion_nombre"]==seccion]
        sc = int(sec_df["puntaje"].sum()); st_ = len(sec_df); sp = sc/st_ if st_ else 0
        color_sp = pct_color(sp)

        with st.expander(f"📁  {seccion}   ·   {sc}/{st_}   ({sp:.0%})", expanded=True):
            # Section progress bar
            st.markdown(f"""
            <div style='margin-bottom:1rem;'>
              <div class='pb-wrap'><div class='pb-fill' style='width:{sp*100:.0f}%;background:{color_sp};'></div></div>
              <div style='font-size:.72rem;color:#94a3b8;margin-top:4px;'>{sc} de {st_} ítems cumplidos</div>
            </div>""", unsafe_allow_html=True)

            for _, row in sec_df.iterrows():
                row_class = "pass" if row["puntaje"]==1 else "fail"
                left, mid, right = st.columns([3, 1.2, 2])

                with left:
                    st.markdown(f"""
                    <div class='audit-item-row {row_class}' style='padding:.6rem .85rem;'>
                      <div class='item-name'>{row['item']}</div>
                    </div>""", unsafe_allow_html=True)

                with mid:
                    cur_val = "✓ Cumple" if row["puntaje"]==1 else "✗ No Cumple"
                    new_val = st.radio(
                        f"puntaje_{row['id']}",
                        ["✓ Cumple","✗ No Cumple"],
                        index=0 if row["puntaje"]==1 else 1,
                        key=f"radio_{row['id']}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    new_puntaje = 1 if new_val=="✓ Cumple" else 0
                    if new_puntaje != row["puntaje"]:
                        c = get_connection()
                        c.execute("UPDATE items_farma SET puntaje=? WHERE id=?", (new_puntaje, row["id"]))
                        c.commit(); c.close()
                        changes_made = True

                with right:
                    obs_current = row["observacion"] if pd.notna(row["observacion"]) else ""
                    new_obs = st.text_input(
                        f"obs_{row['id']}", value=obs_current,
                        placeholder="Observación...",
                        key=f"obs_{row['id']}",
                        label_visibility="collapsed"
                    )
                    if new_obs != obs_current:
                        c = get_connection()
                        c.execute("UPDATE items_farma SET observacion=? WHERE id=?",
                                  (new_obs if new_obs else None, row["id"]))
                        c.commit(); c.close()
                        changes_made = True

    if changes_made:
        st.rerun()

    # Recalculate global score
    conn = get_connection()
    all_f = pd.read_sql("SELECT * FROM items_farma WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    conn.close()
    new_global = all_f["puntaje"].sum()/len(all_f) if len(all_f) else 0
    conn = get_connection()
    conn.execute("UPDATE auditorias SET calificacion_global=? WHERE id=?", (new_global, sel_aud_id))
    conn.commit(); conn.close()


# ═══════════════════════════════════════════════════════════
# PAGE: AUDITORÍA TIENDA (EDITABLE)
# ═══════════════════════════════════════════════════════════
elif page == "🏪  Auditoría Tienda":
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    conn = get_connection()
    items_t = pd.read_sql("SELECT * FROM items_tienda WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    conn.close()

    avg = items_t["calificacion"].mean() if len(items_t) else 0

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>🏪 Auditoría de Tienda</div>
        <div class='ph-sub'>Edita las calificaciones de cada criterio operativo.</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>Promedio: {avg:.1f}</span>
        <span class='ph-badge'>Meta: 9.5</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if len(items_t)==0:
        st.info("Sin datos de tienda para esta auditoría.")
        st.stop()

    dl_col, _, _ = st.columns([1,1,2])
    with dl_col:
        csv_t = items_t[["criterio","minimo","superior","meta","calificacion"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_t, file_name="tienda.csv", mime="text/csv", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    changes_t = False
    st.markdown("<div class='card'><div class='card-hd'>Criterios Operativos</div>", unsafe_allow_html=True)

    for _, row in items_t.iterrows():
        cal = row["calificacion"]
        color = "#10b981" if cal>=row["superior"] else ("#f59e0b" if cal>=row["minimo"] else "#ef4444")
        if cal>=row["superior"]: badge_t="b-ok"; lbl="Superior"
        elif cal>=row["minimo"]: badge_t="b-warn"; lbl="Aceptable"
        else: badge_t="b-fail"; lbl="Bajo mínimo"

        c1, c2, c3 = st.columns([2.5, 1.5, 1])
        with c1:
            st.markdown(f"""
            <div style='padding:.65rem .9rem;background:#f8fafc;border:1px solid #e8eef5;border-left:3px solid {color};border-radius:9px;'>
              <div style='font-weight:600;font-size:.85rem;color:#0f172a;'>{row['criterio']}</div>
              <div style='font-size:.74rem;color:#94a3b8;margin-top:3px;'>Mín: {row['minimo']} · Superior: {row['superior']} · Meta: {row['meta']}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            new_cal = st.number_input(
                f"cal_{row['id']}", min_value=0.0, max_value=10.0,
                value=float(cal), step=0.5,
                key=f"nc_{row['id']}", label_visibility="collapsed"
            )
            if new_cal != cal:
                c = get_connection()
                c.execute("UPDATE items_tienda SET calificacion=? WHERE id=?", (new_cal, row["id"]))
                c.commit(); c.close()
                changes_t = True
        with c3:
            st.markdown(f"<div style='padding:.65rem 0;'><span class='badge {badge_t}'>{lbl}</span></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Chart
    conn = get_connection()
    items_t2 = pd.read_sql("SELECT * FROM items_tienda WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    conn.close()

    st.markdown("<div class='card'><div class='card-hd'>Gráfico de Calificaciones</div>", unsafe_allow_html=True)
    for _, row in items_t2.iterrows():
        cal = row["calificacion"]
        color = "#1D9E75" if cal>=row["superior"] else ("#EF9F27" if cal>=row["minimo"] else "#E24B4A")
        txt_color = "#085041" if cal>=row["superior"] else ("#854F0B" if cal>=row["minimo"] else "#791F1F")
        bg_color  = "#E1F5EE" if cal>=row["superior"] else ("#FAEEDA" if cal>=row["minimo"] else "#FCEBEB")
        pct_width = cal / 10 * 100
        # Meta marker position
        meta_pct = row["meta"] / 10 * 100
        sup_pct  = row["superior"] / 10 * 100
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
          <div style='display:flex;justify-content:space-between;font-size:.78rem;color:#475569;margin-bottom:4px;'>
            <span style='font-weight:500;'>{row['criterio']}</span>
            <span style='font-weight:700;color:{txt_color};'>{cal}</span>
          </div>
          <div style='position:relative;height:24px;background:{bg_color};border-radius:6px;overflow:visible;'>
            <div style='width:{pct_width:.0f}%;height:100%;background:{color};border-radius:6px;
                        display:flex;align-items:center;justify-content:flex-end;padding-right:8px;
                        font-size:.72rem;font-weight:600;color:white;min-width:36px;transition:width .4s ease;'></div>
            <!-- Meta line -->
            <div style='position:absolute;top:-3px;bottom:-3px;left:{meta_pct:.0f}%;
                        width:2px;background:#1a56db;border-radius:1px;opacity:.5;'
                 title='Meta: {row["meta"]}'></div>
            <!-- Superior line -->
            <div style='position:absolute;top:-3px;bottom:-3px;left:{sup_pct:.0f}%;
                        width:2px;background:#7c3aed;border-radius:1px;opacity:.4;'
                 title='Superior: {row["superior"]}'></div>
          </div>
          <div style='display:flex;gap:12px;margin-top:3px;font-size:.68rem;color:#94a3b8;'>
            <span>Mín: {row['minimo']}</span>
            <span style='color:#1a56db;'>● Meta: {row['meta']}</span>
            <span style='color:#7c3aed;'>● Superior: {row['superior']}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if changes_t:
        st.rerun()


# ═══════════════════════════════════════════════════════════
# PAGE: HALLAZGOS
# ═══════════════════════════════════════════════════════════
elif page == "⚠️  Hallazgos":
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    conn = get_connection()
    hall = pd.read_sql("SELECT * FROM hallazgos WHERE auditoria_id=? ORDER BY id", conn, params=(sel_aud_id,))
    conn.close()

    pend = len(hall[hall["estado"]=="Pendiente"]) if len(hall) else 0
    res  = len(hall[hall["estado"]=="Resuelto"]) if len(hall) else 0

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>⚠️ Gestión de Hallazgos</div>
        <div class='ph-sub'>Seguimiento y resolución de no conformidades detectadas.</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge' style='background:rgba(239,68,68,.15);color:#f87171;border-color:rgba(239,68,68,.3);'>{pend} Pendientes</span>
        <span class='ph-badge' style='background:rgba(16,185,129,.15);color:#34d399;border-color:rgba(16,185,129,.3);'>{res} Resueltos</span>
      </div>
    </div>""", unsafe_allow_html=True)

    dl_col2, add_col, _ = st.columns([1,1,2])
    with dl_col2:
        if len(hall):
            csv_h = hall[["proceso_afectado","hallazgo","observaciones","estado"]].to_csv(index=False)
            st.download_button("⬇️ Exportar CSV", csv_h, file_name="hallazgos.csv", mime="text/csv", use_container_width=True)
    with add_col:
        if st.button("➕ Nuevo Hallazgo", type="primary", use_container_width=True):
            st.session_state["show_hall"] = not st.session_state.get("show_hall", False)

    if st.session_state.get("show_hall"):
        with st.form("add_hall"):
            st.markdown("<div class='form-section-label'>Nuevo Hallazgo</div>", unsafe_allow_html=True)
            hc1, hc2 = st.columns(2)
            proc = hc1.text_input("Proceso Afectado")
            obs  = hc2.text_input("Observaciones")
            desc = st.text_area("Descripción del Hallazgo")
            if st.form_submit_button("💾 Guardar Hallazgo", type="primary") and proc and desc:
                c = get_connection()
                c.execute("INSERT INTO hallazgos (auditoria_id,proceso_afectado,hallazgo,observaciones,estado) VALUES (?,?,?,?,'Pendiente')",
                          (sel_aud_id, proc, desc, obs or None))
                c.commit(); c.close()
                st.session_state["show_hall"] = False
                st.rerun()

    # ── Edit / Delete state
    editing_id  = st.session_state.get("edit_hall_id")
    confirm_del = st.session_state.get("confirm_del_id")

    if len(hall) == 0:
        st.markdown("<div class='success-banner'>✅ No hay hallazgos registrados para esta auditoría.</div>", unsafe_allow_html=True)
    else:
        for _, h in hall.iterrows():
            hid = int(h["id"])
            ok  = h["estado"] == "Resuelto"
            bc  = "#10b981" if ok else "#ef4444"
            bg  = "#f0fdf4" if ok else "#fff8f8"
            bdr = "#bbf7d0" if ok else "#fecdd3"

            # ── EDIT MODE for this row
            if editing_id == hid:
                with st.form(f"edit_form_{hid}"):
                    st.markdown(f"<div style='font-size:.75rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.75rem;'>✏️ Editando hallazgo #{hid}</div>", unsafe_allow_html=True)
                    ec1, ec2 = st.columns(2)
                    e_proc = ec1.text_input("Proceso Afectado", value=h["proceso_afectado"])
                    e_est  = ec2.selectbox("Estado", ["Pendiente","Resuelto"],
                                           index=0 if h["estado"]=="Pendiente" else 1)
                    e_hall = st.text_area("Descripción", value=h["hallazgo"])
                    e_obs  = st.text_input("Observaciones", value=h["observaciones"] if pd.notna(h.get("observaciones")) and h["observaciones"] else "")
                    sc1, sc2 = st.columns(2)
                    if sc1.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                        c = get_connection()
                        c.execute("""UPDATE hallazgos SET proceso_afectado=?, hallazgo=?,
                                     observaciones=?, estado=? WHERE id=?""",
                                  (e_proc, e_hall, e_obs or None, e_est, hid))
                        c.commit(); c.close()
                        st.session_state.pop("edit_hall_id", None)
                        st.rerun()
                    if sc2.form_submit_button("✕ Cancelar", use_container_width=True):
                        st.session_state.pop("edit_hall_id", None)
                        st.rerun()
                continue  # skip normal card render while editing

            # ── NORMAL CARD + ACTION BUTTONS
            card_col, btn_col = st.columns([5, 1])

            with card_col:
                obs_html = f'<div style="color:#94a3b8;font-size:.76rem;margin-top:.2rem;font-style:italic;">{h["observaciones"]}</div>' \
                           if pd.notna(h.get("observaciones")) and h["observaciones"] else ""
                st.markdown(f"""
                <div style='background:{bg};border:1px solid {bdr};border-left:4px solid {bc};
                     border-radius:10px;padding:1rem 1.25rem;margin-bottom:.25rem;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <span style='font-weight:700;font-size:.88rem;color:#0f172a;'>#{hid} · {h["proceso_afectado"]}</span>
                    <span class='badge {"b-ok" if ok else "b-fail"}'>{h["estado"]}</span>
                  </div>
                  <div style='color:#475569;font-size:.81rem;margin-top:.35rem;'>{h["hallazgo"]}</div>
                  {obs_html}
                </div>""", unsafe_allow_html=True)

            with btn_col:
                # Resolve / Reopen
                if not ok:
                    if st.button("✅ Resolver", key=f"res_{hid}", use_container_width=True):
                        c = get_connection()
                        c.execute("UPDATE hallazgos SET estado='Resuelto' WHERE id=?", (hid,))
                        c.commit(); c.close(); st.rerun()
                else:
                    if st.button("↩️ Reabrir", key=f"reopen_{hid}", use_container_width=True):
                        c = get_connection()
                        c.execute("UPDATE hallazgos SET estado='Pendiente' WHERE id=?", (hid,))
                        c.commit(); c.close(); st.rerun()

                # Edit
                if st.button("✏️ Editar", key=f"edit_{hid}", use_container_width=True):
                    st.session_state["edit_hall_id"] = hid
                    st.session_state.pop("confirm_del_id", None)
                    st.rerun()

                # Delete — two-step confirm
                if confirm_del == hid:
                    st.markdown("<div style='font-size:.72rem;color:#b91c1c;font-weight:600;text-align:center;margin-top:2px;'>¿Confirmar?</div>", unsafe_allow_html=True)
                    cd1, cd2 = st.columns(2)
                    if cd1.button("Sí", key=f"del_yes_{hid}", use_container_width=True):
                        c = get_connection()
                        c.execute("DELETE FROM hallazgos WHERE id=?", (hid,))
                        c.commit(); c.close()
                        st.session_state.pop("confirm_del_id", None)
                        st.rerun()
                    if cd2.button("No", key=f"del_no_{hid}", use_container_width=True):
                        st.session_state.pop("confirm_del_id", None)
                        st.rerun()
                else:
                    if st.button("🗑️ Borrar", key=f"del_{hid}", use_container_width=True):
                        st.session_state["confirm_del_id"] = hid
                        st.session_state.pop("edit_hall_id", None)
                        st.rerun()

            st.markdown("<div style='margin-bottom:.5rem;'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: BOTIQUÍN
# ═══════════════════════════════════════════════════════════
elif page == "🩺  Botiquín":
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    conn = get_connection()
    boti = pd.read_sql("SELECT * FROM botiquin WHERE auditoria_id=?", conn, params=(sel_aud_id,))
    conn.close()

    today = date.today()

    def venc_status(fs):
        if not fs or pd.isna(fs): return "Sin fecha","b-gray",999
        try:
            d = datetime.strptime(str(fs),"%Y-%m-%d").date()
            diff = (d-today).days
            if diff<0: return f"Vencido","b-fail",diff
            elif diff<=90: return f"⚠️ {diff}d","b-warn",diff
            else: return d.strftime("%d/%m/%Y"),"b-ok",diff
        except: return str(fs),"b-gray",999

    vencidos = sum(1 for _,r in boti.iterrows() if venc_status(r["fecha_vencimiento"])[2]<0)
    proximos = sum(1 for _,r in boti.iterrows() if 0<=venc_status(r["fecha_vencimiento"])[2]<=90)

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>🩺 Botiquín de Primeros Auxilios</div>
        <div class='ph-sub'>Control de vencimientos · Resolución 0705 de 2007</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>{len(boti)} elementos</span>
        {"<span class='ph-badge desfavorable'>"+str(vencidos)+" vencidos</span>" if vencidos else ""}
        {"<span class='ph-badge' style='background:rgba(245,158,11,.15);color:#fbbf24;border-color:rgba(245,158,11,.3);'>"+str(proximos)+" próximos</span>" if proximos else ""}
      </div>
    </div>""", unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    k1.markdown(f"<div class='kpi blue'><div class='kpi-lbl'>Total Elementos</div><div class='kpi-val'>{len(boti)}</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='kpi {'red' if vencidos else 'green'}'><div class='kpi-lbl'>Vencidos</div><div class='kpi-val'>{vencidos}</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='kpi amber'><div class='kpi-lbl'>Próx. a Vencer (90d)</div><div class='kpi-val'>{proximos}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dl3, _ = st.columns([1,3])
    with dl3:
        csv_b = boti[["item","unidades","fecha_vencimiento"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_b, file_name="botiquin.csv", mime="text/csv", use_container_width=True)

    st.markdown("<div class='card'><div class='card-hd'>Inventario — edita fechas directamente en cada fila</div>", unsafe_allow_html=True)

    # Column headers
    st.markdown("""
    <div style='display:grid;grid-template-columns:2rem 2.5fr 1.2fr 1.6fr 1fr;gap:.75rem;
         padding:.4rem 1rem;font-size:.68rem;font-weight:700;color:#94a3b8;
         text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #f1f5f9;margin-bottom:.25rem;'>
      <span>#</span><span>Elemento</span><span>Unidades</span><span>Fecha vencimiento</span><span>Estado</span>
    </div>""", unsafe_allow_html=True)

    changes_b = False
    for i, (_, row) in enumerate(boti.iterrows(), 1):
        lbl, bcls, diff = venc_status(row["fecha_vencimiento"])
        row_bg = "#fff8f8" if diff < 0 else ("#fffbeb" if 0 <= diff <= 90 else "white")
        border = "#fecdd3" if diff < 0 else ("#fde68a" if 0 <= diff <= 90 else "#f1f5f9")

        c_num, c_item, c_uni, c_fecha, c_badge = st.columns([0.3, 2.5, 1.2, 1.6, 1])

        with c_num:
            st.markdown(f"<div style='padding:.6rem 0;color:#94a3b8;font-size:.76rem;font-weight:600;'>{i:02d}</div>",
                        unsafe_allow_html=True)

        with c_item:
            new_item = st.text_input(
                f"item_{row['id']}", value=row["item"],
                key=f"bi_{row['id']}", label_visibility="collapsed"
            )
            if new_item != row["item"]:
                c = get_connection()
                c.execute("UPDATE botiquin SET item=? WHERE id=?", (new_item, row["id"]))
                c.commit(); c.close()
                changes_b = True

        with c_uni:
            new_uni = st.text_input(
                f"uni_{row['id']}", value=row["unidades"] or "",
                placeholder="Unidad",
                key=f"bu_{row['id']}", label_visibility="collapsed"
            )
            if new_uni != (row["unidades"] or ""):
                c = get_connection()
                c.execute("UPDATE botiquin SET unidades=? WHERE id=?", (new_uni or None, row["id"]))
                c.commit(); c.close()
                changes_b = True

        with c_fecha:
            # Parse existing date or default to today
            try:
                cur_date = datetime.strptime(str(row["fecha_vencimiento"]), "%Y-%m-%d").date() \
                           if row["fecha_vencimiento"] and pd.notna(row["fecha_vencimiento"]) else date.today()
            except:
                cur_date = date.today()

            new_fecha = st.date_input(
                f"fecha_{row['id']}", value=cur_date,
                key=f"bf_{row['id']}", label_visibility="collapsed",
                format="DD/MM/YYYY"
            )
            if str(new_fecha) != str(row["fecha_vencimiento"] or ""):
                c = get_connection()
                c.execute("UPDATE botiquin SET fecha_vencimiento=? WHERE id=?",
                          (str(new_fecha), row["id"]))
                c.commit(); c.close()
                changes_b = True

        with c_badge:
            # Re-compute status with potentially updated date
            lbl2, bcls2, _ = venc_status(str(new_fecha))
            st.markdown(f"<div style='padding:.55rem 0;'><span class='badge {bcls2}'>{lbl2}</span></div>",
                        unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if changes_b:
        st.rerun()


# ═══════════════════════════════════════════════════════════
# PAGE: NUEVA AUDITORÍA
# ═══════════════════════════════════════════════════════════
elif page == "➕  Nueva Auditoría":
    conn = get_connection()
    tiendas = pd.read_sql("SELECT * FROM tiendas ORDER BY id", conn)
    conn.close()

    st.markdown("""
    <div class='page-header'>
      <div>
        <div class='ph-title'>➕ Nueva Auditoría</div>
        <div class='ph-sub'>Registra una nueva autoinspección. Los ítems se cargan automáticamente para edición.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:1rem 1.25rem;
         color:#1e40af;font-size:.83rem;margin-bottom:1.25rem;display:flex;gap:.75rem;align-items:flex-start;'>
      <span style='font-size:1.1rem;'>💡</span>
      <div>Después de crear la auditoría, ve a <strong>Auditoría Farma</strong> y <strong>Auditoría Tienda</strong>
      para diligenciar cada ítem con su puntaje y observación. El dashboard se actualizará en tiempo real.</div>
    </div>""", unsafe_allow_html=True)

    with st.form("nueva_aud", clear_on_submit=True):
        st.markdown("<div class='form-section-label'>📋 Información General</div>", unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        tienda_sel = r1c1.selectbox("Tienda", [f"{r['id']} - {r['nombre']}" for _,r in tiendas.iterrows()])
        fecha_sel  = r1c2.date_input("Fecha de Auditoría", value=date.today())

        r2c1, r2c2 = st.columns(2)
        auditor    = r2c1.text_input("Nombre del Auditor", placeholder="Ej: Edwin Merchán")
        resultado_sel = r2c2.selectbox("Resultado Inicial", ["FAVORABLE","DESFAVORABLE","CONDICIONADO"])

        st.markdown("<div class='form-section-label'>⚠️ Hallazgos Iniciales (opcional)</div>", unsafe_allow_html=True)
        hcols = st.columns(2)
        hall_inputs = []
        for i in range(4):
            col = hcols[i%2]
            h = col.text_input(f"Hallazgo {i+1}", placeholder="Proceso: Descripción del hallazgo", key=f"hi_{i}")
            hall_inputs.append(h)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Crear Auditoría", type="primary", use_container_width=True)

        if submitted:
            if not auditor.strip():
                st.error("⚠️ El nombre del auditor es requerido.")
            else:
                tienda_id = tienda_sel.split(" - ")[0]
                c = get_connection()
                c.execute("INSERT INTO auditorias (tienda_id,fecha,auditor,calificacion_global,resultado) VALUES (?,?,?,0.0,?)",
                          (tienda_id, str(fecha_sel), auditor.strip(), resultado_sel))
                new_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]

                # Copy template items from existing farma audit (E103) if available
                template = c.execute("SELECT * FROM items_farma WHERE auditoria_id=1").fetchall()
                if template:
                    for item in template:
                        c.execute("INSERT INTO items_farma (auditoria_id,seccion_id,item,puntaje,observacion) VALUES (?,?,?,0,NULL)",
                                  (new_id, item["seccion_id"], item["item"]))
                # Copy tienda template
                template_t = c.execute("SELECT * FROM items_tienda WHERE auditoria_id=1").fetchall()
                if template_t:
                    for it in template_t:
                        c.execute("INSERT INTO items_tienda (auditoria_id,criterio,minimo,superior,meta,calificacion) VALUES (?,?,?,?,?,0)",
                                  (new_id, it["criterio"], it["minimo"], it["superior"], it["meta"]))

                for h in hall_inputs:
                    if h and ":" in h:
                        parts = h.split(":",1)
                        c.execute("INSERT INTO hallazgos (auditoria_id,proceso_afectado,hallazgo,estado) VALUES (?,?,?,'Pendiente')",
                                  (new_id, parts[0].strip(), parts[1].strip()))

                c.commit(); c.close()

                st.markdown(f"""
                <div class='success-banner'>
                  ✅ <strong>Auditoría #{new_id} creada exitosamente.</strong>
                  Selecciona la tienda <strong>{tienda_sel}</strong> en el panel lateral y elige esta auditoría para comenzar a diligenciarla.
                </div>""", unsafe_allow_html=True)
