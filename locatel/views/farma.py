"""
views/farma.py — Auditoría Farmacéutica modernizada
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
        st.info("ℹ️ Selecciona una auditoría en el panel lateral.")
        st.stop()

    items_f = get_items_farma(sel_aud_id)
    tf = len(items_f)
    cf = int(items_f["puntaje"].sum()) if tf else 0
    pf = cf / tf if tf else 0

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("## 💊 Auditoría Farmacéutica")
    st.caption(f"**{cf}/{tf}** ítems cumplidos · **{pf:.0%}** de cumplimiento · Cambios guardados automáticamente")

    # ── Filtros ───────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([3, 1.5, 1])
    search = fc1.text_input("Buscar", placeholder="🔍  Filtrar por nombre de ítem...", label_visibility="collapsed")
    filt   = fc2.selectbox("Estado", ["Todos", "✅ Cumplidos", "❌ Incumplidos"], label_visibility="collapsed")
    with fc3:
        csv_f = items_f[["seccion_nombre","item","puntaje","observacion"]].to_csv(index=False)
        st.download_button("⬇️ CSV", csv_f, file_name="farma.csv", mime="text/csv", use_container_width=True)

    df_view = items_f.copy()
    if search:
        df_view = df_view[df_view["item"].str.contains(search, case=False, na=False)]
    if filt == "✅ Cumplidos":
        df_view = df_view[df_view["puntaje"] == 1]
    elif filt == "❌ Incumplidos":
        df_view = df_view[df_view["puntaje"] == 0]

    changes_made = False

    for seccion in df_view["seccion_nombre"].unique():
        sec_df = df_view[df_view["seccion_nombre"] == seccion]
        sc = int(sec_df["puntaje"].sum()); st_ = len(sec_df)
        sp = sc / st_ if st_ else 0
        color_sp = pct_color(sp)
        lbl = "Muy favorable" if sp>=0.95 else ("Aceptable" if sp>=0.85 else "Desfavorable")

        with st.expander(f"**{seccion}** — {sc}/{st_} ({sp:.0%}) · {lbl}", expanded=True):
            st.progress(sp)
            st.markdown("")

            for _, row in sec_df.iterrows():
                cumple = row["puntaje"] == 1
                obs_current = row["observacion"] if pd.notna(row["observacion"]) else ""

                # Fila: nombre | toggle | observación
                c_name, c_tog, c_obs = st.columns([3.5, 1, 2.5])

                with c_name:
                    icon = "✅" if cumple else "❌"
                    color = "#059669" if cumple else "#dc2626"
                    bg    = "#f0fdf4" if cumple else "#fff5f5"
                    border= "#bbf7d0" if cumple else "#fecaca"
                    st.markdown(
                        "<div style='background:" + bg + ";border:1px solid " + border + ";"
                        "border-left:3px solid " + color + ";border-radius:8px;"
                        "padding:.55rem .85rem;min-height:42px;display:flex;align-items:center;'>"
                        "<span style='font-size:.82rem;font-weight:500;color:#334155;line-height:1.35;'>"
                        + icon + " " + row["item"] +
                        "</span></div>",
                        unsafe_allow_html=True
                    )

                with c_tog:
                    new_toggle = st.toggle(
                        "Cumple",
                        value=cumple,
                        key=f"tog_{row['id']}",
                        label_visibility="collapsed",
                    )
                    if new_toggle != cumple:
                        update_item_farma_puntaje(row["id"], 1 if new_toggle else 0)
                        changes_made = True

                with c_obs:
                    new_obs = st.text_input(
                        f"obs_{row['id']}", value=obs_current,
                        placeholder="Observación...",
                        key=f"obs_{row['id']}",
                        label_visibility="collapsed",
                    )
                    if new_obs != obs_current:
                        update_item_farma_observacion(row["id"], new_obs if new_obs else None)
                        changes_made = True

            st.markdown("")

    if changes_made:
        all_f = get_items_farma(sel_aud_id)
        nueva = all_f["puntaje"].sum() / len(all_f) if len(all_f) else 0
        update_calificacion_global(sel_aud_id, nueva)
        st.rerun()
