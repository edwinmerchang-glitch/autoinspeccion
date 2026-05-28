"""
pages/farma.py
--------------
Página de Auditoría Farmacéutica: edición por ítem con puntaje y observación.
"""

import streamlit as st
import pandas as pd

from db.queries import (
    get_items_farma,
    update_item_farma_puntaje,
    update_item_farma_observacion,
    update_calificacion_global,
)
from components.ui import pct_color


def render(sel_aud_id: int) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría en el panel lateral.</div>", unsafe_allow_html=True)
        st.stop()

    items_f = get_items_farma(sel_aud_id)
    tf = len(items_f)
    cf = int(items_f["puntaje"].sum()) if tf else 0
    pf = cf / tf if tf else 0

    # Calcular color del badge de porcentaje
    if pf >= 0.95:
        badge_rgb, badge_col, badge_border = "16,185,129", "#34d399", "16,185,129"
    elif pf >= 0.85:
        badge_rgb, badge_col, badge_border = "245,158,11", "#fbbf24", "245,158,11"
    else:
        badge_rgb, badge_col, badge_border = "239,68,68", "#f87171", "239,68,68"

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>💊 Auditoría Farmacéutica</div>
        <div class='ph-sub'>Edita el puntaje y observación de cada ítem. Los cambios se guardan automáticamente.</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>{cf}/{tf} cumplidos</span>
        <span class='ph-badge' style='background:rgba({badge_rgb},.15);color:{badge_col};border-color:rgba({badge_border},.35);'>{pf:.0%}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Filtros ────────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        search = st.text_input("🔍 Buscar ítem", placeholder="Filtra por nombre...", label_visibility="collapsed")
    with fc2:
        filt = st.selectbox("Estado", ["Todos", "✓ Cumplidos", "✗ Incumplidos"], label_visibility="collapsed")
    with fc3:
        csv_f = items_f[["seccion_nombre", "item", "puntaje", "observacion"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_f, file_name="farma.csv", mime="text/csv", use_container_width=True)

    df_view = items_f.copy()
    if search:
        df_view = df_view[df_view["item"].str.contains(search, case=False, na=False)]
    if filt == "✓ Cumplidos":
        df_view = df_view[df_view["puntaje"] == 1]
    elif filt == "✗ Incumplidos":
        df_view = df_view[df_view["puntaje"] == 0]

    changes_made = False

    for seccion in df_view["seccion_nombre"].unique():
        sec_df = df_view[df_view["seccion_nombre"] == seccion]
        sc = int(sec_df["puntaje"].sum()); st_ = len(sec_df)
        sp = sc / st_ if st_ else 0
        color_sp = pct_color(sp)

        with st.expander(f"📁  {seccion}   ·   {sc}/{st_}   ({sp:.0%})", expanded=True):
            st.markdown(f"""
            <div style='margin-bottom:1rem;'>
              <div class='pb-wrap'><div class='pb-fill' style='width:{sp*100:.0f}%;background:{color_sp};'></div></div>
              <div style='font-size:.72rem;color:#94a3b8;margin-top:4px;'>{sc} de {st_} ítems cumplidos</div>
            </div>""", unsafe_allow_html=True)

            for _, row in sec_df.iterrows():
                row_class = "pass" if row["puntaje"] == 1 else "fail"
                left, mid, right = st.columns([3, 1.2, 2])

                with left:
                    st.markdown(f"""
                    <div class='audit-item-row {row_class}' style='padding:.6rem .85rem;'>
                      <div class='item-name'>{row['item']}</div>
                    </div>""", unsafe_allow_html=True)

                with mid:
                    new_val = st.radio(
                        f"puntaje_{row['id']}",
                        ["✓ Cumple", "✗ No Cumple"],
                        index=0 if row["puntaje"] == 1 else 1,
                        key=f"radio_{row['id']}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
                    new_puntaje = 1 if new_val == "✓ Cumple" else 0
                    if new_puntaje != row["puntaje"]:
                        update_item_farma_puntaje(row["id"], new_puntaje)
                        changes_made = True

                with right:
                    obs_current = row["observacion"] if pd.notna(row["observacion"]) else ""
                    new_obs = st.text_input(
                        f"obs_{row['id']}", value=obs_current,
                        placeholder="Observación...",
                        key=f"obs_{row['id']}",
                        label_visibility="collapsed",
                    )
                    if new_obs != obs_current:
                        update_item_farma_observacion(row["id"], new_obs if new_obs else None)
                        changes_made = True

    if changes_made:
        # Recalcular calificación global
        all_f = get_items_farma(sel_aud_id)
        nueva = all_f["puntaje"].sum() / len(all_f) if len(all_f) else 0
        update_calificacion_global(sel_aud_id, nueva)
        st.rerun()
