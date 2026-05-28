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
    tf    = len(items_f)
    cf    = int(items_f["puntaje"].sum()) if tf else 0
    pf    = cf / tf if tf else 0
    avg_t = items_t["calificacion"].mean() if len(items_t) else 0
    pt    = avg_t / 10 if len(items_t) else 0
    h_pend = len(hall[hall["estado"] == "Pendiente"]) if len(hall) else 0

    res_accent = "green" if resultado == "FAVORABLE" else ("amber" if resultado == "CONDICIONADO" else "red")
    res_val    = "val-green" if resultado == "FAVORABLE" else ("val-amber" if resultado == "CONDICIONADO" else "val-red")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(kpi_html("Calificación Global", f"{calif:.0%}", "Score consolidado", "blue", val_color_class(calif)), unsafe_allow_html=True)
    k2.markdown(kpi_html("Cumplimiento Farma",  f"{pf:.0%}",   f"{cf}/{tf} ítems",  "green", val_color_class(pf)),   unsafe_allow_html=True)
    k3.markdown(kpi_html("Promedio Tienda",     f"{avg_t:.1f}","Meta: 9.5 / 10",    "purple", val_color_class(pt)),  unsafe_allow_html=True)
    k4.markdown(kpi_html("Hallazgos Pendientes", str(h_pend),  "sin resolver",      "red" if h_pend else "green", "val-red" if h_pend else "val-green"), unsafe_allow_html=True)
    k5.markdown(kpi_html("Estado", resultado, audit_date, res_accent, res_val), unsafe_allow_html=True)

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
        st.markdown("""
        <div style='background:white;border-radius:16px;border:1px solid #e8eef5;
                    box-shadow:0 2px 12px rgba(0,0,0,.04);padding:1.5rem;margin-bottom:1rem;'>
          <div style='font-size:.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                      letter-spacing:.08em;margin-bottom:1.25rem;padding-bottom:.75rem;
                      border-bottom:1px solid #f1f5f9;'>Cumplimiento por Sección</div>
        """, unsafe_allow_html=True)

        secs = get_secciones_farma()
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"] == s["id"]]
            if not len(si): continue
            cum = int(si["puntaje"].sum()); tot = len(si); p = cum / tot
            bar_color = "#10b981" if p>=0.95 else ("#f59e0b" if p>=0.85 else "#ef4444")
            txt_color = "#059669" if p>=0.95 else ("#d97706" if p>=0.85 else "#dc2626")
            bg_color  = "#f0fdf4" if p>=0.95 else ("#fffbeb" if p>=0.85 else "#fff5f5")
            st.markdown(f"""
            <div style='margin-bottom:14px;'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;'>
                <div style='font-size:.78rem;color:#475569;font-weight:500;max-width:220px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' title='{s["nombre"]}'>
                  {s["nombre"]}
                </div>
                <div style='display:flex;align-items:center;gap:8px;'>
                  <span style='font-size:.72rem;color:#94a3b8;'>{cum}/{tot}</span>
                  <span style='font-size:.78rem;font-weight:700;color:{txt_color};min-width:36px;text-align:right;'>{p:.0%}</span>
                </div>
              </div>
              <div style='background:{bg_color};border-radius:100px;height:8px;overflow:hidden;'>
                <div style='width:{p*100:.0f}%;height:100%;background:{bar_color};border-radius:100px;
                            transition:width .4s ease;'></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='display:flex;gap:16px;margin-top:12px;padding-top:12px;
                    border-top:1px solid #f1f5f9;font-size:.7rem;color:#94a3b8;flex-wrap:wrap;'>
          <span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;
                background:#10b981;margin-right:4px;vertical-align:middle;'></span>≥95% Muy favorable</span>
          <span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;
                background:#f59e0b;margin-right:4px;vertical-align:middle;'></span>85–94% Aceptable</span>
          <span><span style='display:inline-block;width:8px;height:8px;border-radius:2px;
                background:#ef4444;margin-right:4px;vertical-align:middle;'></span>&lt;85% Desfavorable</span>
        </div>
        </div>""", unsafe_allow_html=True)

    with cr:
        st.markdown("""
        <div style='background:white;border-radius:16px;border:1px solid #e8eef5;
                    box-shadow:0 2px 12px rgba(0,0,0,.04);padding:1.5rem;margin-bottom:1rem;'>
          <div style='font-size:.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                      letter-spacing:.08em;margin-bottom:1.25rem;padding-bottom:.75rem;
                      border-bottom:1px solid #f1f5f9;'>Criterios de Tienda</div>
        """, unsafe_allow_html=True)

        for _, row in items_t.iterrows():
            cal = row["calificacion"]
            color    = "#10b981" if cal>=row["superior"] else ("#f59e0b" if cal>=row["minimo"] else "#ef4444")
            txt_col  = "#059669" if cal>=row["superior"] else ("#d97706" if cal>=row["minimo"] else "#dc2626")
            bg_color = "#f0fdf4" if cal>=row["superior"] else ("#fffbeb" if cal>=row["minimo"] else "#fff5f5")
            st.markdown(f"""
            <div style='margin-bottom:12px;'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
                <span style='font-size:.77rem;color:#475569;font-weight:500;'>{row['criterio']}</span>
                <span style='font-size:.82rem;font-weight:700;color:{txt_col};'>{cal}</span>
              </div>
              <div style='background:{bg_color};border-radius:100px;height:8px;overflow:hidden;'>
                <div style='width:{cal/10*100:.0f}%;height:100%;background:{color};border-radius:100px;'></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
