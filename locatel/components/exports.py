"""
components/exports.py
---------------------
Generación de reportes descargables (Excel, CSV).
Importar generate_excel_report en cualquier página que lo necesite.
"""

import io
import pandas as pd


def generate_excel_report(
    aud_row: dict,
    items_farma: pd.DataFrame,
    items_tienda: pd.DataFrame,
    hallazgos: pd.DataFrame,
    botiquin: pd.DataFrame,
    tienda_name: str,
) -> io.BytesIO:
    """
    Genera un archivo Excel con todas las secciones de la auditoría.

    Returns:
        BytesIO listo para pasar a st.download_button.
    """
    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Resumen
        pd.DataFrame({
            "Campo": ["Tienda", "Fecha", "Auditor", "Calificación Global", "Resultado"],
            "Valor": [
                tienda_name,
                aud_row["fecha"],
                aud_row["auditor"],
                f"{aud_row['calificacion_global']:.0%}",
                aud_row["resultado"],
            ],
        }).to_excel(writer, sheet_name="Resumen", index=False)

        # Farma
        if len(items_farma):
            (items_farma[["seccion_nombre", "item", "puntaje", "observacion"]]
             .rename(columns={
                 "seccion_nombre": "Sección",
                 "item": "Ítem",
                 "puntaje": "Puntaje",
                 "observacion": "Observación",
             })
             .to_excel(writer, sheet_name="Auditoría Farma", index=False))

        # Tienda
        if len(items_tienda):
            (items_tienda[["criterio", "minimo", "superior", "meta", "calificacion"]]
             .rename(columns={
                 "criterio": "Criterio",
                 "minimo": "Mínimo",
                 "superior": "Superior",
                 "meta": "Meta",
                 "calificacion": "Calificación",
             })
             .to_excel(writer, sheet_name="Auditoría Tienda", index=False))

        # Hallazgos
        if len(hallazgos):
            (hallazgos[["proceso_afectado", "hallazgo", "observaciones", "estado"]]
             .rename(columns={
                 "proceso_afectado": "Proceso",
                 "hallazgo": "Hallazgo",
                 "observaciones": "Observaciones",
                 "estado": "Estado",
             })
             .to_excel(writer, sheet_name="Hallazgos", index=False))

        # Botiquín
        if len(botiquin):
            (botiquin[["item", "unidades", "fecha_vencimiento"]]
             .rename(columns={
                 "item": "Elemento",
                 "unidades": "Unidades",
                 "fecha_vencimiento": "Vencimiento",
             })
             .to_excel(writer, sheet_name="Botiquín", index=False))

    buf.seek(0)
    return buf
