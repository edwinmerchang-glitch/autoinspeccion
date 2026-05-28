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
import streamlit.components.v1 as components

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

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:.75rem .25rem .5rem;'>
      <div style='font-size:1.05rem;font-weight:800;color:#f0f6ff;letter-spacing:-.02em;'>🏥 Locatel</div>
      <div style='font-size:.6rem;color:#2d4a6b;margin-top:2px;text-transform:uppercase;
                  letter-spacing:.12em;font-weight:700;'>Autoinspección · v2.0</div>
    </div>
    <hr style='border:none;border-top:1px solid #1a2744;margin:.5rem 0;'>
    <div style='font-size:.6rem;font-weight:700;color:#2d4a6b;text-transform:uppercase;
                letter-spacing:.1em;padding:.2rem .25rem .4rem;'>Navegación</div>
    """, unsafe_allow_html=True)

    for icon, label, key in NAV_ITEMS:
        is_active = st.session_state["page"] == key
        st.markdown(f"<div class='{'nav-active' if is_active else ''}'>", unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state["page"] = key
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <hr style='border:none;border-top:1px solid #1a2744;margin:.75rem 0 .5rem;'>
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


# ── Botón hamburguesa flotante (abre el sidebar nativo de Streamlit) ───────────
# Usamos components.html para que el JS sí se ejecute
components.html("""
<style>
  #hb {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 999999;
    width: 44px;
    height: 44px;
    border-radius: 11px;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    box-shadow: 0 4px 14px rgba(37,99,235,.5);
    border: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    transition: transform .15s, box-shadow .15s;
  }
  #hb:hover { transform: scale(1.07); box-shadow: 0 6px 20px rgba(37,99,235,.6); }
  #hb .b { width: 18px; height: 2px; background: white; border-radius: 2px; }
</style>
<button id="hb" title="Menú" onclick="openSidebar()">
  <div class="b"></div>
  <div class="b"></div>
  <div class="b"></div>
</button>
<script>
  function openSidebar() {
    // El sidebar de Streamlit tiene un botón con data-testid="collapsedControl"
    // buscamos en el documento padre (parent frame)
    try {
      const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
      if (btn) btn.click();
    } catch(e) {}
  }
</script>
""", height=70)


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
