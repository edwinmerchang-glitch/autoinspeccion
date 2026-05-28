"""
app.py
------
Punto de entrada de la aplicación. Solo hace tres cosas:
  1. Configura la página y carga el CSS.
  2. Renderiza el sidebar con navegación y selectores.
  3. Delega el render al módulo de página correspondiente.

Para agregar una nueva página:
  1. Crea pages/mi_pagina.py con una función render(...)
  2. Agrega la entrada en NAV_ITEMS
  3. Agrega el elif en el bloque de routing al final
"""

import streamlit as st
from datetime import date
from pathlib import Path

from init_db import init_db
from db.queries import get_tiendas, get_auditorias
import pages.dashboard       as pg_dashboard
import pages.farma           as pg_farma
import pages.tienda          as pg_tienda
import pages.hallazgos       as pg_hallazgos
import pages.botiquin        as pg_botiquin
import pages.nueva_auditoria as pg_nueva


# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Autoinspección Locatel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS desde archivo externo ──────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "main.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Init DB ────────────────────────────────────────────────────────────────────
init_db()

# ── Navegación ─────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("📊", "Dashboard",        "📊  Dashboard"),
    ("💊", "Auditoría Farma",  "💊  Auditoría Farma"),
    ("🏪", "Auditoría Tienda", "🏪  Auditoría Tienda"),
    ("⚠️", "Hallazgos",        "⚠️  Hallazgos"),
    ("🩺", "Botiquín",         "🩺  Botiquín"),
    ("➕", "Nueva Auditoría",  "➕  Nueva Auditoría"),
]

if "page" not in st.session_state:
    st.session_state["page"] = "📊  Dashboard"

page      = st.session_state["page"]
today_str = date.today().strftime("%d/%m/%Y")

