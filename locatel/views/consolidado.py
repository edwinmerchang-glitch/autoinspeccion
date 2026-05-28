"""
views/consolidado.py
--------------------
Dashboard consolidado multi-tienda. Visible para todos los roles,
pero solo admins pueden hacer clic para ir a editar una auditoría.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from db.queries import get_consolidado, get_tiendas
from components.ui import pct_color
from auth import is_admin


def _badge(resultado: str) -> str:
    colors = {
        "FAVORABLE":    ("rgba(16,185,129,.15)", "#34d399", "rgba(16,185,129,.35)"),
        "DESFAVORABLE": ("rgba(239,68,68,.15)",  "#f87171", "rgba(239,68,68,.35)"),
        "CONDICIONADO": ("rgba(245,158,11,.15)", "#fbbf24", "rgba(245,158,11,.35)"),
    }
    bg, color, border = colors.get(resultado, ("rgba(100,116,139,.1)", "#94a3b8", "rgba(100,116,139,.2)"))
    return f"<span style='background:{bg};color:{color};border:1px solid {border};padding:.2rem .65rem;border-radius:100px;font-size:.71rem;font-weight:700;'>{resultado or 'N/D'}</span>"


def render() -> None:
    # ── Filtros ───────────────────────────────────────────────────────────────
    tiendas_df = get_tiendas()
    tienda_opts = ["Todas las tiendas"] + [f"{r['id']} - {r['nombre']}" for _, r in tiendas_df.iterrows()]

    st.markdown("""
    <div class='page-header'>
      <div>
        <div class='ph-title'>📈 Consolidado de Auditorías</div>
        <div class='ph-sub'>Vista global de todas las tiendas · Filtra y compara resultados.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([2, 1.5, 1.5, 1])
    with f1:
        tienda_sel = st.selectbox("Tienda", tienda_opts, label_visibility="collapsed")
    with f2:
        resultado_sel = st.selectbox("Resultado", ["Todos", "FAVORABLE", "DESFAVORABLE", "CONDICIONADO"], label_visibility="collapsed")
    with f3:
        orden_sel = st.selectbox("Ordenar por", ["Más reciente", "Calificación ↓", "Calificación ↑", "Tienda"], label_visibility="collapsed")
    with f4:
        buscar = st.text_input("Buscar", placeholder="Auditor...", label_visibility="collapsed")

    # ── Cargar datos ──────────────────────────────────────────────────────────
    tienda_id = None if tienda_sel == "Todas las tiendas" else tienda_sel.split(" - ")[0]
    df = get_consolidado(tienda_id)

    if len(df) == 0:
        st.markdown("<div class='info-banner'>ℹ️ No hay auditorías registradas aún.</div>", unsafe_allow_html=True)
        return

    # Filtros adicionales
    if resultado_sel != "Todos":
        df = df[df["resultado"] == resultado_sel]
    if buscar:
        df = df[df["auditor"].str.contains(buscar, case=False, na=False)]

    # Ordenar
    if orden_sel == "Calificación ↓":
        df = df.sort_values("calificacion_global", ascending=False)
    elif orden_sel == "Calificación ↑":
        df = df.sort_values("calificacion_global", ascending=True)
    elif orden_sel == "Tienda":
        df = df.sort_values("tienda_nombre")

    # ── KPIs globales ─────────────────────────────────────────────────────────
    total     = len(df)
    favorables = len(df[df["resultado"] == "FAVORABLE"])
    avg_global = df["calificacion_global"].mean() if total else 0
    hall_total = int(df["hall_pend"].sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"<div class='kpi blue'><div class='kpi-lbl'>Total Auditorías</div><div class='kpi-val'>{total}</div><div class='kpi-sub'>registradas</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='kpi green'><div class='kpi-lbl'>Favorables</div><div class='kpi-val val-green'>{favorables}</div><div class='kpi-sub'>{favorables/total:.0%} del total</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='kpi {'green' if avg_global>=0.95 else 'amber' if avg_global>=0.85 else 'red'}'><div class='kpi-lbl'>Promedio Global</div><div class='kpi-val'>{avg_global:.0%}</div><div class='kpi-sub'>todas las tiendas</div></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='kpi {'red' if hall_total else 'green'}'><div class='kpi-lbl'>Hallazgos Pendientes</div><div class='kpi-val {'val-red' if hall_total else 'val-green'}'>{hall_total}</div><div class='kpi-sub'>sin resolver</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabla de auditorías ───────────────────────────────────────────────────
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:grid;grid-template-columns:2fr 1fr 1.2fr 1fr 1fr 1fr 1fr;gap:.5rem;
         padding:.4rem 1rem;font-size:.68rem;font-weight:700;color:#94a3b8;
         text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #f1f5f9;margin-bottom:.25rem;'>
      <span>Tienda</span><span>Fecha</span><span>Auditor</span>
      <span>Farma</span><span>Tienda</span><span>Global</span><span>Resultado</span>
    </div>""", unsafe_allow_html=True)

    for _, row in df.iterrows():
        pf   = row["cumple_farma"] / row["total_farma"] if row["total_farma"] else 0
        pt   = row["avg_tienda"] / 10
        glob = row["calificacion_global"] or 0
        fecha_fmt = datetime.strptime(str(row["fecha"]), "%Y-%m-%d").strftime("%d/%m/%Y") if row["fecha"] else "-"

        col_pf   = pct_color(pf)
        col_pt   = pct_color(pt)
        col_glob = pct_color(glob)

        hall_html = (
            f"<span style='background:rgba(239,68,68,.1);color:#ef4444;font-size:.68rem;"
            f"font-weight:700;padding:.1rem .4rem;border-radius:6px;margin-left:.4rem;'>"
            f"⚠️ {int(row['hall_pend'])}</span>"
        ) if row["hall_pend"] > 0 else ""

        st.markdown(f"""
        <div style='display:grid;grid-template-columns:2fr 1fr 1.2fr 1fr 1fr 1fr 1fr;gap:.5rem;
             align-items:center;padding:.6rem 1rem;border-radius:8px;
             border:1px solid #f1f5f9;margin-bottom:.3rem;background:#fafbfc;
             transition:background .15s;'>
          <div>
            <div style='font-size:.82rem;font-weight:600;color:#0f172a;'>{row['tienda_nombre']}</div>
            <div style='font-size:.7rem;color:#94a3b8;'>ID #{row['id']}{hall_html}</div>
          </div>
          <div style='font-size:.78rem;color:#475569;'>{fecha_fmt}</div>
          <div style='font-size:.78rem;color:#475569;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{row['auditor']}</div>
          <div style='font-size:.82rem;font-weight:700;color:{col_pf};'>{pf:.0%}</div>
          <div style='font-size:.82rem;font-weight:700;color:{col_pt};'>{row['avg_tienda']:.1f}</div>
          <div style='font-size:.82rem;font-weight:700;color:{col_glob};'>{glob:.0%}</div>
          <div>{_badge(row['resultado'])}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Comparativo por tienda ────────────────────────────────────────────────
    st.markdown("<div class='card'><div class='card-hd'>Comparativo por Tienda</div>", unsafe_allow_html=True)
    resumen = (df.groupby("tienda_nombre")
               .agg(auditorias=("id", "count"), avg_global=("calificacion_global", "mean"))
               .reset_index()
               .sort_values("avg_global", ascending=False))

    for _, r in resumen.iterrows():
        p = r["avg_global"]
        bar_color = "#1D9E75" if p >= 0.95 else ("#EF9F27" if p >= 0.85 else "#E24B4A")
        txt_color = "#085041" if p >= 0.95 else ("#854F0B" if p >= 0.85 else "#791F1F")
        bg_color  = "#E1F5EE" if p >= 0.95 else ("#FAEEDA" if p >= 0.85 else "#FCEBEB")
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px;'>
          <div style='font-size:.78rem;color:#475569;min-width:200px;max-width:200px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' title='{r["tienda_nombre"]}'>
            {r["tienda_nombre"]}
          </div>
          <div style='flex:1;height:22px;background:{bg_color};border-radius:5px;overflow:hidden;'>
            <div style='width:{p*100:.0f}%;height:100%;background:{bar_color};border-radius:5px;
                        display:flex;align-items:center;justify-content:flex-end;padding-right:8px;
                        font-size:.72rem;font-weight:600;color:white;min-width:40px;'>
              {r["auditorias"]:.0f} aud.
            </div>
          </div>
          <div style='font-size:.78rem;font-weight:700;color:{txt_color};min-width:40px;text-align:right;'>{p:.0%}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
