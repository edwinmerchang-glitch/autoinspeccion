"""
app.py — Autoinspección Locatel
Navegación: sidebar nativo de Streamlit + CSS hamburguesa personalizado.
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


st.set_page_config(
    page_title="Autoinspección Locatel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "main.css"
base_css = css_path.read_text()

hamburger_css = """
/* Ocultar el botón nativo de colapsar que aparece DENTRO del sidebar */
[data-testid="stSidebarCollapseButton"] { display: none !important; }

/* Reestilizar el botón nativo de ABRIR sidebar (la flecha que queda en pantalla)
   para que parezca un botón hamburguesa */
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 12px !important;
    left: 12px !important;
    z-index: 999999 !important;
    width: 46px !important;
    height: 46px !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,.45) !important;
    border: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: transform .15s, box-shadow .15s !important;
    color: transparent !important;  /* ocultar la flecha original */
    overflow: hidden !important;
}
[data-testid="collapsedControl"]:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 6px 24px rgba(37,99,235,.6) !important;
}

/* Dibujar las 3 líneas hamburguesa con pseudo-elementos */
[data-testid="collapsedControl"]::before {
    content: '';
    position: absolute;
    width: 20px;
    height: 2px;
    background: white;
    border-radius: 2px;
    box-shadow: 0 -6px 0 white, 0 6px 0 white;
    pointer-events: none;
}

/* Ocultar el SVG/ícono original dentro del botón */
[data-testid="collapsedControl"] svg { display: none !important; }

/* Dar espacio al contenido para que no quede debajo del botón */
.block-container { padding-top: 4rem !important; }
"""

st.markdown(f"<style>{base_css}\n{hamburger_css}</style>", unsafe_allow_html=True)

# ── Init DB ────────────────────────────────────────────────────────────────────
init_db()

# ── Estado de navegación ───────────────────────────────────────────────────────
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
        st.markdown("<div style='font-size:.78rem;color:#3b5270;padding:.5rem 0;'>Sin auditorías</div>",
                    unsafe_allow_html=True)
        sel_aud_id = None

    st.markdown(
        f"<hr style='border:none;border-top:1px solid #1a2744;margin:.75rem 0;'>"
        f"<div style='font-size:.62rem;color:#2d4a6b;padding:.25rem;font-weight:600;'>📅 {today_str}</div>",
        unsafe_allow_html=True,
    )


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