# ── Sidebar (solo selectores de tienda/auditoría) ─────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:.75rem .25rem .5rem;'>
      <div style='font-size:1.05rem;font-weight:800;color:#f0f6ff;letter-spacing:-.02em;'>🏥 Locatel</div>
      <div style='font-size:.6rem;color:#2d4a6b;margin-top:2px;text-transform:uppercase;
                  letter-spacing:.12em;font-weight:700;'>Autoinspección · v2.0</div>
    </div>
    <hr style='border:none;border-top:1px solid #1a2744;margin:.5rem 0;'>
    <div style='font-size:.6rem;font-weight:700;color:#2d4a6b;text-transform:uppercase;
                letter-spacing:.1em;padding:.2rem .25rem .4rem;'>Configuración</div>
    """, unsafe_allow_html=True)

    tiendas_df = get_tiendas()
    t_opts     = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in tiendas_df.iterrows()}
    sel_label  = st.selectbox("Tienda", list(t_opts.keys()), index=2)
    sel_tienda = t_opts[sel_label]

    auds = get_auditorias(sel_tienda)
    if len(auds):
        a_opts        = {f"{r['fecha']}  ·  {r['auditor']}": r['id'] for _, r in auds.iterrows()}
        sel_aud_label = st.selectbox("Auditoría", list(a_opts.keys()))
        sel_aud_id    = a_opts[sel_aud_label]
    else:
        st.markdown("<div style='font-size:.78rem;color:#3b5270;padding:.5rem 0;'>Sin auditorías</div>", unsafe_allow_html=True)
        sel_aud_id = None

    st.markdown(
        f"<hr style='border:none;border-top:1px solid #1a2744;margin:.75rem 0;'>"
        f"<div style='font-size:.62rem;color:#2d4a6b;padding:.25rem;font-weight:600;'>📅 {today_str}</div>",
        unsafe_allow_html=True,
    )


# ── Menú hamburguesa flotante ──────────────────────────────────────────────────
# Construimos la lista de ítems con cuál está activo para resaltarlo
nav_items_html = ""
for icon, label, key in NAV_ITEMS:
    active_cls = "hb-item-active" if page == key else ""
    nav_items_html += f"""
    <a class='hb-item {active_cls}' href='#' onclick='navTo("{key}"); return false;'>
      <span class='hb-icon'>{icon}</span>
      <span class='hb-label'>{label}</span>
    </a>"""

st.markdown(f"""
<!-- ══ HAMBURGER MENU ══ -->
<style>
  /* Botón flotante */
  #hb-btn {{
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 99999;
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    box-shadow: 0 4px 16px rgba(37,99,235,.45);
    border: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    transition: transform .15s, box-shadow .15s;
  }}
  #hb-btn:hover {{ transform: scale(1.08); box-shadow: 0 6px 24px rgba(37,99,235,.55); }}
  #hb-btn .bar {{
    width: 20px; height: 2px;
    background: white; border-radius: 2px;
    transition: all .25s ease;
  }}
  #hb-btn.open .bar:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
  #hb-btn.open .bar:nth-child(2) {{ opacity: 0; transform: scaleX(0); }}
  #hb-btn.open .bar:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}

  /* Overlay oscuro */
  #hb-overlay {{
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,.35);
    z-index: 99997;
    backdrop-filter: blur(2px);
  }}
  #hb-overlay.visible {{ display: block; }}

  /* Panel del menú */
  #hb-panel {{
    position: fixed;
    top: 0; left: 0;
    height: 100%;
    width: 260px;
    background: #0a0f1e;
    z-index: 99998;
    transform: translateX(-100%);
    transition: transform .28s cubic-bezier(.4,0,.2,1);
    padding: 1.5rem 1rem 2rem;
    display: flex;
    flex-direction: column;
    box-shadow: 4px 0 32px rgba(0,0,0,.5);
  }}
  #hb-panel.open {{ transform: translateX(0); }}

  /* Logo dentro del panel */
  .hb-logo {{
    padding: .5rem .5rem 1rem;
    border-bottom: 1px solid #1a2744;
    margin-bottom: 1rem;
  }}
  .hb-logo-title {{ font-size: 1.05rem; font-weight: 800; color: #f0f6ff; letter-spacing: -.02em; }}
  .hb-logo-sub   {{ font-size: .6rem; color: #2d4a6b; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; margin-top: 2px; }}

  /* Ítems de navegación */
  .hb-nav-label {{
    font-size: .6rem; font-weight: 700; color: #2d4a6b;
    text-transform: uppercase; letter-spacing: .1em;
    padding: .2rem .5rem .5rem;
  }}
  .hb-item {{
    display: flex;
    align-items: center;
    gap: .75rem;
    padding: .65rem 1rem;
    border-radius: 10px;
    border: 1px solid transparent;
    text-decoration: none;
    color: #7a95b4;
    font-size: .875rem;
    font-weight: 500;
    transition: all .15s ease;
    margin-bottom: 2px;
  }}
  .hb-item:hover {{
    background: rgba(56,139,253,.1);
    border-color: rgba(56,139,253,.25);
    color: #93c5fd;
  }}
  .hb-item-active {{
    background: rgba(37,99,235,.22) !important;
    border-color: rgba(59,130,246,.55) !important;
    color: #60a5fa !important;
    font-weight: 700 !important;
  }}
  .hb-icon  {{ font-size: 1.05rem; width: 22px; text-align: center; }}
  .hb-label {{ flex: 1; }}

  /* Fecha al fondo */
  .hb-footer {{
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid #1a2744;
    font-size: .62rem;
    color: #2d4a6b;
    font-weight: 600;
    padding-left: .5rem;
  }}
</style>

<!-- Botón hamburguesa -->
<button id='hb-btn' onclick='toggleMenu()' aria-label='Menú'>
  <div class='bar'></div>
  <div class='bar'></div>
  <div class='bar'></div>
</button>

<!-- Overlay -->
<div id='hb-overlay' onclick='closeMenu()'></div>

<!-- Panel -->
<div id='hb-panel'>
  <div class='hb-logo'>
    <div class='hb-logo-title'>🏥 Locatel</div>
    <div class='hb-logo-sub'>Autoinspección · v2.0</div>
  </div>
  <div class='hb-nav-label'>Navegación</div>
  {nav_items_html}
  <div class='hb-footer'>📅 {today_str}</div>
</div>

<script>
  function toggleMenu() {{
    const btn     = document.getElementById('hb-btn');
    const panel   = document.getElementById('hb-panel');
    const overlay = document.getElementById('hb-overlay');
    btn.classList.toggle('open');
    panel.classList.toggle('open');
    overlay.classList.toggle('visible');
  }}

  function closeMenu() {{
    document.getElementById('hb-btn').classList.remove('open');
    document.getElementById('hb-panel').classList.remove('open');
    document.getElementById('hb-overlay').classList.remove('visible');
  }}

  /* Navegar a una página vía postMessage a Streamlit */
  function navTo(pageKey) {{
    closeMenu();
    // Usamos el truco de query param para forzar rerun con la página deseada
    const url = new URL(window.location.href);
    url.searchParams.set('nav', encodeURIComponent(pageKey));
    window.location.href = url.toString();
  }}

  /* Cerrar con Escape */
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeMenu();
  }});
</script>
""", unsafe_allow_html=True)

# Capturar navegación desde query param (inyectado por el menú hamburguesa)
_qp = st.query_params.get("nav", None)
if _qp and _qp != page:
    st.query_params.clear()
    st.session_state["page"] = _qp
    st.rerun()


# ── Routing ────────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    pg_dashboard.render(sel_aud_id, sel_label)

elif page == "💊  Auditoría Farma":
    pg_farma.render(sel_aud_id)

elif page == "🏪  Auditoría Tienda":
    pg_tienda.render(sel_aud_id)

elif page == "⚠️  Hallazgos":
    pg_hallazgos.render(sel_aud_id)

elif page == "🩺  Botiquín":
    pg_botiquin.render(sel_aud_id)

elif page == "➕  Nueva Auditoría":
    pg_nueva.render()
