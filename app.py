import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import os
from init_db import init_db, get_connection

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Autoinspección Locatel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

/* Main background */
.main { background-color: #f8fafc; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1a56db 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(26,86,219,0.2);
}
.header-title { color: white; font-size: 1.75rem; font-weight: 700; margin: 0; }
.header-subtitle { color: #93c5fd; font-size: 0.9rem; margin-top: 0.25rem; }
.header-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 100px;
    font-size: 0.85rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
}

/* KPI cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.blue::before { background: linear-gradient(90deg, #1a56db, #3b82f6); }
.kpi-card.green::before { background: linear-gradient(90deg, #059669, #34d399); }
.kpi-card.red::before { background: linear-gradient(90deg, #dc2626, #f87171); }
.kpi-card.amber::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2rem; font-weight: 700; color: #0f172a; line-height: 1; }
.kpi-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 0.3rem; }

/* Section tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: #64748b;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1a56db !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

/* Tables */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}
.styled-table th {
    background: #f8fafc;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #e2e8f0;
}
.styled-table td {
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    vertical-align: middle;
}
.styled-table tr:last-child td { border-bottom: none; }
.styled-table tr:hover td { background: #f8fafc; }

/* Badges */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-success { background: #dcfce7; color: #166534; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-info { background: #dbeafe; color: #1e40af; }
.badge-neutral { background: #f1f5f9; color: #475569; }

/* Cards */
.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f1f5f9;
}

/* Progress bar */
.prog-bar-wrap { background: #f1f5f9; border-radius: 100px; height: 8px; overflow: hidden; }
.prog-bar { height: 100%; border-radius: 100px; }

/* Hallazgo row */
.hallazgo-card {
    background: white;
    border: 1px solid #fee2e2;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.hallazgo-card.resolved {
    border-color: #d1fae5;
    border-left-color: #10b981;
}

/* Sidebar nav */
.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.75rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    color: #94a3b8;
    transition: all 0.15s;
    margin-bottom: 2px;
}
.nav-item:hover, .nav-item.active {
    background: rgba(59,130,246,0.1);
    color: #60a5fa;
}

/* Divider */
.divider { border: none; border-top: 1px solid #1e293b; margin: 1rem 0; }

/* Form elements */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
    font-size: 0.875rem !important;
}
.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INIT DATABASE
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1.25rem 0.75rem 0.5rem;'>
        <div style='font-size:1.1rem; font-weight:700; color:#f8fafc; letter-spacing:-0.01em;'>🏥 Locatel</div>
        <div style='font-size:0.72rem; color:#64748b; margin-top:2px; text-transform:uppercase; letter-spacing:0.08em;'>Sistema de Autoinspección</div>
    </div>
    <hr class='divider'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navegación",
        ["📊 Dashboard", "💊 Auditoría Farma", "🏪 Auditoría Tienda",
         "⚠️ Hallazgos", "🩺 Botiquín", "➕ Nueva Auditoría"],
        label_visibility="collapsed"
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    conn = get_connection()
    tiendas_df = pd.read_sql("SELECT id, nombre FROM tiendas ORDER BY id", conn)
    conn.close()
    tienda_options = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in tiendas_df.iterrows()}
    selected_label = st.selectbox("Tienda", list(tienda_options.keys()), index=2)
    selected_tienda = tienda_options[selected_label]

    conn = get_connection()
    auds = pd.read_sql(
        "SELECT id, fecha, auditor, calificacion_global, resultado FROM auditorias WHERE tienda_id=? ORDER BY fecha DESC",
        conn, params=(selected_tienda,)
    )
    conn.close()

    if len(auds) > 0:
        aud_opts = {f"{r['fecha']} — {r['auditor']}": r['id'] for _, r in auds.iterrows()}
        selected_aud_label = st.selectbox("Auditoría", list(aud_opts.keys()))
        selected_aud_id = aud_opts[selected_aud_label]
    else:
        st.info("Sin auditorías registradas")
        selected_aud_id = None

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def score_badge(score, total=None):
    if total:
        pct = score / total if total > 0 else 0
    else:
        pct = score
    if pct >= 0.95:
        return f"<span class='badge badge-success'>✓ {pct:.0%}</span>"
    elif pct >= 0.85:
        return f"<span class='badge badge-warning'>⚡ {pct:.0%}</span>"
    else:
        return f"<span class='badge badge-danger'>✗ {pct:.0%}</span>"

def gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        title={'text': title, 'font': {'size': 13, 'family': 'Inter', 'color': '#475569'}},
        number={'suffix': '%', 'font': {'size': 28, 'family': 'Inter', 'color': '#0f172a'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': '#e2e8f0',
                     'tickfont': {'size': 9, 'color': '#94a3b8'}},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': '#f8fafc',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 85], 'color': '#fee2e2'},
                {'range': [85, 95], 'color': '#fef3c7'},
                {'range': [95, 100], 'color': '#dcfce7'},
            ],
            'threshold': {'line': {'color': color, 'width': 3}, 'thickness': 0.8, 'value': value * 100}
        }
    ))
    fig.update_layout(
        height=200, margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor='white', plot_bgcolor='white', font_family='Inter'
    )
    return fig

