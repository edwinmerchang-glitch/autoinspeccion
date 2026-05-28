"""
pages/nueva_auditoria.py
------------------------
Formulario para crear una nueva auditoría, copiando la plantilla de ítems.
"""

import streamlit as st
from datetime import date

from db.queries import (
    get_tiendas,
    create_auditoria,
    copy_farma_template,
    copy_tienda_template,
    bulk_create_hallazgos,
)


def render() -> None:
    tiendas = get_tiendas()

    st.markdown("""
    <div class='page-header'>
      <div>
        <div class='ph-title'>➕ Nueva Auditoría</div>
        <div class='ph-sub'>Registra una nueva autoinspección. Los ítems se cargan automáticamente para edición.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:1rem 1.25rem;
         color:#1e40af;font-size:.83rem;margin-bottom:1.25rem;display:flex;gap:.75rem;align-items:flex-start;'>
      <span style='font-size:1.1rem;'>💡</span>
      <div>Después de crear la auditoría, ve a <strong>Auditoría Farma</strong> y <strong>Auditoría Tienda</strong>
      para diligenciar cada ítem con su puntaje y observación. El dashboard se actualizará en tiempo real.</div>
    </div>""", unsafe_allow_html=True)

    with st.form("nueva_aud", clear_on_submit=True):
        st.markdown("<div class='form-section-label'>📋 Información General</div>", unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        tienda_opts = [f"{r['id']} - {r['nombre']}" for _, r in tiendas.iterrows()]
        tienda_sel  = r1c1.selectbox("Tienda", tienda_opts)
        fecha_sel   = r1c2.date_input("Fecha de Auditoría", value=date.today())

        r2c1, r2c2 = st.columns(2)
        auditor       = r2c1.text_input("Nombre del Auditor", placeholder="Ej: Edwin Merchán")
        resultado_sel = r2c2.selectbox("Resultado Inicial", ["FAVORABLE", "DESFAVORABLE", "CONDICIONADO"])

        st.markdown("<div class='form-section-label'>⚠️ Hallazgos Iniciales (opcional)</div>", unsafe_allow_html=True)
        hcols = st.columns(2)
        hall_inputs = [
            hcols[i % 2].text_input(f"Hallazgo {i+1}", placeholder="Proceso: Descripción del hallazgo", key=f"hi_{i}")
            for i in range(4)
        ]

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Crear Auditoría", type="primary", use_container_width=True)

        if submitted:
            if not auditor.strip():
                st.error("⚠️ El nombre del auditor es requerido.")
            else:
                tienda_id = tienda_sel.split(" - ")[0]
                new_id = create_auditoria(tienda_id, str(fecha_sel), auditor.strip(), resultado_sel)

                copy_farma_template(new_id)
                copy_tienda_template(new_id)

                # Hallazgos iniciales con formato "Proceso: Descripción"
                hallazgos_validos = [
                    (h.split(":", 1)[0].strip(), h.split(":", 1)[1].strip(), None)
                    for h in hall_inputs
                    if h and ":" in h
                ]
                if hallazgos_validos:
                    bulk_create_hallazgos(new_id, hallazgos_validos)

                st.markdown(f"""
                <div class='success-banner'>
                  ✅ <strong>Auditoría #{new_id} creada exitosamente.</strong>
                  Selecciona la tienda <strong>{tienda_sel}</strong> en el panel lateral y elige esta auditoría para comenzar a diligenciarla.
                </div>""", unsafe_allow_html=True)
