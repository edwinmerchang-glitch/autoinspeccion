"""
views/dashboard.py — Dashboard moderno
"""

import streamlit as st
from datetime import datetime

from db.queries import get_auditoria, get_items_farma, get_items_tienda, get_hallazgos, get_botiquin, get_secciones_farma
from components.ui import gauge_html, kpi_html, pct_color, val_color_class
from components.exports import generate_excel_report


def render(sel_aud_id: int, sel_label: str) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona o crea una auditoría en el panel lateral.</div>", unsafe_allow_html=True)
        st.stop()

    aud     = get_auditoria(sel_aud_id)
    items_f = get_items_farma(sel_aud_id)
    items_t = get_items_tienda(sel_aud_id)
    hall    = get_hallazgos(sel_aud_id)
    boti    = get_botiquin(sel_aud_id)

    tienda_name = sel_label.split(" - ", 1)[1] if " - " in sel_label else sel_label
    audit_date  = datetime.strptime(aud["fecha"], "%Y-%m-%d").strftime("%d %b %Y")
    resultado   = aud["resultado"] or "N/D"
    calif       = aud["calificacion_global"] or 0
    res_cls     = "favorable" if resultado == "FAVORABLE" else ("desfavorable" if resultado == "DESFAVORABLE" else "")

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>📊 {tienda_name}</div>
        <div class='ph-sub'>📅 {audit_date} &nbsp;·&nbsp; 👤 {aud['auditor']}</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>ID #{sel_aud_id}</span>
        <span class='ph-badge {res_cls}'>{resultado}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Descargas ─────────────────────────────────────────────────────────────
    dc1, dc2, _ = st.columns([1, 1, 3])
    with dc1:
        xl = generate_excel_report(aud, items_f, items_t, hall, boti, tienda_name)
        st.download_button("⬇️ Descargar Excel", xl,
            file_name=f"auditoria_{tienda_name.replace(' ','_')}_{aud['fecha']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)
    with dc2:
        csv_data = items_f[["seccion_nombre","item","puntaje","observacion"]].to_csv(index=False)
        st.download_button("⬇️ Descargar CSV", csv_data,
            file_name=f"items_{aud['fecha']}.csv", mime="text/csv", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    tf     = len(items_f)
    cf     = int(items_f["puntaje"].sum()) if tf else 0
    pf     = cf / tf if tf else 0
    avg_t  = items_t["calificacion"].mean() if len(items_t) else 0
    pt     = avg_t / 10 if len(items_t) else 0
    h_pend = len(hall[hall["estado"] == "Pendiente"]) if len(hall) else 0

    # CSS para estilizar st.metric como tarjetas modernas
    st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e8eef5;
        border-radius: 16px;
        padding: 1.1rem 1.25rem 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,.05);
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1a56db, #60a5fa);
        border-radius: 16px 16px 0 0;
    }
    [data-testid="stMetricLabel"] {
        font-size: .62rem !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
        letter-spacing: .07em !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -.02em !important;
        line-height: 1.1 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: .72rem !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)

    # Calificación global
    k1.metric(
        label="📊 Calificación Global",
        value=f"{calif:.0%}",
        delta="Score consolidado",
    )

    # Cumplimiento farma
    delta_f = "✅ Favorable" if pf >= 0.95 else ("⚠️ Aceptable" if pf >= 0.85 else "❌ Desfavorable")
    k2.metric(
        label="💊 Cumplimiento Farma",
        value=f"{pf:.0%}",
        delta=f"{cf}/{tf} ítems · {delta_f}",
    )

    # Promedio tienda
    delta_t = "✅ Favorable" if pt >= 0.95 else ("⚠️ Aceptable" if pt >= 0.85 else "❌ Bajo meta")
    k3.metric(
        label="🏪 Promedio Tienda",
        value=f"{avg_t:.1f}",
        delta=f"Meta 9.5 · {delta_t}",
    )

    # Hallazgos
    k4.metric(
        label="⚠️ Hallazgos Pendientes",
        value=str(h_pend),
        delta="sin resolver" if h_pend else "Todo resuelto ✅",
        delta_color="inverse" if h_pend else "normal",
    )

    # Estado
    estado_icon = "✅" if resultado == "FAVORABLE" else ("⚠️" if resultado == "CONDICIONADO" else "❌")
    k5.metric(
        label="🏁 Estado Auditoría",
        value=resultado,
        delta=f"{estado_icon} {audit_date}",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauges ────────────────────────────────────────────────────────────────
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(gauge_html(pf,    "Farmacia", f"{cf}/{tf} ítems",        pct_color(pf)),    unsafe_allow_html=True)
    with g2:
        st.markdown(gauge_html(pt,    "Tienda",   f"Prom. {avg_t:.1f} / 10", pct_color(pt)),    unsafe_allow_html=True)
    with g3:
        st.markdown(gauge_html(calif, "Global",   resultado,                  pct_color(calif)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Secciones + Tienda ────────────────────────────────────────────────────
    cl, cr = st.columns([1.3, 1])

    with cl:
        st.markdown("**📋 Cumplimiento por Sección**")
        secs = get_secciones_farma()
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"] == s["id"]]
            if not len(si): continue
            cum = int(si["puntaje"].sum()); tot = len(si); p = cum / tot
            if p >= 0.95:   tc, lbl, icon = "normal",  "Muy favorable ✅", "🟢"
            elif p >= 0.85: tc, lbl, icon = "normal",  "Aceptable ⚠️",     "🟡"
            else:           tc, lbl, icon = "normal",  "Desfavorable ❌",   "🔴"

            with st.container():
                ca, cb = st.columns([4, 1])
                ca.markdown(f"{icon} **{s['nombre']}**  \n{lbl}")
                cb.markdown(f"### {p:.0%}")
                cb.caption(f"{cum}/{tot}")
                st.progress(p)
                st.markdown("---")

    with cr:
        st.markdown("**🏪 Criterios de Tienda**")
        for _, row in items_t.iterrows():
            cal = row["calificacion"]
            if cal >= row["superior"]:   lbl, icon = "Superior ✅",    "🟢"
            elif cal >= row["minimo"]:   lbl, icon = "Aceptable ⚠️",   "🟡"
            else:                        lbl, icon = "Bajo mínimo ❌",  "🔴"

            with st.container():
                ca, cb = st.columns([4, 1])
                ca.markdown(f"{icon} **{row['criterio']}**  \n{lbl}")
                cb.markdown(f"### {cal}")
                ca.caption(f"Mín {row['minimo']} · Meta {row['meta']} · Sup {row['superior']}")
                st.progress(cal / 10)
                st.markdown("---")

    # ── Hallazgos ─────────────────────────────────────────────────────────────
    if len(hall):
        st.markdown("""
        <div style='background:white;border-radius:16px;border:1px solid #e8eef5;
                    box-shadow:0 2px 12px rgba(0,0,0,.04);padding:1.5rem;'>
          <div style='font-size:.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                      letter-spacing:.08em;margin-bottom:1rem;padding-bottom:.75rem;
                      border-bottom:1px solid #f1f5f9;'>⚠️ Hallazgos Activos</div>
        """, unsafe_allow_html=True)
        for _, h in hall.iterrows():
            ok = h["estado"] == "Resuelto"
            bc = "#10b981" if ok else "#ef4444"
            bg = "#f0fdf4" if ok else "#fff5f5"
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {bc}22;border-left:3px solid {bc};
                 border-radius:10px;padding:.85rem 1.1rem;margin-bottom:.5rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='font-weight:600;font-size:.83rem;color:#0f172a;'>{h['proceso_afectado']}</span>
                <span class='badge {"b-ok" if ok else "b-fail"}'>{h['estado']}</span>
              </div>
              <div style='color:#64748b;font-size:.79rem;margin-top:3px;'>{h['hallazgo']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