# ─────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────
if page == "📊 Dashboard":
    if selected_aud_id is None:
        st.info("Selecciona una auditoría en el panel lateral para comenzar.")
        st.stop()

    conn = get_connection()
    aud = conn.execute("SELECT * FROM auditorias WHERE id=?", (selected_aud_id,)).fetchone()
    items_farma = pd.read_sql("SELECT * FROM items_farma WHERE auditoria_id=?", conn, params=(selected_aud_id,))
    items_tienda = pd.read_sql("SELECT * FROM items_tienda WHERE auditoria_id=?", conn, params=(selected_aud_id,))
    hallazgos = pd.read_sql("SELECT * FROM hallazgos WHERE auditoria_id=?", conn, params=(selected_aud_id,))
    conn.close()

    tienda_name = selected_label.split(" - ", 1)[1] if " - " in selected_label else selected_label
    audit_date = datetime.strptime(aud['fecha'], '%Y-%m-%d').strftime('%d %b %Y')
    resultado = aud['resultado'] or "N/A"
    calificacion = aud['calificacion_global'] or 0

    # Header
    resultado_color = "#10b981" if resultado == "FAVORABLE" else "#ef4444"
    st.markdown(f"""
    <div class='header-banner'>
        <div>
            <div class='header-title'>Autoinspección — {tienda_name}</div>
            <div class='header-subtitle'>📅 {audit_date} &nbsp;·&nbsp; 👤 {aud['auditor']}</div>
        </div>
        <div style='display:flex; gap:0.75rem; align-items:center;'>
            <div class='header-badge' style='background:rgba(255,255,255,0.08); border-color:rgba(255,255,255,0.15);'>
                📋 ID #{selected_aud_id}
            </div>
            <div class='header-badge' style='background:{resultado_color}33; border-color:{resultado_color}66; color:white;'>
                {resultado}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    total_farma = len(items_farma)
    cumplidos_farma = int(items_farma['puntaje'].sum()) if total_farma > 0 else 0
    pct_farma = cumplidos_farma / total_farma if total_farma > 0 else 0

    pct_tienda_raw = items_tienda['calificacion'].mean() / 10 if len(items_tienda) > 0 else 0

    hallazgos_pendientes = len(hallazgos[hallazgos['estado'] == 'Pendiente']) if len(hallazgos) > 0 else 0
    hallazgos_resueltos = len(hallazgos[hallazgos['estado'] == 'Resuelto']) if len(hallazgos) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='kpi-card blue'>
            <div class='kpi-label'>Calificación Global</div>
            <div class='kpi-value'>{calificacion:.0%}</div>
            <div class='kpi-sub'>Score consolidado</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='kpi-card green'>
            <div class='kpi-label'>Cumplimiento Farma</div>
            <div class='kpi-value'>{pct_farma:.0%}</div>
            <div class='kpi-sub'>{cumplidos_farma} / {total_farma} ítems</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='kpi-card amber'>
            <div class='kpi-label'>Hallazgos Pendientes</div>
            <div class='kpi-value'>{hallazgos_pendientes}</div>
            <div class='kpi-sub'>{hallazgos_resueltos} resueltos</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        pct_tienda_disp = items_tienda['calificacion'].mean() if len(items_tienda) > 0 else 0
        st.markdown(f"""
        <div class='kpi-card {'green' if pct_tienda_disp >= 9 else 'red'}'>
            <div class='kpi-label'>Prom. Tienda</div>
            <div class='kpi-value'>{pct_tienda_disp:.1f}</div>
            <div class='kpi-sub'>Meta: 9.5 / 10</div>
        </div>""", unsafe_allow_html=True)

    # Charts row
    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        st.markdown("<div class='card'><div class='card-title'>Cumplimiento Farma</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(pct_farma, "Farmacia", "#1a56db"), use_container_width=True, key="g_farma")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("<div class='card'><div class='card-title'>Calificación Tienda</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(pct_tienda_raw, "Tienda", "#059669"), use_container_width=True, key="g_tienda")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g3:
        st.markdown("<div class='card'><div class='card-title'>Score Global</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(calificacion, "Global", "#d97706"), use_container_width=True, key="g_global")
        st.markdown("</div>", unsafe_allow_html=True)

    # Cumplimiento por sección + Tienda items
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("<div class='card'><div class='card-title'>Cumplimiento por Sección Farma</div>", unsafe_allow_html=True)
        if len(items_farma) > 0:
            conn2 = get_connection()
            secs = pd.read_sql("SELECT * FROM secciones_farma", conn2)
            conn2.close()
            sec_data = []
            for _, sec in secs.iterrows():
                sec_items = items_farma[items_farma['seccion_id'] == sec['id']]
                if len(sec_items) > 0:
                    cum = int(sec_items['puntaje'].sum())
                    tot = len(sec_items)
                    sec_data.append({'Sección': sec['nombre'], 'Cumplidos': cum, 'Total': tot, 'Pct': cum/tot})

            if sec_data:
                fig_bar = px.bar(
                    sec_data, x='Pct', y='Sección', orientation='h',
                    text=[f"{d['Cumplidos']}/{d['Total']}" for d in sec_data],
                    color='Pct', color_continuous_scale=['#fee2e2', '#fef3c7', '#dcfce7'],
                    range_color=[0.8, 1.0]
                )
                fig_bar.update_traces(textposition='inside', textfont_size=11)
                fig_bar.update_layout(
                    height=240, margin=dict(t=5, b=5, l=5, r=5),
                    paper_bgcolor='white', plot_bgcolor='white',
                    showlegend=False, coloraxis_showscale=False,
                    xaxis=dict(tickformat='.0%', range=[0, 1], gridcolor='#f1f5f9', showline=False),
                    yaxis=dict(gridcolor='#f1f5f9', tickfont_size=11),
                    font_family='Inter'
                )
                st.plotly_chart(fig_bar, use_container_width=True, key="bar_sec")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='card'><div class='card-title'>Criterios de Tienda</div>", unsafe_allow_html=True)
        if len(items_tienda) > 0:
            for _, row in items_tienda.iterrows():
                cal = row['calificacion']
                meta = row['meta']
                pct_cal = cal / 10
                color = "#10b981" if cal >= row['superior'] else ("#f59e0b" if cal >= row['minimo'] else "#ef4444")
                st.markdown(f"""
                <div style='margin-bottom:0.6rem;'>
                    <div style='display:flex; justify-content:space-between; font-size:0.78rem; color:#475569; margin-bottom:3px;'>
                        <span>{row['criterio']}</span>
                        <span style='font-weight:600; color:{color};'>{cal}</span>
                    </div>
                    <div class='prog-bar-wrap'>
                        <div class='prog-bar' style='width:{pct_cal*100:.0f}%; background:{color};'></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Hallazgos summary
    if len(hallazgos) > 0:
        st.markdown("<div class='card'><div class='card-title'>⚠️ Hallazgos Activos</div>", unsafe_allow_html=True)
        for _, h in hallazgos.iterrows():
            css_class = "resolved" if h['estado'] == 'Resuelto' else "hallazgo-card"
            st.markdown(f"""
            <div class='{css_class}'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div>
                        <div style='font-weight:600; font-size:0.85rem; color:#0f172a;'>{h['proceso_afectado']}</div>
                        <div style='color:#64748b; font-size:0.8rem; margin-top:2px;'>{h['hallazgo']}</div>
                    </div>
                    <span class='badge {"badge-success" if h["estado"]=="Resuelto" else "badge-danger"}'>{h['estado']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: AUDITORÍA FARMA
# ─────────────────────────────────────────────
elif page == "💊 Auditoría Farma":
    if selected_aud_id is None:
        st.info("Selecciona una auditoría.")
        st.stop()

    conn = get_connection()
    items_farma = pd.read_sql("""
        SELECT if.*, sf.nombre as seccion_nombre
        FROM items_farma if
        JOIN secciones_farma sf ON sf.id = if.seccion_id
        WHERE if.auditoria_id = ?
        ORDER BY if.seccion_id, if.id
    """, conn, params=(selected_aud_id,))
    conn.close()

    st.markdown(f"<div class='header-banner'><div><div class='header-title'>💊 Auditoría Farmacéutica</div><div class='header-subtitle'>Revisión detallada de ítems por sección</div></div></div>", unsafe_allow_html=True)

    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        search = st.text_input("🔍 Buscar ítem", placeholder="Escribe para filtrar...")
    with filter_col2:
        filter_estado = st.selectbox("Filtrar por", ["Todos", "Cumplidos", "Incumplidos"])

    if search:
        items_farma = items_farma[items_farma['item'].str.contains(search, case=False, na=False)]
    if filter_estado == "Cumplidos":
        items_farma = items_farma[items_farma['puntaje'] == 1]
    elif filter_estado == "Incumplidos":
        items_farma = items_farma[items_farma['puntaje'] == 0]

    secciones = items_farma['seccion_nombre'].unique()

    for seccion in secciones:
        sec_items = items_farma[items_farma['seccion_nombre'] == seccion]
        cum = int(sec_items['puntaje'].sum())
        tot = len(sec_items)
        pct = cum / tot if tot > 0 else 0

        color = "#10b981" if pct >= 0.95 else ("#f59e0b" if pct >= 0.85 else "#ef4444")
        with st.expander(f"📁 {seccion}  —  {cum}/{tot} ítems  ({pct:.0%})", expanded=True):
            st.markdown("""<table class='styled-table'>
            <thead><tr>
                <th style='width:50%'>Ítem</th>
                <th style='width:12%'>Estado</th>
                <th>Observación</th>
                <th style='width:8%'>Acción</th>
            </tr></thead><tbody>""", unsafe_allow_html=True)

            for _, row in sec_items.iterrows():
                badge = "<span class='badge badge-success'>✓ OK</span>" if row['puntaje'] == 1 else "<span class='badge badge-danger'>✗ No cumple</span>"
                obs = row['observacion'] if pd.notna(row['observacion']) else "—"
                st.markdown(f"""
                <tr>
                    <td style='font-size:0.82rem;'>{row['item']}</td>
                    <td>{badge}</td>
                    <td style='color:#64748b; font-size:0.8rem;'>{obs}</td>
                    <td><span class='badge badge-info' style='cursor:pointer;'>✏️</span></td>
                </tr>""", unsafe_allow_html=True)

            st.markdown("</tbody></table>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='display:flex; justify-content:flex-end; margin-top:0.75rem;'>
                <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.5rem 1rem; font-size:0.8rem; color:#475569;'>
                    Cumplimiento: <strong style='color:{color};'>{pct:.1%}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: AUDITORÍA TIENDA
# ─────────────────────────────────────────────
elif page == "🏪 Auditoría Tienda":
    if selected_aud_id is None:
        st.info("Selecciona una auditoría.")
        st.stop()

    conn = get_connection()
    items = pd.read_sql("SELECT * FROM items_tienda WHERE auditoria_id=?", conn, params=(selected_aud_id,))
    conn.close()

    st.markdown("<div class='header-banner'><div><div class='header-title'>🏪 Auditoría de Tienda</div><div class='header-subtitle'>Criterios operativos y de presentación</div></div></div>", unsafe_allow_html=True)

    if len(items) == 0:
        st.info("Sin datos de tienda para esta auditoría.")
        st.stop()

    avg = items['calificacion'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='kpi-card blue'><div class='kpi-label'>Promedio General</div><div class='kpi-value'>{avg:.1f}</div><div class='kpi-sub'>Meta: 9.5 — Mínimo: 9.0</div></div>", unsafe_allow_html=True)
    with col2:
        sobre_meta = len(items[items['calificacion'] >= items['superior']])
        st.markdown(f"<div class='kpi-card green'><div class='kpi-label'>Sobre Meta</div><div class='kpi-value'>{sobre_meta}</div><div class='kpi-sub'>de {len(items)} criterios</div></div>", unsafe_allow_html=True)
    with col3:
        bajo_min = len(items[items['calificacion'] < items['minimo']])
        st.markdown(f"<div class='kpi-card red'><div class='kpi-label'>Bajo Mínimo</div><div class='kpi-value'>{bajo_min}</div><div class='kpi-sub'>requieren atención</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure()
    for _, row in items.iterrows():
        cal = row['calificacion']
        color = "#10b981" if cal >= row['superior'] else ("#f59e0b" if cal >= row['minimo'] else "#ef4444")
        fig.add_trace(go.Bar(
            name=row['criterio'], x=[row['criterio']], y=[cal],
            marker_color=color, showlegend=False,
            text=[f"{cal}"], textposition='outside',
        ))

    fig.add_hline(y=9.5, line_dash="dash", line_color="#1a56db", annotation_text="Meta Superior", annotation_font_size=11)
    fig.add_hline(y=9.0, line_dash="dot", line_color="#f59e0b", annotation_text="Mínimo", annotation_font_size=11)
    fig.update_layout(
        height=380, margin=dict(t=20, b=10, l=5, r=5),
        paper_bgcolor='white', plot_bgcolor='white',
        xaxis=dict(tickangle=-35, tickfont_size=11, gridcolor='#f1f5f9'),
        yaxis=dict(range=[0, 11], gridcolor='#f1f5f9', tickfont_size=11),
        font_family='Inter', bargap=0.3
    )
    st.markdown("<div class='card'><div class='card-title'>Calificaciones por Criterio</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key="tienda_bar")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><div class='card-title'>Detalle de Criterios</div>", unsafe_allow_html=True)
    st.markdown("""<table class='styled-table'>
    <thead><tr><th>Criterio</th><th>Mínimo</th><th>Superior</th><th>Meta</th><th>Calificación</th><th>Estado</th></tr></thead><tbody>""",
    unsafe_allow_html=True)
    for _, row in items.iterrows():
        cal = row['calificacion']
        if cal >= row['superior']:
            badge = "<span class='badge badge-success'>✓ Superior</span>"
        elif cal >= row['minimo']:
            badge = "<span class='badge badge-warning'>⚡ Aceptable</span>"
        else:
            badge = "<span class='badge badge-danger'>✗ Bajo mínimo</span>"
        st.markdown(f"""<tr>
            <td style='font-weight:500;'>{row['criterio']}</td>
            <td>{row['minimo']}</td><td>{row['superior']}</td><td>{row['meta']}</td>
            <td style='font-weight:700;'>{cal}</td><td>{badge}</td>
        </tr>""", unsafe_allow_html=True)
    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: HALLAZGOS
# ─────────────────────────────────────────────
elif page == "⚠️ Hallazgos":
    if selected_aud_id is None:
        st.info("Selecciona una auditoría.")
        st.stop()

    st.markdown("<div class='header-banner'><div><div class='header-title'>⚠️ Gestión de Hallazgos</div><div class='header-subtitle'>Seguimiento y resolución de no conformidades</div></div></div>", unsafe_allow_html=True)

    conn = get_connection()
    hallazgos = pd.read_sql("SELECT * FROM hallazgos WHERE auditoria_id=? ORDER BY id", conn, params=(selected_aud_id,))
    conn.close()

    col_add, _ = st.columns([1, 2])
    with col_add:
        if st.button("➕ Agregar Hallazgo", use_container_width=True):
            st.session_state['show_add_hallazgo'] = True

    if st.session_state.get('show_add_hallazgo'):
        with st.form("add_hallazgo"):
            st.markdown("**Nuevo Hallazgo**")
            proc = st.text_input("Proceso Afectado")
            hall = st.text_area("Descripción del Hallazgo")
            obs = st.text_area("Observaciones (opcional)")
            submitted = st.form_submit_button("Guardar")
            if submitted and proc and hall:
                conn = get_connection()
                conn.execute("INSERT INTO hallazgos (auditoria_id, proceso_afectado, hallazgo, observaciones, estado) VALUES (?,?,?,?,'Pendiente')",
                             (selected_aud_id, proc, hall, obs if obs else None))
                conn.commit()
                conn.close()
                st.session_state['show_add_hallazgo'] = False
                st.rerun()

    if len(hallazgos) == 0:
        st.success("✅ No hay hallazgos registrados para esta auditoría.")
    else:
        pend = hallazgos[hallazgos['estado'] == 'Pendiente']
        res = hallazgos[hallazgos['estado'] == 'Resuelto']
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='kpi-card red'><div class='kpi-label'>Pendientes</div><div class='kpi-value'>{len(pend)}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card green'><div class='kpi-label'>Resueltos</div><div class='kpi-value'>{len(res)}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for _, h in hallazgos.iterrows():
            is_resolved = h['estado'] == 'Resuelto'
            border_color = "#10b981" if is_resolved else "#ef4444"
            bg_color = "#f0fdf4" if is_resolved else "#fff5f5"
            with st.container():
                st.markdown(f"""
                <div style='background:{bg_color}; border:1px solid {border_color}; border-left:4px solid {border_color};
                     border-radius:10px; padding:1.1rem 1.25rem; margin-bottom:0.75rem;'>
                    <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;'>
                        <span style='font-weight:700; color:#0f172a; font-size:0.9rem;'>#{h["id"]} · {h["proceso_afectado"]}</span>
                        <span class='badge {"badge-success" if is_resolved else "badge-danger"}'>{h["estado"]}</span>
                    </div>
                    <div style='color:#475569; font-size:0.83rem; margin-bottom:0.25rem;'>{h["hallazgo"]}</div>
                    {f'<div style="color:#94a3b8; font-size:0.78rem; font-style:italic;">{h["observaciones"]}</div>' if pd.notna(h["observaciones"]) else ""}
                </div>""", unsafe_allow_html=True)

                if not is_resolved:
                    if st.button(f"✅ Marcar como resuelto", key=f"resolve_{h['id']}"):
                        conn = get_connection()
                        conn.execute("UPDATE hallazgos SET estado='Resuelto' WHERE id=?", (h['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

# ─────────────────────────────────────────────
# PAGE: BOTIQUÍN
# ─────────────────────────────────────────────
elif page == "🩺 Botiquín":
    if selected_aud_id is None:
        st.info("Selecciona una auditoría.")
        st.stop()

    conn = get_connection()
    botiquin = pd.read_sql("SELECT * FROM botiquin WHERE auditoria_id=?", conn, params=(selected_aud_id,))
    conn.close()

    st.markdown("<div class='header-banner'><div><div class='header-title'>🩺 Elementos de Botiquín</div><div class='header-subtitle'>Control de insumos de primeros auxilios · Res. 0705/2007</div></div></div>", unsafe_allow_html=True)

    if len(botiquin) == 0:
        st.info("Sin registros de botiquín.")
        st.stop()

    today = date.today()
    def vencimiento_status(fecha_str):
        if not fecha_str or pd.isna(fecha_str):
            return "N/A", "badge-neutral"
        try:
            d = datetime.strptime(str(fecha_str), '%Y-%m-%d').date()
            diff = (d - today).days
            if diff < 0: return f"Vencido ({abs(diff)}d)", "badge-danger"
            elif diff <= 90: return f"⚠️ {diff}d", "badge-warning"
            else: return d.strftime('%d/%m/%Y'), "badge-success"
        except:
            return str(fecha_str), "badge-neutral"

    vencidos = sum(1 for _, r in botiquin.iterrows() if pd.notna(r['fecha_vencimiento']) and datetime.strptime(str(r['fecha_vencimiento']), '%Y-%m-%d').date() < today)
    proximos = sum(1 for _, r in botiquin.iterrows() if pd.notna(r['fecha_vencimiento']) and 0 <= (datetime.strptime(str(r['fecha_vencimiento']), '%Y-%m-%d').date() - today).days <= 90)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='kpi-card blue'><div class='kpi-label'>Total Elementos</div><div class='kpi-value'>{len(botiquin)}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card {'red' if vencidos > 0 else 'green'}'><div class='kpi-label'>Vencidos</div><div class='kpi-value'>{vencidos}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi-card amber'><div class='kpi-label'>Próximos a Vencer</div><div class='kpi-value'>{proximos}</div><div class='kpi-sub'>Dentro de 90 días</div></div>", unsafe_allow_html=True)

    st.markdown("<br><div class='card'><div class='card-title'>Inventario de Elementos</div>", unsafe_allow_html=True)
    st.markdown("""<table class='styled-table'>
    <thead><tr><th>#</th><th>Elemento</th><th>Unidades</th><th>Vencimiento</th><th>Estado</th></tr></thead><tbody>""",
    unsafe_allow_html=True)
    for i, (_, row) in enumerate(botiquin.iterrows(), 1):
        label, badge_cls = vencimiento_status(row['fecha_vencimiento'])
        st.markdown(f"""<tr>
            <td style='color:#94a3b8; font-size:0.78rem;'>{i:02d}</td>
            <td style='font-weight:500;'>{row['item']}</td>
            <td style='color:#64748b;'>{row['unidades'] or '—'}</td>
            <td style='color:#475569; font-size:0.82rem;'>{row['fecha_vencimiento'] or '—'}</td>
            <td><span class='badge {badge_cls}'>{label}</span></td>
        </tr>""", unsafe_allow_html=True)
    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: NUEVA AUDITORÍA
# ─────────────────────────────────────────────
elif page == "➕ Nueva Auditoría":
    st.markdown("<div class='header-banner'><div><div class='header-title'>➕ Registrar Nueva Auditoría</div><div class='header-subtitle'>Crea un nuevo registro de autoinspección</div></div></div>", unsafe_allow_html=True)

    conn = get_connection()
    tiendas = pd.read_sql("SELECT * FROM tiendas ORDER BY id", conn)
    conn.close()

    with st.form("nueva_auditoria", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tienda_sel = st.selectbox("Tienda", [f"{r['id']} - {r['nombre']}" for _, r in tiendas.iterrows()])
            auditor = st.text_input("Nombre del Auditor")
        with c2:
            fecha = st.date_input("Fecha de Auditoría", value=date.today())
            resultado_sel = st.selectbox("Resultado", ["FAVORABLE", "DESFAVORABLE", "CONDICIONADO"])

        calif = st.slider("Calificación Global", 0.0, 1.0, 0.90, 0.01, format="%.0%%")

        st.markdown("---")
        st.markdown("**Hallazgos Iniciales** (opcional)")
        hall1 = st.text_area("Hallazgo 1 — Proceso afectado : Descripción", placeholder="Ej: Bomberos : Pendiente visita de renovación")
        hall2 = st.text_area("Hallazgo 2", placeholder="Opcional...")

        submitted = st.form_submit_button("💾 Guardar Auditoría", use_container_width=True)
        if submitted:
            if not auditor:
                st.error("El nombre del auditor es requerido.")
            else:
                tienda_id = tienda_sel.split(" - ")[0]
                conn = get_connection()
                conn.execute("""INSERT INTO auditorias (tienda_id, fecha, auditor, calificacion_global, resultado)
                                VALUES (?,?,?,?,?)""",
                             (tienda_id, str(fecha), auditor, calif, resultado_sel))
                new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                for hall_raw in [hall1, hall2]:
                    if hall_raw and ":" in hall_raw:
                        parts = hall_raw.split(":", 1)
                        conn.execute("INSERT INTO hallazgos (auditoria_id, proceso_afectado, hallazgo, estado) VALUES (?,?,?,'Pendiente')",
                                     (new_id, parts[0].strip(), parts[1].strip()))

                conn.commit()
                conn.close()
                st.success(f"✅ Auditoría #{new_id} registrada correctamente. Selecciónala en el panel lateral.")
