"""
components/ui.py
----------------
Componentes visuales reutilizables: gauge SVG, badges, barras de progreso
y helpers de color. Importar desde aquí en cualquier página.
"""

import math
from typing import Literal


# ── Tipos ──────────────────────────────────────────────────────────────────────

ColorClass = Literal["val-green", "val-amber", "val-red", "val-blue", "val-purple"]
AccentClass = Literal["green", "amber", "red", "blue", "purple"]


# ── Helpers de color ───────────────────────────────────────────────────────────

def pct_color(p: float) -> str:
    """Hex color según porcentaje de cumplimiento."""
    if p >= 0.95:
        return "#10b981"
    if p >= 0.85:
        return "#f59e0b"
    return "#ef4444"


def val_color_class(pct: float) -> ColorClass:
    """Clase CSS para el valor del KPI según porcentaje."""
    if pct >= 0.95:
        return "val-green"
    if pct >= 0.85:
        return "val-amber"
    return "val-red"


def resultado_badge(resultado: str) -> str:
    """HTML badge para el resultado de una auditoría."""
    cls = {
        "FAVORABLE": "b-fav",
        "DESFAVORABLE": "b-desfav",
        "CONDICIONADO": "b-cond",
    }.get(resultado, "b-gray")
    return f"<span class='badge {cls}'>{resultado or 'N/D'}</span>"


# ── Gauge SVG ──────────────────────────────────────────────────────────────────

def gauge_html(value: float, title: str, label: str, threshold_color: str) -> str:
    """
    Gauge de anillo en SVG puro — renderiza nativamente en Streamlit st.markdown.

    Args:
        value:           Porcentaje 0.0–1.0.
        title:           Título superior del gauge.
        label:           Subtítulo bajo el valor (ej. '111/117 ítems').
        threshold_color: Color hex resultado de pct_color().
    """
    pct = max(0.0, min(1.0, value))
    display_val = f"{pct * 100:.0f}%"

    themes = {
        "#10b981": ("#1D9E75", "#085041", "#E1F5EE", "Muy favorable"),
        "#f59e0b": ("#EF9F27", "#854F0B", "#FAEEDA", "Aceptable"),
    }
    arc_col, txt_col, track_col, status_txt = themes.get(
        threshold_color, ("#E24B4A", "#791F1F", "#FCEBEB", "Desfavorable")
    )

    cx, cy, r = 100, 100, 70
    stroke_w = 16
    sweep, start = 240, 210

    def pt(deg: float) -> tuple[float, float]:
        rad = math.radians(deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def arc(d1: float, d2: float) -> str:
        x1, y1 = pt(d1)
        x2, y2 = pt(d2)
        laf = 1 if (d2 - d1) > 180 else 0
        return f"M {x1:.3f} {y1:.3f} A {r} {r} 0 {laf} 1 {x2:.3f} {y2:.3f}"

    track = arc(start, start + sweep)
    end_deg = start + sweep * pct
    fill = arc(start, end_deg) if pct > 0.005 else ""

    fill_svg = (
        f'<path d="{fill}" fill="none" stroke="{arc_col}" '
        f'stroke-width="{stroke_w}" stroke-linecap="round"/>'
        if fill else ""
    )
    ex, ey = pt(end_deg)
    cap_svg = (
        f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{stroke_w // 2}" fill="{arc_col}"/>'
        if pct > 0.02 else ""
    )

    sx, sy = pt(start)
    ex2, ey2 = pt(start + sweep)

    return f"""
    <div style="background:white;border-radius:14px;border:1px solid #e8eef5;
                box-shadow:0 2px 8px rgba(0,0,0,.04);padding:1.25rem 1rem 1.5rem;text-align:center;">
      <div style="font-size:.72rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
                  letter-spacing:.07em;margin-bottom:.5rem;">{title}</div>
      <svg width="200" height="185" viewBox="0 0 200 165" xmlns="http://www.w3.org/2000/svg"
           style="display:block;margin:0 auto;overflow:visible;">
        <path d="{track}" fill="none" stroke="{track_col}" stroke-width="{stroke_w}" stroke-linecap="round"/>
        {fill_svg}
        {cap_svg}
        <circle cx="{sx:.2f}" cy="{sy:.2f}" r="{stroke_w // 2}" fill="{track_col}"/>
        <text x="100" y="95" text-anchor="middle" dominant-baseline="middle"
              font-family="Inter,sans-serif" font-size="30" font-weight="700" fill="{arc_col}">{display_val}</text>
        <text x="100" y="118" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="11" fill="{txt_col}">{status_txt}</text>
        <text x="100" y="134" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="10" fill="#94a3b8">{label}</text>
        <text x="{sx - 6:.1f}" y="{sy + 4:.1f}" text-anchor="end"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">0%</text>
        <text x="{ex2 + 6:.1f}" y="{ey2 + 4:.1f}" text-anchor="start"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">100%</text>
      </svg>
    </div>"""


# ── KPI card ───────────────────────────────────────────────────────────────────

def kpi_html(label: str, value: str, subtitle: str, accent: AccentClass, val_class: str = "") -> str:
    """HTML para una tarjeta KPI."""
    return f"""<div class='kpi {accent}'>
      <div class='kpi-lbl'>{label}</div>
      <div class='kpi-val {val_class}'>{value}</div>
      <div class='kpi-sub'>{subtitle}</div>
    </div>"""


# ── Barra de progreso ──────────────────────────────────────────────────────────

def progress_bar(pct: float, color: str) -> str:
    """HTML de barra de progreso con porcentaje dado."""
    return f"""<div class='pb-wrap'>
      <div class='pb-fill' style='width:{pct * 100:.0f}%;background:{color};'></div>
    </div>"""


# ── Page header ────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str, badges_html: str = "") -> str:
    """HTML del encabezado de página."""
    return f"""
    <div class='page-header'>
      <div>
        <div class='ph-title'>{title}</div>
        <div class='ph-sub'>{subtitle}</div>
      </div>
      <div class='ph-badges'>{badges_html}</div>
    </div>"""


def info_banner(text: str) -> str:
    return f"<div class='info-banner'>ℹ️ {text}</div>"


def success_banner(text: str) -> str:
    return f"<div class='success-banner'>✅ {text}</div>"
