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
        st.markdown("""<div style="background:white;border-radius:16px;border:1px solid #e8eef5;
            box-shadow:0 2px 12px rgba(0,0,0,.04);padding:1.5rem;margin-bottom:1rem;">
            <div style="font-size:.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                letter-spacing:.08em;margin-bottom:1rem;padding-bottom:.75rem;
                border-bottom:1px solid #f1f5f9;">📋 Cumplimiento por Sección</div>""",
            unsafe_allow_html=True)

        secs = get_secciones_farma()
        for _, s in secs.iterrows():
            si = items_f[items_f["seccion_id"] == s["id"]]
            if not len(si): continue
            cum = int(si["puntaje"].sum()); tot = len(si); p = cum / tot
            if p >= 0.95:
                bc, tc, bg, dc, lbl = "#10b981","#059669","#f0fdf4","#d1fae5","Muy favorable"
            elif p >= 0.85:
                bc, tc, bg, dc, lbl = "#f59e0b","#b45309","#fffbeb","#fde68a","Aceptable"
            else:
                bc, tc, bg, dc, lbl = "#ef4444","#dc2626","#fff5f5","#fecaca","Desfavorable"
            nombre = s["nombre"]
            pw = f"{p*100:.0f}"
            pf = f"{p:.0%}"
            st.markdown(
                f"<div style=\"background:{bg};border:1px solid {dc};border-radius:12px;"
                f"padding:.85rem 1rem;margin-bottom:.6rem;\">"
                f"<div style=\"display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem;\">"
                f"<div style=\"font-size:.8rem;font-weight:600;color:#334155;line-height:1.3;flex:1;padding-right:.5rem;\">{nombre}</div>"
                f"<div style=\"text-align:right;flex-shrink:0;\">"
                f"<div style=\"font-size:1.1rem;font-weight:800;color:{tc};line-height:1;\">{pf}</div>"
                f"<div style=\"font-size:.65rem;color:{tc};opacity:.7;margin-top:1px;\">{cum}/{tot} ítems</div>"
                f"</div></div>"
                f"<div style=\"background:white;border-radius:100px;height:6px;overflow:hidden;opacity:.7;\">"
                f"<div style=\"width:{pw}%;height:100%;background:{bc};border-radius:100px;\"></div></div>"
                f"<div style=\"font-size:.65rem;color:{tc};margin-top:.35rem;font-weight:600;opacity:.8;\">{lbl}</div>"
                f"</div>",
                unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with cr:
        st.markdown("""<div style="background:white;border-radius:16px;border:1px solid #e8eef5;
            box-shadow:0 2px 12px rgba(0,0,0,.04);padding:1.5rem;margin-bottom:1rem;">
            <div style="font-size:.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                letter-spacing:.08em;margin-bottom:1rem;padding-bottom:.75rem;
                border-bottom:1px solid #f1f5f9;">🏪 Criterios de Tienda</div>""",
            unsafe_allow_html=True)

        for _, row in items_t.iterrows():
            cal = row["calificacion"]
            if cal >= row["superior"]:
                bc, tc, bg, dc, lbl, icon = "#10b981","#059669","#f0fdf4","#d1fae5","Superior","✅"
            elif cal >= row["minimo"]:
                bc, tc, bg, dc, lbl, icon = "#f59e0b","#b45309","#fffbeb","#fde68a","Aceptable","⚠️"
            else:
                bc, tc, bg, dc, lbl, icon = "#ef4444","#dc2626","#fff5f5","#fecaca","Bajo mínimo","❌"
            pw = f"{cal/10*100:.0f}"
            criterio = row["criterio"]
            mn, mt, sp = row["minimo"], row["meta"], row["superior"]
            st.markdown(
                f"<div style=\"background:{bg};border:1px solid {dc};border-radius:12px;"
                f"padding:.85rem 1rem;margin-bottom:.6rem;\">"
                f"<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:.45rem;\">"
                f"<div style=\"font-size:.78rem;font-weight:600;color:#334155;flex:1;padding-right:.5rem;line-height:1.3;\">"
                f"{icon} {criterio}</div>"
                f"<div style=\"font-size:1.15rem;font-weight:800;color:{tc};flex-shrink:0;\">{cal}</div></div>"
                f"<div style=\"background:white;border-radius:100px;height:6px;overflow:hidden;opacity:.7;\">"
                f"<div style=\"width:{pw}%;height:100%;background:{bc};border-radius:100px;\"></div></div>"
                f"<div style=\"display:flex;justify-content:space-between;margin-top:.35rem;font-size:.63rem;color:{tc};opacity:.75;\">"
                f"<span>{lbl}</span><span>Mín {mn} · Meta {mt} · Sup {sp}</span></div>"
                f"</div>",
                unsafe_allow_html=True)

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
