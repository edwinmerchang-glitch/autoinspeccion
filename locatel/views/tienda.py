"""
pages/tienda.py
---------------
Página de Auditoría de Tienda: edición de calificaciones y gráfico comparativo.
"""

import streamlit as st

from db.queries import get_items_tienda, update_calificacion_tienda


def render(sel_aud_id: int) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    items_t = get_items_tienda(sel_aud_id)
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

    if len(items_t) == 0:
        st.info("Sin datos de tienda para esta auditoría.")
        st.stop()

    dl_col, _, _ = st.columns([1, 1, 2])
    with dl_col:
        csv_t = items_t[["criterio", "minimo", "superior", "meta", "calificacion"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_t, file_name="tienda.csv", mime="text/csv", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    changes_t = False
    st.markdown("<div class='card'><div class='card-hd'>Criterios Operativos</div>", unsafe_allow_html=True)

    for _, row in items_t.iterrows():
        cal = row["calificacion"]
        color = "#10b981" if cal >= row["superior"] else ("#f59e0b" if cal >= row["minimo"] else "#ef4444")
        if cal >= row["superior"]:
            badge_t, lbl = "b-ok", "Superior"
        elif cal >= row["minimo"]:
            badge_t, lbl = "b-warn", "Aceptable"
        else:
            badge_t, lbl = "b-fail", "Bajo mínimo"

        c1, c2, c3 = st.columns([2.5, 1.5, 1])
        with c1:
            st.markdown(f"""
            <div style='padding:.65rem .9rem;background:#f8fafc;border:1px solid #e8eef5;
                        border-left:3px solid {color};border-radius:9px;'>
              <div style='font-weight:600;font-size:.85rem;color:#0f172a;'>{row['criterio']}</div>
              <div style='font-size:.74rem;color:#94a3b8;margin-top:3px;'>
                Mín: {row['minimo']} · Superior: {row['superior']} · Meta: {row['meta']}
              </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            new_cal = st.number_input(
                f"cal_{row['id']}", min_value=0.0, max_value=10.0,
                value=float(cal), step=0.5,
                key=f"nc_{row['id']}", label_visibility="collapsed",
            )
            if new_cal != cal:
                update_calificacion_tienda(row["id"], new_cal)
                changes_t = True
        with c3:
            st.markdown(f"<div style='padding:.65rem 0;'><span class='badge {badge_t}'>{lbl}</span></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Gráfico comparativo ───────────────────────────────────────────────────
    # Recargamos los datos para reflejar cambios inmediatos
    items_t2 = get_items_tienda(sel_aud_id)

    st.markdown("<div class='card'><div class='card-hd'>Gráfico de Calificaciones</div>", unsafe_allow_html=True)
    for _, row in items_t2.iterrows():
        cal = row["calificacion"]
        color     = "#1D9E75" if cal >= row["superior"] else ("#EF9F27" if cal >= row["minimo"] else "#E24B4A")
        txt_color = "#085041" if cal >= row["superior"] else ("#854F0B" if cal >= row["minimo"] else "#791F1F")
        bg_color  = "#E1F5EE" if cal >= row["superior"] else ("#FAEEDA" if cal >= row["minimo"] else "#FCEBEB")
        pct_width = cal / 10 * 100
        meta_pct  = row["meta"] / 10 * 100
        sup_pct   = row["superior"] / 10 * 100
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
          <div style='display:flex;justify-content:space-between;font-size:.78rem;color:#475569;margin-bottom:4px;'>
            <span style='font-weight:500;'>{row['criterio']}</span>
            <span style='font-weight:700;color:{txt_color};'>{cal}</span>
          </div>
          <div style='position:relative;height:24px;background:{bg_color};border-radius:6px;overflow:visible;'>
            <div style='width:{pct_width:.0f}%;height:100%;background:{color};border-radius:6px;
                        display:flex;align-items:center;justify-content:flex-end;padding-right:8px;
                        font-size:.72rem;font-weight:600;color:white;min-width:36px;'></div>
            <div style='position:absolute;top:-3px;bottom:-3px;left:{meta_pct:.0f}%;
                        width:2px;background:#1a56db;border-radius:1px;opacity:.5;'></div>
            <div style='position:absolute;top:-3px;bottom:-3px;left:{sup_pct:.0f}%;
                        width:2px;background:#7c3aed;border-radius:1px;opacity:.4;'></div>
          </div>
          <div style='display:flex;gap:12px;margin-top:3px;font-size:.68rem;color:#94a3b8;'>
            <span>Mín: {row['minimo']}</span>
            <span style='color:#1a56db;'>● Meta: {row['meta']}</span>
            <span style='color:#7c3aed;'>● Superior: {row['superior']}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if changes_t:
        st.rerun()
