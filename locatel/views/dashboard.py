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

    def kpi(col, label, value, sub, color):
        vc = {"blue":"#1a56db","green":"#059669","red":"#dc2626","amber":"#b45309","purple":"#7c3aed"}.get(color,"#1a56db")
        col.markdown(
            "<div style='background:white;border-radius:14px;padding:1rem 1.1rem;"
            "border:1px solid #e8eef5;box-shadow:0 2px 8px rgba(0,0,0,.05);"
            "border-top:3px solid " + vc + ";'>"
            "<p style='margin:0 0 4px;font-size:.62rem;font-weight:700;"
            "color:#94a3b8;text-transform:uppercase;letter-spacing:.07em;'>" + label + "</p>"
            "<p style='margin:0 0 3px;font-size:1.55rem;font-weight:800;"
            "color:" + vc + ";line-height:1.1;'>" + value + "</p>"
            "<p style='margin:0;font-size:.72rem;color:#94a3b8;'>" + sub + "</p>"
            "</div>",
            unsafe_allow_html=True
        )

    fc = "#059669" if pf>=0.95 else ("#b45309" if pf>=0.85 else "#dc2626")
    fl = "Muy favorable" if pf>=0.95 else ("Aceptable" if pf>=0.85 else "Desfavorable")
    tc2 = "#059669" if pt>=0.95 else ("#b45309" if pt>=0.85 else "#dc2626")
    tl = "Muy favorable" if pt>=0.95 else ("Aceptable" if pt>=0.85 else "Bajo meta")
    rc = "#059669" if resultado=="FAVORABLE" else ("#b45309" if resultado=="CONDICIONADO" else "#dc2626")

    k1,k2,k3,k4,k5 = st.columns(5)
    cc = "#059669" if calif>=0.95 else ("#b45309" if calif>=0.85 else "#dc2626")
    kpi(k1, "Calificación Global", f"{calif:.0%}", "Score consolidado", "blue")
    kpi(k2, "Cumplimiento Farma",  f"{pf:.0%}",   f"{cf}/{tf} ítems · {fl}", "green")
    kpi(k3, "Promedio Tienda",     f"{avg_t:.1f}", f"Meta 9.5 · {tl}", "purple")
    kpi(k4, "Hallazgos Pendientes",str(h_pend),    "sin resolver" if h_pend else "Todo resuelto", "red" if h_pend else "green")
    kpi(k5, "Estado",              resultado,       audit_date, "green" if resultado=="FAVORABLE" else ("amber" if resultado=="CONDICIONADO" else "red"))

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

    import plotly.graph_objects as go

    with cl:
        secs = get_secciones_farma()
        nombres, valores, colores, textos = [], [], [], []
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"] == s["id"]]
            if not len(si): continue
            cum = int(si["puntaje"].sum()); tot = len(si); p = cum / tot
            nombres.append(s["nombre"][:35] + "…" if len(s["nombre"]) > 35 else s["nombre"])
            valores.append(round(p * 100, 1))
            colores.append("#10b981" if p >= 0.95 else ("#f59e0b" if p >= 0.85 else "#ef4444"))
            textos.append(f"{cum}/{tot} · {p:.0%}")

        fig_f = go.Figure(go.Bar(
            x=valores, y=nombres, orientation="h",
            marker_color=colores,
            text=textos, textposition="inside",
            textfont=dict(color="white", size=11, family="Inter"),
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        fig_f.update_layout(
            title=dict(text="📋 Cumplimiento por Sección", font=dict(size=13, color="#64748b"), x=0),
            xaxis=dict(range=[0, 105], showgrid=True, gridcolor="#f1f5f9",
                       ticksuffix="%", tickfont=dict(size=10), zeroline=False),
            yaxis=dict(tickfont=dict(size=11, color="#334155"), automargin=True),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=20, t=40, b=10),
            height=max(200, len(nombres) * 52),
            showlegend=False,
            shapes=[
                dict(type="line", x0=95, x1=95, y0=-0.5, y1=len(nombres)-0.5,
                     line=dict(color="#10b981", width=1.5, dash="dot")),
                dict(type="line", x0=85, x1=85, y0=-0.5, y1=len(nombres)-0.5,
                     line=dict(color="#f59e0b", width=1.5, dash="dot")),
            ],
            annotations=[
                dict(x=95, y=len(nombres)-0.3, text="95%", showarrow=False,
                     font=dict(size=9, color="#10b981"), xanchor="center"),
                dict(x=85, y=len(nombres)-0.3, text="85%", showarrow=False,
                     font=dict(size=9, color="#f59e0b"), xanchor="center"),
            ],
        )
        st.plotly_chart(fig_f, use_container_width=True, config={"displayModeBar": False})

    with cr:
        criterios, califs, colores_t, textos_t = [], [], [], []
        for _, row in items_t.iterrows():
            cal = row["calificacion"]
            criterios.append(row["criterio"][:28] + "…" if len(row["criterio"]) > 28 else row["criterio"])
            califs.append(float(cal))
            colores_t.append("#10b981" if cal >= row["superior"] else ("#f59e0b" if cal >= row["minimo"] else "#ef4444"))
            lbl = "Superior" if cal >= row["superior"] else ("Aceptable" if cal >= row["minimo"] else "Bajo mín.")
            textos_t.append(f"{cal} · {lbl}")

        fig_t = go.Figure(go.Bar(
            x=califs, y=criterios, orientation="h",
            marker_color=colores_t,
            text=textos_t, textposition="inside",
            textfont=dict(color="white", size=10, family="Inter"),
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        fig_t.update_layout(
            title=dict(text="🏪 Criterios de Tienda", font=dict(size=13, color="#64748b"), x=0),
            xaxis=dict(range=[0, 10.5], showgrid=True, gridcolor="#f1f5f9",
                       tickfont=dict(size=10), zeroline=False),
            yaxis=dict(tickfont=dict(size=10, color="#334155"), automargin=True),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=20, t=40, b=10),
            height=max(200, len(criterios) * 48),
            showlegend=False,
            shapes=[
                dict(type="line", x0=9.5, x1=9.5, y0=-0.5, y1=len(criterios)-0.5,
                     line=dict(color="#10b981", width=1.5, dash="dot")),
                dict(type="line", x0=9.0, x1=9.0, y0=-0.5, y1=len(criterios)-0.5,
                     line=dict(color="#f59e0b", width=1.5, dash="dot")),
            ],
            annotations=[
                dict(x=9.5, y=len(criterios)-0.3, text="Sup 9.5", showarrow=False,
                     font=dict(size=9, color="#10b981"), xanchor="center"),
                dict(x=9.0, y=len(criterios)-0.3, text="Mín 9.0", showarrow=False,
                     font=dict(size=9, color="#f59e0b"), xanchor="center"),
            ],
        )
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

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
