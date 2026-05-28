"""
app.py — Autoinspección Locatel
"""

import streamlit as st
from datetime import date
from pathlib import Path

from init_db import init_db
from db.queries import get_tiendas, get_auditorias
from auth import require_login, is_admin, current_user, logout
import views.dashboard       as pg_dashboard
import views.farma           as pg_farma
import views.tienda          as pg_tienda
import views.hallazgos       as pg_hallazgos
import views.botiquin        as pg_botiquin
import views.nueva_auditoria as pg_nueva
import views.consolidado     as pg_consolidado
import views.usuarios        as pg_usuarios


st.set_page_config(
    page_title="Autoinspección Locatel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "styles" / "main.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

init_db()
require_login()

# ── Navegación según rol ───────────────────────────────────────────────────────
ADMIN_ONLY = {
    "💊  Auditoría Farma",
    "🏪  Auditoría Tienda",
    "⚠️  Hallazgos",
    "🩺  Botiquín",
    "➕  Nueva Auditoría",
    "👥  Usuarios",
}

ALL_NAV = [
    ("📈", "Consolidado",      "📈  Consolidado"),
    ("📊", "Dashboard",        "📊  Dashboard"),
    ("💊", "Auditoría Farma",  "💊  Auditoría Farma"),
    ("🏪", "Auditoría Tienda", "🏪  Auditoría Tienda"),
    ("⚠️", "Hallazgos",        "⚠️  Hallazgos"),
    ("🩺", "Botiquín",         "🩺  Botiquín"),
    ("➕", "Nueva Auditoría",  "➕  Nueva Auditoría"),
    ("👥", "Usuarios",         "👥  Usuarios"),
]

NAV_ITEMS = ALL_NAV if is_admin() else [n for n in ALL_NAV if n[2] not in ADMIN_ONLY]

if "page" not in st.session_state:
    st.session_state["page"] = "📈  Consolidado"

if not is_admin() and st.session_state["page"] in ADMIN_ONLY:
    st.session_state["page"] = "📈  Consolidado"

page      = st.session_state["page"]
today_str = date.today().strftime("%d/%m/%Y")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    role_badge = "🔑 Admin" if is_admin() else "👁️ Viewer"
    st.markdown(f"""
    <div style='padding:.75rem .25rem .25rem;'>
      <div style='font-size:1.05rem;font-weight:800;color:#f0f6ff;letter-spacing:-.02em;'>🏥 Locatel</div>
      <div style='font-size:.6rem;color:#2d4a6b;margin-top:2px;text-transform:uppercase;
                  letter-spacing:.12em;font-weight:700;'>Autoinspección · v2.0</div>
    </div>
    <div style='display:flex;align-items:center;justify-content:space-between;
                padding:.4rem .25rem .25rem;'>
      <div style='font-size:.72rem;color:#4a6a8a;font-weight:600;'>
        👤 {current_user()} &nbsp;·&nbsp; {role_badge}
      </div>
    </div>
    <hr style='border:none;border-top:1px solid #1a2744;margin:.4rem 0;'>
    """, unsafe_allow_html=True)

    if st.button("🚪 Cerrar sesión", key="logout_btn", use_container_width=True):
        logout()

    st.markdown("""
    <hr style='border:none;border-top:1px solid #1a2744;margin:.5rem 0 .25rem;'>
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

    needs_selector = page not in {"📈  Consolidado", "➕  Nueva Auditoría", "👥  Usuarios"}
    if needs_selector:
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
    else:
        sel_label  = ""
        sel_aud_id = None

    st.markdown(
        f"<hr style='border:none;border-top:1px solid #1a2744;margin:.75rem 0;'>"
        f"<div style='font-size:.62rem;color:#2d4a6b;padding:.25rem;font-weight:600;'>📅 {today_str}</div>",
        unsafe_allow_html=True,
    )

# ── Routing ────────────────────────────────────────────────────────────────────
if page == "📈  Consolidado":
    pg_consolidado.render()
elif page == "📊  Dashboard":
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
elif page == "👥  Usuarios":
    pg_usuarios.render()
