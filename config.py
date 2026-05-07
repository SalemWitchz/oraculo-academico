# -*- coding: utf-8 -*-
"""Paleta monocromática — blanco, negro y escala de grises."""

# ── Fondos ────────────────────────────────────────────────────────────────────
BG_MAIN      = "#0A0A0A"
BG_SECONDARY = "#111111"
BG_CARD      = "#1A1A1A"
BG_SIDEBAR   = "#0C0C0C"
BG_INPUT     = "#141414"

# ── Texto / Interactivos ──────────────────────────────────────────────────────
COLOR_GOLD        = "#F0F0F0"   # texto principal → blanco suave
COLOR_GOLD_BRIGHT = "#FFFFFF"   # énfasis → blanco puro
COLOR_GOLD_DIM    = "#999999"   # texto secundario → gris medio
COLOR_PURPLE      = "#252525"   # bg botón normal → gris oscuro
COLOR_PURPLE_LT   = "#383838"   # bg botón hover  → gris claro
COLOR_RED         = "#F0F0F0"   # btn accent bg   → blanco (invertido)
COLOR_RED_LT      = "#CCCCCC"   # btn accent hover
COLOR_BORDER      = "#2E2E2E"   # bordes → gris muy oscuro
COLOR_BORDER_LT   = "#555555"   # bordes resaltados

# ── Estado académico (mantener legibilidad funcional) ─────────────────────────
COLOR_ALTO   = "#EEEEEE"    # alto rendimiento  → blanco/gris claro
COLOR_MEDIO  = "#888888"    # nivel medio       → gris medio
COLOR_RIESGO = "#DD3322"    # en riesgo         → rojo oscuro (alerta)

# ── Tipografía ────────────────────────────────────────────────────────────────
_SERIF = "Palatino Linotype"
FONT_TITLE    = (_SERIF, 26, "bold")
FONT_HEADING  = (_SERIF, 16, "bold")
FONT_SUBHEAD  = (_SERIF, 13, "bold")
FONT_BODY     = (_SERIF, 12)
FONT_SMALL    = (_SERIF, 10)
FONT_TINY     = (_SERIF,  9)
FONT_STAT     = (_SERIF, 38, "bold")
FONT_NAV      = (_SERIF, 13)
FONT_PROPHECY = (_SERIF, 14, "italic")
FONT_ORACLE   = (_SERIF, 48, "bold")

# ── Ventana ───────────────────────────────────────────────────────────────────
WIN_W         = 1280
WIN_H         = 780
SIDEBAR_W     = 215

# ── Dominio ───────────────────────────────────────────────────────────────────
CARRERAS = [
    "Ingeniería en Sistemas",
    "Ingeniería Industrial",
    "Administración",
    "Contabilidad",
    "Diseño Gráfico",
    "Mercadotecnia",
    "Derecho",
]
MATERIAS  = ["Probabilidad y Estadística", "Cálculo Diferencial",
             "Álgebra Lineal", "Programación", "Bases de Datos"]
SEMESTRES = list(range(1, 10))

# ── Matplotlib monocromático ──────────────────────────────────────────────────
MPL_STYLE = {
    "figure.facecolor":       BG_MAIN,
    "figure.edgecolor":       COLOR_BORDER,
    "axes.facecolor":         BG_CARD,
    "axes.edgecolor":         COLOR_BORDER,
    "axes.labelcolor":        COLOR_GOLD_DIM,
    "axes.titlecolor":        COLOR_GOLD,
    "axes.titlesize":         12,
    "axes.labelsize":         10,
    "axes.grid":              True,
    "axes.spines.top":        False,
    "axes.spines.right":      False,
    "xtick.color":            COLOR_GOLD_DIM,
    "ytick.color":            COLOR_GOLD_DIM,
    "xtick.labelsize":        9,
    "ytick.labelsize":        9,
    "grid.color":             "#252525",
    "grid.alpha":             0.6,
    "grid.linestyle":         "--",
    "text.color":             COLOR_GOLD,
    "legend.facecolor":       BG_CARD,
    "legend.edgecolor":       COLOR_BORDER,
    "legend.labelcolor":      COLOR_GOLD_DIM,
    "legend.fontsize":        9,
    "lines.linewidth":        2,
    "scatter.marker":         "o",
}
