# -*- coding: utf-8 -*-
"""Pantalla de inicio — Oráculo Gótico Académico."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from ui.widgets import GothicCard, GothicButton, ornamento, StatCard


class HomeScreen:
    def __init__(self, win):
        self.win = win

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        n = len(ds.estudiantes)
        counts = ds.count_by_nivel()

        # ── Título ────────────────────────────────────────────────────
        tk.Label(parent, text="", bg=BG_MAIN).pack(pady=6)
        ornamento(parent).pack()
        tk.Label(parent, text="ORÁCULO GÓTICO ACADÉMICO",
                 font=("Palatino Linotype", 28, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(4, 0))
        tk.Label(parent,
                 text='"Los datos revelan el destino. La estadística ilumina las sombras del rendimiento."',
                 font=("Palatino Linotype", 12, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN, wraplength=700).pack(pady=4)
        ornamento(parent).pack(pady=(0, 16))

        # ── Tarjetas de resumen ────────────────────────────────────────
        cards_frame = tk.Frame(parent, bg=BG_MAIN)
        cards_frame.pack()

        StatCard(cards_frame, "Almas Registradas", str(n),
                 color=COLOR_GOLD).grid(row=0, column=0, padx=10, pady=6, ipadx=12)
        StatCard(cards_frame, "Alto Rendimiento", str(counts["Alto Rendimiento"]),
                 color=COLOR_ALTO).grid(row=0, column=1, padx=10, pady=6, ipadx=12)
        StatCard(cards_frame, "Nivel Medio", str(counts["Medio"]),
                 color=COLOR_MEDIO).grid(row=0, column=2, padx=10, pady=6, ipadx=12)
        StatCard(cards_frame, "En Riesgo", str(counts["En Riesgo"]),
                 color=COLOR_RIESGO).grid(row=0, column=3, padx=10, pady=6, ipadx=12)

        # ── Hipótesis ─────────────────────────────────────────────────
        hip = GothicCard(parent, padx=24, pady=14)
        hip.pack(padx=30, pady=14, fill="x")

        tk.Label(hip, text="Hipótesis a Validar (Opción B)",
                 font=("Palatino Linotype", 14, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")
        tk.Label(hip,
                 text="H₁: Los estudiantes que trabajan tienen un promedio menor a los que no trabajan.  (μ_trabaja < μ_no_trabaja)",
                 font=("Palatino Linotype", 12, "italic"),
                 fg="#A09060", bg=BG_CARD).pack(anchor="w", pady=(4, 0))
        tk.Label(hip,
                 text="H₀: μ_trabaja ≥ μ_no_trabaja   (trabajar no reduce el promedio)",
                 font=("Palatino Linotype", 11),
                 fg=COLOR_GOLD_DIM, bg=BG_CARD).pack(anchor="w", pady=(2, 0))
        tk.Label(hip,
                 text="Método: Prueba t de Welch para dos muestras independientes · Una cola izquierda · α = 0.05",
                 font=("Palatino Linotype", 10),
                 fg=COLOR_BORDER, bg=BG_CARD).pack(anchor="w", pady=(2, 0))

        # ── Acciones rápidas ──────────────────────────────────────────
        btn_frame = tk.Frame(parent, bg=BG_MAIN)
        btn_frame.pack(pady=14)

        GothicButton(btn_frame, text="⊕  Cargar / Importar Datos",
                     command=lambda: self.win.show("datos")).pack(side="left", padx=8)
        GothicButton(btn_frame, text="✦  Ver Profecía Individual",
                     accent=True,
                     command=lambda: self.win.show("profecia")).pack(side="left", padx=8)
        GothicButton(btn_frame, text="✧  Abrir El Grimorio",
                     command=lambda: self.win.show("grimorio")).pack(side="left", padx=8)

        # ── Info de flujo ─────────────────────────────────────────────
        info = GothicCard(parent, padx=20, pady=10)
        info.pack(padx=30, pady=(0, 16), fill="x")
        flujo = [
            ("⊕ Datos",         "Importa el CSV del Google Forms o ingresa datos manuales"),
            ("✦ La Profecía",   "Predicción de calificación final para un estudiante"),
            ("✧ El Grimorio",   "Estadística descriptiva, gráficas y prueba de hipótesis"),
            ("⚖ El Juicio Final","Simulación ¿qué pasa si mejora la asistencia?"),
            ("☽ Los Rituales",  "Recomendaciones automáticas por nivel de riesgo"),
        ]
        for icon_lbl, desc in flujo:
            row = tk.Frame(info, bg=BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=icon_lbl, font=("Palatino Linotype", 11, "bold"),
                     fg=COLOR_GOLD, bg=BG_CARD, width=20, anchor="w").pack(side="left")
            tk.Label(row, text=desc, font=("Palatino Linotype", 10),
                     fg=COLOR_GOLD_DIM, bg=BG_CARD, anchor="w").pack(side="left", padx=6)
