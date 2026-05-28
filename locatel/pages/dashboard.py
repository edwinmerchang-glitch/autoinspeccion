"""
pages/dashboard.py
------------------
Página de Dashboard: KPIs, gauges, gráficos de sección y hallazgos activos.
"""

import streamlit as st
from datetime import datetime

from db.queries import get_auditoria, get_items_farma, get_items_tienda, get_hallazgos, get_botiquin, get_secciones_farma
from components.ui import gauge_html, kpi_html, pct_color, val_color_class, page_header
from components.exports import generate_excel_report


def render(sel_aud_id: int, sel_label: str) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona o crea una auditoría en el panel lateral para comenzar.</div>", unsafe_allow_html=True)
        st.stop()

    aud       = get_auditoria(sel_aud_id)
    items_f   = get_items_farma(sel_aud_id)
    items_t   = get_items_tienda(sel_aud_id)
    hall      = get_hallazgos(sel_aud_id)
    boti      = get_botiquin(sel_aud_id)

    tienda_name = sel_label.split(" - ", 1)[1]
    audit_date  = datetime.strptime(aud["fecha"], "%Y-%m-%d").strftime("%d %b %Y")
    resultado   = aud["resultado"] or "N/D"
    calif       = aud["calificacion_global"] or 0
    res_cls     = "favorable" if resultado == "FAVORABLE" else ("desfavorable" if resultado == "DESFAVORABLE" else "")

    # ── Header ────────────────────────────────────────────────────────────────
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

    # ── Descargas ─────────────────────────────────────────────────────────────
    dc1, dc2, _ = st.columns([1, 1, 3])
    with dc1:
        xl = generate_excel_report(aud, items_f, items_t, hall, boti, tienda_name)
        st.download_button(
            "⬇️ Descargar Excel", xl,
            file_name=f"auditoria_{tienda_name.replace(' ', '_')}_{aud['fecha']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with dc2:
        csv_data = items_f[["seccion_nombre", "item", "puntaje", "observacion"]].to_csv(index=False)
        st.download_button(
            "⬇️ Descargar CSV", csv_data,
            file_name=f"items_{aud['fecha']}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── KPIs ──────────────────────────────────────────────────────────────────
    tf    = len(items_f)
    cf    = int(items_f["puntaje"].sum()) if tf else 0
    pf    = cf / tf if tf else 0
    avg_t = items_t["calificacion"].mean() if len(items_t) else 0
    pt    = avg_t / 10 if len(items_t) else 0
    h_pend = len(hall[hall["estado"] == "Pendiente"]) if len(hall) else 0

    res_val_color = "val-green" if resultado == "FAVORABLE" else ("val-amber" if resultado == "CONDICIONADO" else "val-red")
    res_accent    = "green"     if resultado == "FAVORABLE" else ("amber"     if resultado == "CONDICIONADO" else "red")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(kpi_html("Calificación Global",  f"{calif:.0%}",    "Score consolidado",     "blue",   val_color_class(calif)), unsafe_allow_html=True)
    k2.markdown(kpi_html("Cumplimiento Farma",   f"{pf:.0%}",       f"{cf}/{tf} ítems",      "green",  val_color_class(pf)),    unsafe_allow_html=True)
    k3.markdown(kpi_html("Promedio Tienda",       f"{avg_t:.1f}",   "Meta: 9.5 / 10",        "purple", val_color_class(pt)),    unsafe_allow_html=True)
    k4.markdown(kpi_html("Hallazgos Pendientes", str(h_pend),       "sin resolver",          "red" if h_pend else "green", "val-red" if h_pend else "val-green"), unsafe_allow_html=True)
    k5.markdown(kpi_html("Estado",               resultado,         audit_date,              res_accent, res_val_color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauges ────────────────────────────────────────────────────────────────
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(gauge_html(pf,    "Farmacia", f"{cf}/{tf} ítems",        pct_color(pf)),    unsafe_allow_html=True)
    with g2:
        st.markdown(gauge_html(pt,    "Tienda",   f"Prom. {avg_t:.1f} / 10", pct_color(pt)),    unsafe_allow_html=True)
    with g3:
        st.markdown(gauge_html(calif, "Global",   resultado,                  pct_color(calif)), unsafe_allow_html=True)

    # ── Gráfico por sección ───────────────────────────────────────────────────
    cl, cr = st.columns([1.3, 1])
    with cl:
        st.markdown("<div class='card'><div class='card-hd'>Cumplimiento por Sección</div>", unsafe_allow_html=True)
        secs = get_secciones_farma()
        sec_data = []
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"] == s["id"]]
            if len(si):
                cum = int(si["puntaje"].sum()); tot = len(si); pct = cum / tot
                sec_data.append({"seccion": s["nombre"], "cum": cum, "tot": tot, "pct": pct})

        for d in sec_data:
            p = d["pct"]
            bar_color = "#1D9E75" if p >= 0.95 else ("#EF9F27" if p >= 0.85 else "#E24B4A")
            txt_color = "#085041" if p >= 0.95 else ("#854F0B" if p >= 0.85 else "#791F1F")
            bg_color  = "#E1F5EE" if p >= 0.95 else ("#FAEEDA" if p >= 0.85 else "#FCEBEB")
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
              <div style='font-size:.78rem;color:#475569;min-width:220px;max-width:220px;
                          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' title='{d["seccion"]}'>
                {d["seccion"]}
              </div>
              <div style='flex:1;height:22px;background:{bg_color};border-radius:5px;overflow:hidden;'>
                <div style='width:{p*100:.0f}%;height:100%;background:{bar_color};border-radius:5px;
                            display:flex;align-items:center;justify-content:flex-end;padding-right:8px;
                            font-size:.72rem;font-weight:600;color:white;min-width:40px;'>
                  {d["cum"]}/{d["tot"]}
                </div>
              </div>
              <div style='font-size:.78rem;font-weight:700;color:{txt_color};min-width:36px;text-align:right;'>{p:.0%}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='display:flex;gap:14px;margin-top:10px;padding-top:10px;
                    border-top:1px solid #f1f5f9;font-size:.72rem;color:#94a3b8;flex-wrap:wrap;'>
          <span><span style='width:9px;height:9px;border-radius:2px;background:#1D9E75;display:inline-block;margin-right:4px;'></span>≥ 95% · Muy favorable</span>
          <span><span style='width:9px;height:9px;border-radius:2px;background:#EF9F27;display:inline-block;margin-right:4px;'></span>85–94% · Aceptable</span>
          <span><span style='width:9px;height:9px;border-radius:2px;background:#E24B4A;display:inline-block;margin-right:4px;'></span>&lt; 85% · Desfavorable</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cr:
        st.markdown("<div class='card'><div class='card-hd'>Criterios de Tienda</div>", unsafe_allow_html=True)
        for _, row in items_t.iterrows():
            cal = row["calificacion"]
            color = "#10b981" if cal >= row["superior"] else ("#f59e0b" if cal >= row["minimo"] else "#ef4444")
            st.markdown(f"""
            <div style='margin-bottom:.55rem;'>
              <div style='display:flex;justify-content:space-between;font-size:.77rem;color:#475569;margin-bottom:3px;'>
                <span>{row['criterio']}</span>
                <span style='font-weight:700;color:{color};'>{cal}</span>
              </div>
              <div class='pb-wrap'><div class='pb-fill' style='width:{cal/10*100:.0f}%;background:{color};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Hallazgos activos ─────────────────────────────────────────────────────
    if len(hall):
        st.markdown("<div class='card'><div class='card-hd'>⚠️ Hallazgos Activos</div>", unsafe_allow_html=True)
        for _, h in hall.iterrows():
            ok = h["estado"] == "Resuelto"
            bc = "#10b981" if ok else "#ef4444"
            bg = "#f0fdf4" if ok else "#fff5f5"
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
