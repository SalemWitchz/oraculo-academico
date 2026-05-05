# -*- coding: utf-8 -*-
"""⚖ El Juicio Final — Simulación ¿qué pasa si mejoras?"""
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from stats.modelo_prediccion import Oraculo
from stats.regresion_lineal import ajustar
from ui.widgets import (GothicCard, GothicButton, SectionTitle,
                         Medidor, BarraProbabilidad, color_nivel, ornamento)


class JuicioScreen:
    def __init__(self, win):
        self.win = win
        self._oraculo = Oraculo()
        self._medidor: Medidor | None = None
        self._barra: BarraProbabilidad | None = None
        self._lbl_cal: tk.Label | None = None
        self._lbl_nivel: tk.Label | None = None
        self._lbl_profecia: tk.Label | None = None
        self._canvas_fig = None

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        est = ds.estudiantes

        tk.Label(parent, text="⚖  EL JUICIO FINAL  ⚖",
                 font=("Palatino Linotype", 22, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(parent,
                 text='"Simula el destino: ¿qué profecía obtienes si cambias tu rumbo?"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 10))

        if not est or len(est) < 3:
            tk.Label(parent, text="⚠ Necesitas al menos 3 almas registradas.",
                     font=FONT_BODY, fg=COLOR_RIESGO, bg=BG_MAIN).pack(pady=30)
            return

        # Entrenar modelo
        self._oraculo.entrenar(ds.asistencias(), ds.promedios())

        # ── Selector de estudiante ─────────────────────────────────────
        top = GothicCard(parent, padx=20, pady=10)
        top.pack(padx=24, fill="x", pady=(0, 8))

        tk.Label(top, text="Estudiante a juzgar:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")
        nombres = [str(e) for e in est]
        self._var_est = tk.StringVar(value=nombres[0])
        opt = tk.OptionMenu(top, self._var_est, *nombres,
                            command=lambda _: self._recalcular())
        opt.config(font=FONT_BODY, bg=BG_SECONDARY, fg=COLOR_GOLD,
                   relief="flat", bd=0, activebackground=COLOR_PURPLE)
        opt["menu"].config(bg=BG_SECONDARY, fg=COLOR_GOLD, font=FONT_SMALL)
        opt.pack(fill="x", pady=4)

        # ── Controles de simulación ────────────────────────────────────
        ctrl = GothicCard(parent, padx=20, pady=10)
        ctrl.pack(padx=24, fill="x", pady=(0, 8))

        # Asistencia slider
        self._asist_var = tk.DoubleVar(value=75)
        self._estudio_var = tk.DoubleVar(value=10)

        self._add_slider(ctrl, "Asistencia simulada (%)", self._asist_var, 0, 100)
        self._add_slider(ctrl, "Horas de estudio/semana", self._estudio_var, 0, 30)

        GothicButton(ctrl, text="⚖  Pronunciar el Juicio",
                     accent=True, command=self._recalcular).pack(pady=(8, 0))

        # ── Área de resultado ─────────────────────────────────────────
        result_row = tk.Frame(parent, bg=BG_MAIN)
        result_row.pack(fill="both", expand=True, padx=24, pady=4)

        # Panel izquierdo: Medidor
        left = GothicCard(result_row, padx=14, pady=10)
        left.pack(side="left", fill="y", padx=(0, 8))
        tk.Label(left, text="Destino Predicho",
                 font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack()
        self._medidor = Medidor(left)
        self._medidor.pack()
        self._lbl_cal = tk.Label(left, text="", font=("Palatino Linotype", 14, "bold"),
                                  fg=COLOR_GOLD, bg=BG_CARD)
        self._lbl_cal.pack()
        self._lbl_nivel = tk.Label(left, text="",
                                    font=("Palatino Linotype", 11, "italic"),
                                    fg=COLOR_GOLD_DIM, bg=BG_CARD)
        self._lbl_nivel.pack(pady=2)
        self._barra = BarraProbabilidad(left, width=200)
        self._barra.pack(pady=6)

        # Panel derecho: comparativa + gráfica
        right = tk.Frame(result_row, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True)

        self._lbl_profecia = tk.Label(right, text="",
                                       font=("Palatino Linotype", 12, "italic"),
                                       fg="#A09060", bg=BG_MAIN,
                                       wraplength=450, justify="left")
        self._lbl_profecia.pack(anchor="w", pady=(0, 8))

        self._fig_frame = tk.Frame(right, bg=BG_MAIN)
        self._fig_frame.pack(fill="both", expand=True)

        # Cargar estudiante inicial
        self._set_sliders_from_selected(est)
        self._recalcular()

    # ── Helpers ───────────────────────────────────────────────────────
    def _add_slider(self, parent, label, var, lo, hi):
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(fill="x", pady=3)
        tk.Label(f, text=label, font=FONT_SMALL, fg=COLOR_GOLD_DIM,
                 bg=BG_CARD, width=28, anchor="w").pack(side="left")
        slider = tk.Scale(f, from_=lo, to=hi, orient="horizontal",
                          variable=var, resolution=1,
                          bg=BG_CARD, fg=COLOR_GOLD, troughcolor=COLOR_PURPLE,
                          highlightthickness=0, font=FONT_TINY, length=220,
                          command=lambda _: self._recalcular())
        slider.pack(side="left")
        lbl_val = tk.Label(f, textvariable=var, font=FONT_SMALL,
                           fg=COLOR_GOLD, bg=BG_CARD, width=5)
        lbl_val.pack(side="left")

    def _set_sliders_from_selected(self, est):
        nombre = self._var_est.get()
        e = next((x for x in est if str(x) == nombre), None)
        if e:
            self._asist_var.set(e.porcentaje_asistencia)
            self._estudio_var.set(e.horas_estudio)

    def _recalcular(self):
        ds = DataStore.get()
        est = ds.estudiantes
        nombre = self._var_est.get()
        e = next((x for x in est if str(x) == nombre), None)
        if e is None:
            return

        asist_sim  = self._asist_var.get()
        hest_sim   = self._estudio_var.get()
        resultado  = self._oraculo.predecir(asist_sim, hest_sim, e.trabaja)
        resultado_actual = self._oraculo.predecir(
            e.porcentaje_asistencia, e.horas_estudio, e.trabaja)

        # Actualizar medidor
        if self._medidor:
            self._medidor.set_value(resultado.calificacion_predicha)
        if self._lbl_cal:
            self._lbl_cal.config(text=f"{resultado.calificacion_predicha:.2f} / 10")
        if self._lbl_nivel:
            self._lbl_nivel.config(text=resultado.nivel,
                                   fg=color_nivel(resultado.nivel))
        if self._barra:
            self._barra.set_value(resultado.prob_aprobar)
        if self._lbl_profecia:
            delta = resultado.calificacion_predicha - resultado_actual.calificacion_predicha
            signo = "+" if delta >= 0 else ""
            self._lbl_profecia.config(
                text=f'"{resultado.profecia}"\n\n'
                     f'Actual: {resultado_actual.calificacion_predicha:.2f}  →  '
                     f'Simulado: {resultado.calificacion_predicha:.2f}  '
                     f'({signo}{delta:.2f})'
            )

        # Gráfica de escenarios
        self._grafica_escenarios(e, resultado_actual.calificacion_predicha)

    def _grafica_escenarios(self, e, cal_actual):
        for w in self._fig_frame.winfo_children():
            w.destroy()

        modelo = self._oraculo.modelo
        if modelo is None:
            return

        asist_range = np.linspace(0, 100, 200)
        cal_range   = np.clip(modelo.beta0 + modelo.beta1 * asist_range, 0, 10)

        fig = plt.Figure(figsize=(6, 3.2), facecolor=BG_MAIN)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(BG_CARD)

        ax.plot(asist_range, cal_range, color=COLOR_PURPLE_LT, linewidth=2,
                label="Curva del Destino")
        ax.axhline(6, color=COLOR_RIESGO, linestyle="--", linewidth=1, alpha=0.7,
                   label="Mínimo aprobatorio (6)")
        ax.axhline(8.5, color=COLOR_ALTO, linestyle="--", linewidth=1, alpha=0.7,
                   label="Alto Rendimiento (8.5)")

        # Punto actual
        ax.scatter([e.porcentaje_asistencia], [cal_actual],
                   color=COLOR_RIESGO, s=90, zorder=6, label="Actual")
        # Punto simulado
        asist_sim = self._asist_var.get()
        cal_sim = np.clip(modelo.beta0 + modelo.beta1 * asist_sim, 0, 10)
        ax.scatter([asist_sim], [cal_sim],
                   color=COLOR_ALTO, s=90, zorder=6, label="Simulado")
        # Flecha
        ax.annotate("", xy=(asist_sim, cal_sim),
                    xytext=(e.porcentaje_asistencia, cal_actual),
                    arrowprops=dict(arrowstyle="->", color=COLOR_GOLD, lw=1.5))

        ax.set_xlabel("Asistencia (%)")
        ax.set_ylabel("Calificación Predicha")
        ax.set_title("Curva del Destino — Simulación", color=COLOR_GOLD)
        ax.legend(fontsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
