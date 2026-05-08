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
    "Institución":   "Universidad Autónoma de Chiapas (UNACH)",
    "Carrera":       "Ingeniería en Desarrollo y Tecnologías de Software",
    "Materia":       "Probabilidad y Estadística",
    "Grado y grupo": "4° \"O\"",
    "Docente":       "Ing. Víctor Sol Hernández",
    "Ciclo escolar": "2024 – 2025",
}

_REFERENCIAS = [
    ("Walpole, R. E., Myers, R. H., & Myers, S. L. (2012).",
     "Probabilidad y estadística para ingeniería y ciencias (9.ª ed.). Pearson Educación."),
    ("Montgomery, D. C., & Runger, G. C. (2018).",
     "Applied statistics and probability for engineers (7th ed.). Wiley."),
    ("Devore, J. L. (2016).",
     "Probability and statistics for engineering and the sciences (9th ed.). Cengage Learning."),
    ("Anderson, D. R., Sweeney, D. J., & Williams, T. A. (2019).",
     "Estadística para negocios y economía (13.ª ed.). Cengage Learning."),
    ("Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020).",
     "Array programming with NumPy. Nature, 585, 357–362. https://doi.org/10.1038/s41586-020-2649-2"),
    ("Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020).",
     "SciPy 1.0: Fundamental algorithms for scientific computing in Python. "
     "Nature Methods, 17, 261–272. https://doi.org/10.1038/s41592-020-0772-5"),
    ("Hunter, J. D. (2007).",
     "Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. "
     "https://doi.org/10.1109/MCSE.2007.55"),
    ("Python Software Foundation. (2024).",
     "Python (Versión 3.x) [Software]. https://www.python.org"),
    ("McKinney, W. (2010).",
     "Data structures for statistical computing in Python. Proceedings of the 9th Python in "
     "Science Conference, 51–56. https://doi.org/10.25080/Majora-92bf1922-00a"),
]


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

        # ── Referencias ───────────────────────────────────────────────
        tk.Label(inner, text="─── ◆ ◆ ◆ ───",
                 font=("Palatino Linotype", 13),
                 fg=COLOR_BORDER_LT, bg=BG_MAIN).pack(pady=(20, 4))
        self._seccion_referencias(inner)

        # ── Pie ───────────────────────────────────────────────────────
        tk.Label(inner,
                 text="Desarrollado con Python · Tkinter · Matplotlib · SciPy · NumPy · pandas",
                 font=("Palatino Linotype", 9, "italic"),
                 fg=COLOR_BORDER_LT, bg=BG_MAIN).pack(pady=(12, 2))
        tk.Label(inner,
                 text="Universidad Autónoma de Chiapas (UNACH)  ·  2024–2025",
                 font=("Palatino Linotype", 9, "italic"),
                 fg=COLOR_BORDER_LT, bg=BG_MAIN).pack(pady=(0, 20))

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

    def _seccion_referencias(self, parent):
        tk.Label(parent, text="REFERENCIAS  (formato APA 7.ª edición)",
                 font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(4, 10))

        card = GothicCard(parent, padx=0, pady=0)
        card.pack(fill="x", padx=60, pady=(0, 8))

        for i, (autor, titulo) in enumerate(_REFERENCIAS):
            bg = BG_CARD if i % 2 == 0 else BG_SECONDARY
            row = tk.Frame(card, bg=bg, padx=16, pady=8)
            row.pack(fill="x")

            # Número de referencia
            tk.Label(row, text=f"[{i + 1}]",
                     font=("Palatino Linotype", 10, "bold"),
                     fg=COLOR_BORDER_LT, bg=bg,
                     width=4, anchor="nw").pack(side="left", anchor="n")

            # Bloque autor + título con sangría francesa
            bloque = tk.Frame(row, bg=bg)
            bloque.pack(side="left", fill="x", expand=True)

            tk.Label(bloque, text=autor,
                     font=("Palatino Linotype", 10, "bold"),
                     fg=COLOR_GOLD, bg=bg,
                     anchor="w", justify="left",
                     wraplength=820).pack(anchor="w")
            tk.Label(bloque, text="      " + titulo,
                     font=("Palatino Linotype", 10),
                     fg=COLOR_GOLD_DIM, bg=bg,
                     anchor="w", justify="left",
                     wraplength=820).pack(anchor="w")

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
