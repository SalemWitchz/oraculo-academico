# -*- coding: utf-8 -*-
"""☆ Créditos — Equipo de desarrollo y datos del proyecto."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER, COLOR_BORDER_LT,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from ui.widgets import GothicCard, ScrollableFrame

_EQUIPO = [
    ("Rodrigo Axel Pineda Arce",        "Líder de proyecto / Desarrollo"),
    ("Felix Eduardo Torres Grajales",    "Desarrollo estadístico"),
    ("Aldo Egalin Roblero Pérez",        "Diseño e interfaz"),
    ("Fátima Vázquez Méndez",           "Análisis de datos"),
    ("Sergio Alberto Solís Díaz",        "Documentación y pruebas"),
]

_INFO = {
    "Institución":  "Instituto Tecnológico",
    "Carrera":      "Ingeniería en Desarrollo y Tecnologías de Software",
    "Materia":      "Probabilidad y Estadística",
    "Grado y grupo":"4° \"O\"",
    "Docente":      "Ing. Víctor Sol Hernández",
    "Ciclo escolar": "2024 – 2025",
}


class CreditosScreen:
    def __init__(self, win):
        self.win = win

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)

        scroll = ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # ── Encabezado ────────────────────────────────────────────────
        tk.Label(inner, text="☆  CRÉDITOS  ☆",
                 font=("Palatino Linotype", 24, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(16, 2))
        tk.Label(inner,
                 text='"Sistema de Análisis Estadístico Académico — Hipótesis B"',
                 font=("Palatino Linotype", 12, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 4))
        tk.Frame(inner, bg=COLOR_BORDER, height=1).pack(fill="x", padx=40, pady=(4, 16))

        # ── Información del proyecto ──────────────────────────────────
        self._seccion_info(inner)

        # ── Equipo ────────────────────────────────────────────────────
        self._seccion_equipo(inner)

        # ── Pie decorativo ────────────────────────────────────────────
        tk.Label(inner, text="─── ◆ ◆ ◆ ───",
                 font=("Palatino Linotype", 13),
                 fg=COLOR_BORDER_LT, bg=BG_MAIN).pack(pady=(20, 4))
        tk.Label(inner,
                 text="Desarrollado con Python · Tkinter · Matplotlib · SciPy · NumPy",
                 font=("Palatino Linotype", 10, "italic"),
                 fg=COLOR_BORDER_LT, bg=BG_MAIN).pack(pady=(0, 4))
        tk.Label(inner,
                 text="Todos los métodos estadísticos siguen la notación y procedimientos\n"
                      "de la bibliografía oficial del plan de estudios.",
                 font=("Palatino Linotype", 10, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN,
                 justify="center").pack(pady=(2, 20))

    # ── Sub-secciones ─────────────────────────────────────────────────
    def _seccion_info(self, parent):
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(fill="x", padx=60, pady=(0, 12))

        tk.Label(card, text="INFORMACIÓN DEL PROYECTO",
                 font=("Palatino Linotype", 11, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD,
                 pady=10, padx=16).pack(anchor="w")
        tk.Frame(card, bg=COLOR_BORDER, height=1).pack(fill="x")

        for i, (k, v) in enumerate(_INFO.items()):
            bg = BG_CARD if i % 2 == 0 else BG_SECONDARY
            row = tk.Frame(card, bg=bg)
            row.pack(fill="x")
            tk.Label(row, text=k,
                     font=("Palatino Linotype", 11, "bold"),
                     fg=COLOR_GOLD_DIM, bg=bg,
                     width=20, anchor="w",
                     padx=16, pady=8).pack(side="left")
            tk.Label(row, text=v,
                     font=("Palatino Linotype", 11),
                     fg=COLOR_GOLD, bg=bg,
                     anchor="w", padx=8).pack(side="left")

    def _seccion_equipo(self, parent):
        tk.Label(parent, text="EQUIPO DE TRABAJO",
                 font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(8, 10))

        container = tk.Frame(parent, bg=BG_MAIN)
        container.pack(padx=60, fill="x")

        for i, (nombre, rol) in enumerate(_EQUIPO):
            card = GothicCard(container, padx=0, pady=0)
            card.pack(fill="x", pady=4)

            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(fill="x")

            # Número de integrante
            num_frame = tk.Frame(inner, bg="#111111", width=48)
            num_frame.pack(side="left", fill="y")
            num_frame.pack_propagate(False)
            tk.Label(num_frame, text=str(i + 1),
                     font=("Palatino Linotype", 20, "bold"),
                     fg=COLOR_BORDER_LT, bg="#111111").pack(expand=True)

            # Información
            info = tk.Frame(inner, bg=BG_CARD, padx=16, pady=10)
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=nombre.upper(),
                     font=("Palatino Linotype", 13, "bold"),
                     fg=COLOR_GOLD, bg=BG_CARD,
                     anchor="w").pack(anchor="w")
            tk.Label(info, text=rol,
                     font=("Palatino Linotype", 10, "italic"),
                     fg=COLOR_GOLD_DIM, bg=BG_CARD,
                     anchor="w").pack(anchor="w")
