# -*- coding: utf-8 -*-
"""Paleta gótica y constantes globales."""

# ── Colores ──────────────────────────────────────────────────────────────────
BG_MAIN      = "#0A0008"
BG_SECONDARY = "#0F0018"
BG_CARD      = "#130020"
BG_SIDEBAR   = "#0D0015"
BG_INPUT     = "#0F0018"

COLOR_GOLD        = "#C9A96E"
COLOR_GOLD_BRIGHT = "#F0C070"
COLOR_GOLD_DIM    = "#7A6040"
COLOR_PURPLE      = "#4A0E6E"
COLOR_PURPLE_LT   = "#6B21A8"
COLOR_RED         = "#8B0000"
COLOR_RED_LT      = "#C0392B"
COLOR_BORDER      = "#3D1C5E"

COLOR_ALTO   = "#4CAF50"
COLOR_MEDIO  = "#FF9800"
COLOR_RIESGO = "#F44336"

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

# ── Matplotlib gótico ─────────────────────────────────────────────────────────
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
    "grid.color":             "#2A1040",
    "grid.alpha":             0.5,
    "grid.linestyle":         "--",
    "text.color":             COLOR_GOLD,
    "legend.facecolor":       BG_CARD,
    "legend.edgecolor":       COLOR_BORDER,
    "legend.labelcolor":      COLOR_GOLD_DIM,
    "legend.fontsize":        9,
    "lines.linewidth":        2,
    "scatter.marker":         "o",
}
