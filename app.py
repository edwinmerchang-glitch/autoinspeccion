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

/* ─ Layout ─ */
.main { background: #f0f4f8; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1440px; }

/* ─ Sidebar ─ */
[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 2px;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    background: transparent;
    border-radius: 8px;
    padding: 0.55rem 0.85rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(56,139,253,0.1) !important;
    border-color: rgba(56,139,253,0.2);
}
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
    background: rgba(56,139,253,0.15) !important;
    border-color: rgba(56,139,253,0.4) !important;
    color: #58a6ff !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #111827 !important;
    border-color: #1e2d45 !important;
    color: #c8d6e5 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4b6080 !important;
    font-weight: 600;
}

/* ─ Header Banner ─ */
.page-header {
    background: linear-gradient(135deg, #0d1b2e 0%, #0f2847 40%, #0e3a6e 100%);
    border-radius: 14px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(10,25,60,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
    border: 1px solid rgba(56,139,253,0.15);
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: -40%; right: -5%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(56,139,253,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.ph-title { color: #f0f6ff; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; }
.ph-sub { color: #6b8fba; font-size: 0.85rem; margin-top: 4px; }
.ph-badges { display: flex; gap: 0.6rem; flex-wrap: wrap; align-items: center; }
.ph-badge {
    padding: 0.35rem 0.9rem;
    border-radius: 100px;
    font-size: 0.78rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.12);
    color: #c8d6e5;
    background: rgba(255,255,255,0.06);
}
.ph-badge.favorable { background: rgba(16,185,129,0.15); border-color: rgba(16,185,129,0.35); color: #34d399; }
.ph-badge.desfavorable { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.35); color: #f87171; }

/* ─ KPI Cards ─ */
.kpi {
    background: white;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #e8eef5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    position: relative; overflow: hidden;
}
.kpi::after {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    border-radius:14px 14px 0 0;
}
.kpi.blue::after  { background: linear-gradient(90deg,#1a56db,#60a5fa); }
.kpi.green::after { background: linear-gradient(90deg,#059669,#34d399); }
.kpi.red::after   { background: linear-gradient(90deg,#dc2626,#f87171); }
.kpi.amber::after { background: linear-gradient(90deg,#b45309,#fbbf24); }
.kpi.purple::after{ background: linear-gradient(90deg,#7c3aed,#a78bfa); }
.kpi-lbl { font-size:0.7rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.07em; margin-bottom:.5rem; }
.kpi-val { font-size:2.1rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-0.02em; }
.kpi-sub { font-size:0.76rem; color:#94a3b8; margin-top:4px; }
.kpi-icon { position:absolute; right:1.25rem; top:50%; transform:translateY(-50%); font-size:2rem; opacity:0.12; }

/* ─ Cards ─ */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #e8eef5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 1.25rem;
}
.card-hd {
    font-size: 0.78rem; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: .07em;
    margin-bottom: 1rem; padding-bottom: .75rem;
    border-bottom: 1px solid #f1f5f9;
    display: flex; align-items: center; justify-content: space-between;
}

/* ─ Audit Item Row ─ */
.audit-item-row {
    display: grid;
    grid-template-columns: 1fr 140px 1fr;
    gap: .75rem;
    align-items: start;
    padding: .75rem 1rem;
    border-radius: 10px;
    border: 1px solid #f1f5f9;
    margin-bottom: .5rem;
    background: #fafbfc;
    transition: border-color .15s, box-shadow .15s;
}
.audit-item-row:hover { border-color: #c7d7f0; box-shadow: 0 2px 8px rgba(26,86,219,.06); }
.audit-item-row.fail  { border-color: #fecdd3; background: #fff8f8; }
.audit-item-row.pass  { border-color: #bbf7d0; background: #f8fff9; }
.item-name { font-size:.82rem; font-weight:500; color:#334155; line-height:1.4; }
.item-obs  { font-size:.78rem; color:#94a3b8; font-style:italic; margin-top:3px; }

/* ─ Badges ─ */
.badge {
    display:inline-flex; align-items:center; gap:.25rem;
    padding:.22rem .65rem; border-radius:100px;
    font-size:.71rem; font-weight:700; letter-spacing:.02em;
}
.b-ok   { background:#dcfce7; color:#15803d; }
.b-fail { background:#fee2e2; color:#b91c1c; }
.b-warn { background:#fef3c7; color:#92400e; }
.b-info { background:#dbeafe; color:#1d4ed8; }
.b-gray { background:#f1f5f9; color:#475569; }
.b-fav  { background:#d1fae5; color:#065f46; }
.b-desfav{ background:#fee2e2; color:#991b1b; }
.b-cond { background:#fef3c7; color:#78350f; }

/* ─ Progress ─ */
.pb-wrap { background:#f1f5f9; border-radius:100px; height:7px; overflow:hidden; }
.pb-fill { height:100%; border-radius:100px; transition:width .4s ease; }

/* ─ Section Expander ─ */
.stExpander { border:1px solid #e2e8f0 !important; border-radius:12px !important; overflow:hidden !important; margin-bottom:.75rem !important; }
.stExpander summary { font-weight:600 !important; font-size:.875rem !important; }

/* ─ Form Inputs ─ */
div[data-testid="stForm"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.75rem;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    border-radius: 9px !important;
    border-color: #d1dde8 !important;
    font-size: .875rem !important;
    background: #f8fafc !important;
    transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.12) !important;
    background: white !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {
    font-size: .75rem !important; font-weight: 600 !important;
    color: #64748b !important; text-transform: uppercase;
    letter-spacing: .05em !important;
}

/* ─ Buttons ─ */
.stButton > button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: .875rem !important;
    transition: all .15s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(37,99,235,.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,.4) !important;
}

/* ─ Download button ─ */
.stDownloadButton > button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
    background: white !important;
    border: 1.5px solid #e2e8f0 !important;
    color: #475569 !important;
    display: flex; align-items: center; gap: .4rem;
}
.stDownloadButton > button:hover {
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
    background: #eff6ff !important;
}

/* ─ Radio toggle (pass/fail) ─ */
div[data-testid="stRadio"] > label { display:none !important; }
div[data-testid="stRadio"] > div {
    display:flex; flex-direction:row; gap:.4rem;
    background:#f1f5f9; border-radius:8px; padding:3px;
}
div[data-testid="stRadio"] > div > label {
    flex:1; text-align:center !important;
    padding:.35rem .6rem !important;
    border-radius:6px !important;
    font-size:.8rem !important; font-weight:600 !important;
    cursor:pointer !important;
    border:1px solid transparent !important;
    margin:0 !important;
}
div[data-testid="stRadio"] > div > label[aria-checked="true"] {
    background:white !important;
    box-shadow:0 1px 4px rgba(0,0,0,.1) !important;
}

/* ─ Tabs ─ */
.stTabs [data-baseweb="tab-list"] {
    background:#f1f5f9; border-radius:10px; padding:3px; gap:0; border:none;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px; padding:.45rem 1.2rem;
    font-weight:500; font-size:.85rem; color:#64748b;
    background:transparent; border:none;
}
.stTabs [aria-selected="true"] {
    background:white !important; color:#1d4ed8 !important;
    box-shadow:0 1px 4px rgba(0,0,0,.1);
}

/* ─ Divider ─ */
.sdiv { border:none; border-top:1px solid #1e2d45; margin:.75rem 0; }

/* ─ Success/info banners ─ */
.info-banner {
    background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px;
    padding:1rem 1.25rem; color:#1e40af; font-size:.85rem;
    display:flex; align-items:center; gap:.75rem; margin-bottom:1rem;
}
.success-banner {
    background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;
    padding:1rem 1.25rem; color:#15803d; font-size:.85rem;
    display:flex; align-items:center; gap:.75rem; margin-bottom:1rem;
}

/* ─ Form section label ─ */
.form-section-label {
    font-size:.7rem; font-weight:700; color:#94a3b8;
    text-transform:uppercase; letter-spacing:.08em;
    margin: 1.25rem 0 .75rem; padding-top:.75rem;
    border-top:1px solid #f1f5f9;
}

/* ─ Hide Streamlit chrome ─ */
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
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

def gauge(value, title, color="#1a56db"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(value*100, 1),
        title={"text": title, "font": {"size": 12, "family":"Inter", "color":"#64748b"}},
        number={"suffix":"%","font":{"size":28,"family":"Inter","color":"#0f172a"}},
        gauge={
            "axis":{"range":[0,100],"tickwidth":0,"tickfont":{"size":9,"color":"#94a3b8"}},
            "bar":{"color":color,"thickness":0.28},
            "bgcolor":"#f8fafc","borderwidth":0,
            "steps":[
                {"range":[0,85],"color":"#fef2f2"},
                {"range":[85,95],"color":"#fefce8"},
                {"range":[95,100],"color":"#f0fdf4"},
            ],
            "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":value*100}
        }
    ))
    fig.update_layout(height=190,margin=dict(t=40,b=5,l=15,r=15),
                      paper_bgcolor="white",plot_bgcolor="white",font_family="Inter")
    return fig

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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.5rem 1rem .75rem;'>
      <div style='font-size:1.15rem;font-weight:800;color:#f0f6ff;letter-spacing:-.02em;'>🏥 Locatel</div>
      <div style='font-size:.68rem;color:#3b5270;margin-top:3px;text-transform:uppercase;letter-spacing:.1em;font-weight:600;'>Autoinspección · v2.0</div>
    </div>
    <hr class='sdiv'>
    """, unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard",
        "💊  Auditoría Farma",
        "🏪  Auditoría Tienda",
        "⚠️  Hallazgos",
        "🩺  Botiquín",
        "➕  Nueva Auditoría",
    ], label_visibility="collapsed")

    st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)

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
        st.info("Sin auditorías")
        sel_aud_id = None

    st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.68rem;color:#3b5270;padding:.5rem 0;'>Hoy: {date.today().strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

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

    k1,k2,k3,k4,k5 = st.columns(5)
    for col, color, label, val, sub in [
        (k1,"blue","Calificación Global",f"{calif:.0%}","Score consolidado"),
        (k2,"green","Cumplimiento Farma",f"{pf:.0%}",f"{cf}/{tf} ítems"),
        (k3,"purple","Promedio Tienda",f"{avg_t:.1f}","Meta: 9.5 / 10"),
        (k4,"amber","Hallazgos Pendientes",str(h_pend),"sin resolver"),
        (k5,"red" if h_pend>3 else "green","Estado",resultado,audit_date),
    ]:
        col.markdown(f"<div class='kpi {color}'><div class='kpi-lbl'>{label}</div><div class='kpi-val'>{val}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauges
    g1,g2,g3 = st.columns(3)
    with g1:
        st.markdown("<div class='card'><div class='card-hd'>Farmacia</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge(pf,"Cumplimiento Farma",pct_color(pf)), use_container_width=True, key="gf")
        st.markdown("</div>", unsafe_allow_html=True)
    with g2:
        st.markdown("<div class='card'><div class='card-hd'>Tienda</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge(pt,"Criterios Tienda",pct_color(pt)), use_container_width=True, key="gt")
        st.markdown("</div>", unsafe_allow_html=True)
    with g3:
        st.markdown("<div class='card'><div class='card-hd'>Global</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge(calif,"Score Global",pct_color(calif)), use_container_width=True, key="gg")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts
    cl, cr = st.columns([1.3,1])
    with cl:
        st.markdown("<div class='card'><div class='card-hd'>Cumplimiento por Sección</div>", unsafe_allow_html=True)
        conn2 = get_connection()
        secs = pd.read_sql("SELECT * FROM secciones_farma", conn2); conn2.close()
        sec_data = []
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"]==s["id"]]
            if len(si): sec_data.append({"Sección":s["nombre"],"Cum":int(si["puntaje"].sum()),"Tot":len(si),"Pct":int(si["puntaje"].sum())/len(si)})
        if sec_data:
            fig_b = px.bar(sec_data, x="Pct", y="Sección", orientation="h",
                           text=[f"{d['Cum']}/{d['Tot']}" for d in sec_data],
                           color="Pct", color_continuous_scale=["#fef2f2","#fefce8","#f0fdf4"], range_color=[0.8,1])
            fig_b.update_traces(textposition="inside", textfont_size=11)
            fig_b.update_layout(height=240, margin=dict(t=5,b=5,l=5,r=5), paper_bgcolor="white", plot_bgcolor="white",
                                showlegend=False, coloraxis_showscale=False,
                                xaxis=dict(tickformat=".0%",range=[0,1],gridcolor="#f1f5f9",showline=False),
                                yaxis=dict(gridcolor="#f1f5f9",tickfont_size=11), font_family="Inter")
            st.plotly_chart(fig_b, use_container_width=True, key="secbar")
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

    fig = go.Figure()
    for _, row in items_t2.iterrows():
        cal = row["calificacion"]
        color = "#10b981" if cal>=row["superior"] else ("#f59e0b" if cal>=row["minimo"] else "#ef4444")
        fig.add_trace(go.Bar(x=[row["criterio"]], y=[cal], marker_color=color,
                             showlegend=False, text=[f"{cal}"], textposition="outside"))
    fig.add_hline(y=9.5, line_dash="dash", line_color="#3b82f6", annotation_text="Meta")
    fig.add_hline(y=9.0, line_dash="dot", line_color="#f59e0b", annotation_text="Mínimo")
    fig.update_layout(height=300, margin=dict(t=20,b=5,l=5,r=5), paper_bgcolor="white", plot_bgcolor="white",
                      xaxis=dict(tickangle=-30,tickfont_size=10,gridcolor="#f1f5f9"),
                      yaxis=dict(range=[0,11],gridcolor="#f1f5f9"), font_family="Inter", bargap=0.3)
    st.markdown("<div class='card'><div class='card-hd'>Gráfico de Calificaciones</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key="tbar")
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

    if len(hall)==0:
        st.markdown("<div class='success-banner'>✅ No hay hallazgos registrados para esta auditoría.</div>", unsafe_allow_html=True)
    else:
        for _, h in hall.iterrows():
            ok = h["estado"]=="Resuelto"
            bc = "#10b981" if ok else "#ef4444"; bg = "#f0fdf4" if ok else "#fff8f8"
            hcol1, hcol2 = st.columns([4,1])
            with hcol1:
                st.markdown(f"""
                <div style='background:{bg};border:1px solid {"#bbf7d0" if ok else "#fecdd3"};border-left:4px solid {bc};
                     border-radius:10px;padding:1rem 1.25rem;margin-bottom:.5rem;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <span style='font-weight:700;font-size:.88rem;color:#0f172a;'>#{h["id"]} · {h["proceso_afectado"]}</span>
                    <span class='badge {"b-ok" if ok else "b-fail"}'>{h["estado"]}</span>
                  </div>
                  <div style='color:#475569;font-size:.81rem;margin-top:.35rem;'>{h["hallazgo"]}</div>
                  {f'<div style="color:#94a3b8;font-size:.76rem;margin-top:.2rem;font-style:italic;">{h["observaciones"]}</div>' if pd.notna(h.get("observaciones")) and h["observaciones"] else ""}
                </div>""", unsafe_allow_html=True)
            with hcol2:
                if not ok:
                    if st.button("✅ Resolver", key=f"res_{h['id']}", use_container_width=True):
                        c = get_connection()
                        c.execute("UPDATE hallazgos SET estado='Resuelto' WHERE id=?", (h["id"],))
                        c.commit(); c.close(); st.rerun()
                else:
                    if st.button("↩️ Reabrir", key=f"reopen_{h['id']}", use_container_width=True):
                        c = get_connection()
                        c.execute("UPDATE hallazgos SET estado='Pendiente' WHERE id=?", (h["id"],))
                        c.commit(); c.close(); st.rerun()


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

    st.markdown("<div class='card'><div class='card-hd'>Inventario</div>", unsafe_allow_html=True)
    for i,(_, row) in enumerate(boti.iterrows(),1):
        lbl, bcls, diff = venc_status(row["fecha_vencimiento"])
        bg = "#fff8f8" if diff<0 else ("#fffbeb" if diff<=90 else "white")
        st.markdown(f"""
        <div style='display:grid;grid-template-columns:2rem 2fr 1fr 1fr 1fr;gap:.75rem;align-items:center;
             padding:.65rem 1rem;border-radius:9px;background:{bg};border:1px solid #f1f5f9;margin-bottom:.35rem;'>
          <span style='color:#94a3b8;font-size:.76rem;font-weight:600;'>{i:02d}</span>
          <span style='font-weight:500;font-size:.83rem;color:#0f172a;'>{row['item']}</span>
          <span style='color:#64748b;font-size:.8rem;'>{row['unidades'] or '—'}</span>
          <span style='color:#64748b;font-size:.78rem;'>{row['fecha_vencimiento'] or '—'}</span>
          <span><span class='badge {bcls}'>{lbl}</span></span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


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
