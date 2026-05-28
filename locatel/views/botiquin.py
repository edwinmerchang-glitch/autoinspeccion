"""
pages/botiquin.py
-----------------
Control de vencimientos del botiquín de primeros auxilios.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime

from db.queries import (
    get_botiquin,
    update_botiquin_item,
    update_botiquin_unidades,
    update_botiquin_fecha,
)


def _venc_status(fs: str | None, today: date) -> tuple[str, str, int]:
    """Retorna (label, badge_class, dias_restantes)."""
    if not fs or pd.isna(fs):
        return "Sin fecha", "b-gray", 999
    try:
        d = datetime.strptime(str(fs), "%Y-%m-%d").date()
        diff = (d - today).days
        if diff < 0:
            return "Vencido", "b-fail", diff
        if diff <= 90:
            return f"⚠️ {diff}d", "b-warn", diff
        return d.strftime("%d/%m/%Y"), "b-ok", diff
    except Exception:
        return str(fs), "b-gray", 999


def render(sel_aud_id: int) -> None:
    if not sel_aud_id:
        st.markdown("<div class='info-banner'>ℹ️ Selecciona una auditoría.</div>", unsafe_allow_html=True)
        st.stop()

    boti  = get_botiquin(sel_aud_id)
    today = date.today()

    vencidos = sum(1 for _, r in boti.iterrows() if _venc_status(r["fecha_vencimiento"], today)[2] < 0)
    proximos = sum(1 for _, r in boti.iterrows() if 0 <= _venc_status(r["fecha_vencimiento"], today)[2] <= 90)

    venc_badge = f"<span class='ph-badge desfavorable'>{vencidos} vencidos</span>" if vencidos else ""
    prox_badge = (
        f"<span class='ph-badge' style='background:rgba(245,158,11,.15);color:#fbbf24;border-color:rgba(245,158,11,.3);'>"
        f"{proximos} próximos</span>"
    ) if proximos else ""

    st.markdown(f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>🩺 Botiquín de Primeros Auxilios</div>
        <div class='ph-sub'>Control de vencimientos · Resolución 0705 de 2007</div>
      </div>
      <div class='ph-badges'>
        <span class='ph-badge'>{len(boti)} elementos</span>
        {venc_badge}{prox_badge}
      </div>
    </div>""", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"<div class='kpi blue'><div class='kpi-lbl'>Total Elementos</div><div class='kpi-val'>{len(boti)}</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='kpi {'red' if vencidos else 'green'}'><div class='kpi-lbl'>Vencidos</div><div class='kpi-val'>{vencidos}</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='kpi amber'><div class='kpi-lbl'>Próx. a Vencer (90d)</div><div class='kpi-val'>{proximos}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dl3, _ = st.columns([1, 3])
    with dl3:
        csv_b = boti[["item", "unidades", "fecha_vencimiento"]].to_csv(index=False)
        st.download_button("⬇️ Exportar CSV", csv_b, file_name="botiquin.csv", mime="text/csv", use_container_width=True)

    # ── Tabla editable ────────────────────────────────────────────────────────
    st.markdown("<div class='card'><div class='card-hd'>Inventario — edita fechas directamente en cada fila</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:grid;grid-template-columns:2rem 2.5fr 1.2fr 1.6fr 1fr;gap:.75rem;
         padding:.4rem 1rem;font-size:.68rem;font-weight:700;color:#94a3b8;
         text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #f1f5f9;margin-bottom:.25rem;'>
      <span>#</span><span>Elemento</span><span>Unidades</span><span>Fecha vencimiento</span><span>Estado</span>
    </div>""", unsafe_allow_html=True)

    changes_b = False

    for i, (_, row) in enumerate(boti.iterrows(), 1):
        lbl, bcls, diff = _venc_status(row["fecha_vencimiento"], today)
        c_num, c_item, c_uni, c_fecha, c_badge = st.columns([0.3, 2.5, 1.2, 1.6, 1])

        with c_num:
            st.markdown(f"<div style='padding:.6rem 0;color:#94a3b8;font-size:.76rem;font-weight:600;'>{i:02d}</div>", unsafe_allow_html=True)

        with c_item:
            new_item = st.text_input(f"item_{row['id']}", value=row["item"], key=f"bi_{row['id']}", label_visibility="collapsed")
            if new_item != row["item"]:
                update_botiquin_item(row["id"], new_item)
                changes_b = True

        with c_uni:
            new_uni = st.text_input(f"uni_{row['id']}", value=row["unidades"] or "", placeholder="Unidad", key=f"bu_{row['id']}", label_visibility="collapsed")
            if new_uni != (row["unidades"] or ""):
                update_botiquin_unidades(row["id"], new_uni or None)
                changes_b = True

        with c_fecha:
            try:
                cur_date = (
                    datetime.strptime(str(row["fecha_vencimiento"]), "%Y-%m-%d").date()
                    if row["fecha_vencimiento"] and pd.notna(row["fecha_vencimiento"])
                    else date.today()
                )
            except Exception:
                cur_date = date.today()

            new_fecha = st.date_input(f"fecha_{row['id']}", value=cur_date, key=f"bf_{row['id']}", label_visibility="collapsed", format="DD/MM/YYYY")
            if str(new_fecha) != str(row["fecha_vencimiento"] or ""):
                update_botiquin_fecha(row["id"], str(new_fecha))
                changes_b = True

        with c_badge:
            lbl2, bcls2, _ = _venc_status(str(new_fecha), today)
            st.markdown(f"<div style='padding:.55rem 0;'><span class='badge {bcls2}'>{lbl2}</span></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if changes_b:
        st.rerun()
