"""
pages/hallazgos.py
------------------
Gestión de hallazgos: crear, editar, resolver/reabrir y borrar con confirmación.
"""

import streamlit as st
import pandas as pd

from db.queries import (
    get_hallazgos,
    create_hallazgo,
    update_hallazgo,
    set_hallazgo_estado,
    delete_hallazgo,
)


def render(sel_aud_id: int) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    hall  = get_hallazgos(sel_aud_id)
    pend  = len(hall[hall["estado"] == "Pendiente"]) if len(hall) else 0
    res   = len(hall[hall["estado"] == "Resuelto"])  if len(hall) else 0

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

    dl_col, add_col, _ = st.columns([1, 1, 2])
    with dl_col:
        if len(hall):
            csv_h = hall[["proceso_afectado", "hallazgo", "observaciones", "estado"]].to_csv(index=False)
            st.download_button("⬇️ Exportar CSV", csv_h, file_name="hallazgos.csv", mime="text/csv", use_container_width=True)
    with add_col:
        if st.button("➕ Nuevo Hallazgo", type="primary", use_container_width=True):
            st.session_state["show_hall"] = not st.session_state.get("show_hall", False)

    # ── Formulario nuevo hallazgo ─────────────────────────────────────────────
    if st.session_state.get("show_hall"):
        with st.form("add_hall"):
            st.markdown("<div class='form-section-label'>Nuevo Hallazgo</div>", unsafe_allow_html=True)
            hc1, hc2 = st.columns(2)
            proc = hc1.text_input("Proceso Afectado")
            obs  = hc2.text_input("Observaciones")
            desc = st.text_area("Descripción del Hallazgo")
            if st.form_submit_button("💾 Guardar Hallazgo", type="primary") and proc and desc:
                create_hallazgo(sel_aud_id, proc, desc, obs or None)
                st.session_state["show_hall"] = False
                st.rerun()

    # ── Lista de hallazgos ────────────────────────────────────────────────────
    editing_id  = st.session_state.get("edit_hall_id")
    confirm_del = st.session_state.get("confirm_del_id")

    if len(hall) == 0:
        st.markdown("<div class='success-banner'>✅ No hay hallazgos registrados para esta auditoría.</div>", unsafe_allow_html=True)
        return

    for _, h in hall.iterrows():
        hid = int(h["id"])
        ok  = h["estado"] == "Resuelto"
        bc  = "#10b981" if ok else "#ef4444"
        bg  = "#f0fdf4" if ok else "#fff8f8"
        bdr = "#bbf7d0" if ok else "#fecdd3"

        # ── Modo edición ──────────────────────────────────────────────────────
        if editing_id == hid:
            with st.form(f"edit_form_{hid}"):
                st.markdown(f"<div style='font-size:.75rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.75rem;'>✏️ Editando hallazgo #{hid}</div>", unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                e_proc = ec1.text_input("Proceso Afectado", value=h["proceso_afectado"])
                e_est  = ec2.selectbox("Estado", ["Pendiente", "Resuelto"], index=0 if h["estado"] == "Pendiente" else 1)
                e_hall = st.text_area("Descripción", value=h["hallazgo"])
                e_obs  = st.text_input("Observaciones", value=h["observaciones"] if pd.notna(h.get("observaciones")) and h["observaciones"] else "")
                sc1, sc2 = st.columns(2)
                if sc1.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                    update_hallazgo(hid, e_proc, e_hall, e_obs or None, e_est)
                    st.session_state.pop("edit_hall_id", None)
                    st.rerun()
                if sc2.form_submit_button("✕ Cancelar", use_container_width=True):
                    st.session_state.pop("edit_hall_id", None)
                    st.rerun()
            continue

        # ── Tarjeta normal + botones ──────────────────────────────────────────
        card_col, btn_col = st.columns([5, 1])
        with card_col:
            obs_html = (
                f'<div style="color:#94a3b8;font-size:.76rem;margin-top:.2rem;font-style:italic;">{h["observaciones"]}</div>'
                if pd.notna(h.get("observaciones")) and h["observaciones"] else ""
            )
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {bdr};border-left:4px solid {bc};
                 border-radius:10px;padding:1rem 1.25rem;margin-bottom:.25rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='font-weight:700;font-size:.88rem;color:#0f172a;'>#{hid} · {h["proceso_afectado"]}</span>
                <span class='badge {"b-ok" if ok else "b-fail"}'>{h["estado"]}</span>
              </div>
              <div style='color:#475569;font-size:.81rem;margin-top:.35rem;'>{h["hallazgo"]}</div>
              {obs_html}
            </div>""", unsafe_allow_html=True)

        with btn_col:
            if not ok:
                if st.button("✅ Resolver", key=f"res_{hid}", use_container_width=True):
                    set_hallazgo_estado(hid, "Resuelto")
                    st.rerun()
            else:
                if st.button("↩️ Reabrir", key=f"reopen_{hid}", use_container_width=True):
                    set_hallazgo_estado(hid, "Pendiente")
                    st.rerun()

            if st.button("✏️ Editar", key=f"edit_{hid}", use_container_width=True):
                st.session_state["edit_hall_id"] = hid
                st.session_state.pop("confirm_del_id", None)
                st.rerun()

            if confirm_del == hid:
                st.markdown("<div style='font-size:.72rem;color:#b91c1c;font-weight:600;text-align:center;margin-top:2px;'>¿Confirmar?</div>", unsafe_allow_html=True)
                cd1, cd2 = st.columns(2)
                if cd1.button("Sí", key=f"del_yes_{hid}", use_container_width=True):
                    delete_hallazgo(hid)
                    st.session_state.pop("confirm_del_id", None)
                    st.rerun()
                if cd2.button("No", key=f"del_no_{hid}", use_container_width=True):
                    st.session_state.pop("confirm_del_id", None)
                    st.rerun()
            else:
                if st.button("🗑️ Borrar", key=f"del_{hid}", use_container_width=True):
                    st.session_state["confirm_del_id"] = hid
                    st.session_state.pop("edit_hall_id", None)
                    st.rerun()

        st.markdown("<div style='margin-bottom:.5rem;'></div>", unsafe_allow_html=True)
