"""
components/ui.py — Componentes visuales modernos
"""

import math
from typing import Literal

ColorClass = Literal["val-green", "val-amber", "val-red", "val-blue", "val-purple"]
AccentClass = Literal["green", "amber", "red", "blue", "purple"]


def pct_color(p: float) -> str:
    if p >= 0.95: return "#10b981"
    if p >= 0.85: return "#f59e0b"
    return "#ef4444"


def val_color_class(pct: float) -> ColorClass:
    if pct >= 0.95: return "val-green"
    if pct >= 0.85: return "val-amber"
    return "val-red"


def resultado_badge(resultado: str) -> str:
    cls = {"FAVORABLE": "b-fav", "DESFAVORABLE": "b-desfav", "CONDICIONADO": "b-cond"}.get(resultado, "b-gray")
    return f"<span class='badge {cls}'>{resultado or 'N/D'}</span>"


def gauge_html(value: float, title: str, label: str, threshold_color: str) -> str:
    pct = max(0.0, min(1.0, value))
    display_val = f"{pct * 100:.0f}%"

    themes = {
        "#10b981": ("#10b981", "#059669", "#d1fae5", "#ecfdf5", "Muy favorable"),
        "#f59e0b": ("#f59e0b", "#d97706", "#fde68a", "#fffbeb", "Aceptable"),
    }
    arc_col, dark_col, glow_col, bg_col, status_txt = themes.get(
        threshold_color,
        ("#ef4444", "#dc2626", "#fecaca", "#fff5f5", "Desfavorable")
    )

    cx, cy, r = 110, 110, 80
    stroke_w = 14
    sweep, start = 240, 210

    def pt(deg):
        rad = math.radians(deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def arc(d1, d2):
        x1, y1 = pt(d1)
        x2, y2 = pt(d2)
        laf = 1 if (d2 - d1) > 180 else 0
        return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 {laf} 1 {x2:.2f} {y2:.2f}"

    track = arc(start, start + sweep)
    end_deg = start + sweep * pct
    fill = arc(start, end_deg) if pct > 0.005 else ""

    ex, ey = pt(end_deg)
    sx, sy = pt(start)
    ex2, ey2 = pt(start + sweep)

    fill_svg = f'<path d="{fill}" fill="none" stroke="{arc_col}" stroke-width="{stroke_w}" stroke-linecap="round" filter="url(#glow)"/>' if fill else ""
    cap_svg  = f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{stroke_w//2 + 1}" fill="{arc_col}" filter="url(#glow)"/>' if pct > 0.02 else ""

    return f"""
    <div style="background:white;border-radius:20px;border:1px solid #e8eef5;
                box-shadow:0 4px 24px rgba(0,0,0,.06);padding:1.5rem 1rem 1.25rem;
                text-align:center;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:3px;
                  background:linear-gradient(90deg,{arc_col},{dark_col});border-radius:20px 20px 0 0;"></div>
      <div style="font-size:.68rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
                  letter-spacing:.1em;margin-bottom:.75rem;">{title}</div>
      <svg width="220" height="175" viewBox="0 0 220 175" xmlns="http://www.w3.org/2000/svg"
           style="display:block;margin:0 auto;overflow:visible;">
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <linearGradient id="trackGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#f1f5f9;stop-opacity:1"/>
            <stop offset="100%" style="stop-color:#e2e8f0;stop-opacity:1"/>
          </linearGradient>
        </defs>
        <!-- Track -->
        <path d="{track}" fill="none" stroke="url(#trackGrad)" stroke-width="{stroke_w}" stroke-linecap="round"/>
        <!-- Fill -->
        {fill_svg}
        <!-- Cap dot -->
        {cap_svg}
        <!-- Start dot -->
        <circle cx="{sx:.2f}" cy="{sy:.2f}" r="{stroke_w//2}" fill="#e2e8f0"/>
        <!-- Center value -->
        <text x="110" y="102" text-anchor="middle" dominant-baseline="middle"
              font-family="Inter,sans-serif" font-size="34" font-weight="800"
              fill="{arc_col}" letter-spacing="-1">{display_val}</text>
        <text x="110" y="124" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="11" font-weight="600"
              fill="{dark_col}">{status_txt}</text>
        <text x="110" y="142" text-anchor="middle"
              font-family="Inter,sans-serif" font-size="10" fill="#94a3b8">{label}</text>
        <!-- Scale labels -->
        <text x="{sx-8:.1f}" y="{sy+5:.1f}" text-anchor="end"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">0%</text>
        <text x="{ex2+8:.1f}" y="{ey2+5:.1f}" text-anchor="start"
              font-family="Inter,sans-serif" font-size="9" fill="#cbd5e1">100%</text>
      </svg>
    </div>"""


def kpi_html(label: str, value: str, subtitle: str, accent: AccentClass, val_class: str = "") -> str:
    accent_colors = {
        "blue":   ("#1a56db", "#eff6ff", "#dbeafe"),
        "green":  ("#059669", "#f0fdf4", "#dcfce7"),
        "red":    ("#dc2626", "#fff5f5", "#fee2e2"),
        "amber":  ("#b45309", "#fffbeb", "#fde68a"),
        "purple": ("#7c3aed", "#faf5ff", "#ede9fe"),
    }
    col, bg_light, border_col = accent_colors.get(accent, ("#1a56db", "#eff6ff", "#dbeafe"))
    return f"""
    <div style="background:white;border-radius:16px;padding:1.1rem 1.25rem;
                border:1px solid #e8eef5;box-shadow:0 2px 12px rgba(0,0,0,.04);
                position:relative;overflow:hidden;height:100%;">
      <div style="position:absolute;top:0;left:0;right:0;height:3px;
                  background:linear-gradient(90deg,{col},{col}88);"></div>
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:32px;height:32px;border-radius:8px;background:{bg_light};
                  border:1px solid {border_col};margin-bottom:.6rem;">
        <div style="width:10px;height:10px;border-radius:50%;background:{col};"></div>
      </div>
      <div style="font-size:.62rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
                  letter-spacing:.07em;margin-bottom:.3rem;">{label}</div>
      <div style="font-size:1.5rem;font-weight:800;color:#0f172a;line-height:1.1;
                  letter-spacing:-.02em;" class="{val_class}">{value}</div>
      <div style="font-size:.72rem;color:#94a3b8;margin-top:.3rem;">{subtitle}</div>
    </div>"""


def progress_bar(pct: float, color: str) -> str:
    return f"""<div class='pb-wrap'>
      <div class='pb-fill' style='width:{pct*100:.0f}%;background:{color};'></div>
    </div>"""


def page_header(title: str, subtitle: str, badges_html: str = "") -> str:
    return f"""
    <div class='page-header'>
      <div><div class='ph-title'>{title}</div><div class='ph-sub'>{subtitle}</div></div>
      <div class='ph-badges'>{badges_html}</div>
    </div>"""


def info_banner(text: str) -> str:
    return f"<div class='info-banner'>ℹ️ {text}</div>"


def success_banner(text: str) -> str:
    return f"<div class='success-banner'>✅ {text}</div>"
