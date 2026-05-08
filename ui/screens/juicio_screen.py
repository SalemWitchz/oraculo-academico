# -*- coding: utf-8 -*-
"""⚖ El Juicio Final — Simulación ¿qué pasa si dejas de trabajar? (Hipótesis B)"""
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import stats as sp_stats

from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY, BG_INPUT,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER, COLOR_BORDER_LT,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from stats.modelo_prediccion import Oraculo
from ui.widgets import (GothicCard, GothicButton, SectionTitle,
                         Medidor, BarraProbabilidad, color_nivel)


class JuicioScreen:
    def __init__(self, win):
        self.win = win
        self._oraculo = Oraculo()
        self._medidor: Medidor | None = None
        self._barra: BarraProbabilidad | None = None
        self._lbl_cal: tk.Label | None = None
        self._lbl_nivel: tk.Label | None = None
        self._lbl_profecia: tk.Label | None = None
        self._fig_frame: tk.Frame | None = None
        self._trabaja_sim: tk.BooleanVar | None = None
        self._calculo_vars: dict = {}   # etiqueta → tk.StringVar para filas de cálculo

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        est = ds.estudiantes

        tk.Label(parent, text="⚖  EL JUICIO FINAL  ⚖",
                 font=("Palatino Linotype", 22, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(parent,
                 text='"Simula el destino: ¿qué profecía obtienes si cambias tu situación laboral?"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 10))

        if not est or len(est) < 3:
            tk.Label(parent, text="⚠ Necesitas al menos 3 almas registradas.",
                     font=FONT_BODY, fg=COLOR_RIESGO, bg=BG_MAIN).pack(pady=30)
            return

        prom_trab = [e.promedio_final for e in est if     e.trabaja]
        prom_no   = [e.promedio_final for e in est if not e.trabaja]
        self._oraculo.entrenar(prom_trab, prom_no)

        # ── Selector de estudiante ─────────────────────────────────────
        top = GothicCard(parent, padx=20, pady=10)
        top.pack(padx=24, fill="x", pady=(0, 8))

        tk.Label(top, text="Estudiante a juzgar:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")
        nombres = [str(e) for e in est]
        self._var_est = tk.StringVar(value=nombres[0])
        opt = tk.OptionMenu(top, self._var_est, *nombres,
                            command=lambda _: self._al_cambiar_estudiante(est))
        opt.config(font=FONT_BODY, bg=BG_SECONDARY, fg=COLOR_GOLD,
                   relief="flat", bd=0, activebackground=COLOR_PURPLE)
        opt["menu"].config(bg=BG_SECONDARY, fg=COLOR_GOLD, font=FONT_SMALL)
        opt.pack(fill="x", pady=4)

        # ── Controles de simulación ────────────────────────────────────
        ctrl = GothicCard(parent, padx=20, pady=10)
        ctrl.pack(padx=24, fill="x", pady=(0, 8))

        tk.Label(ctrl, text="Simular situación laboral:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 6))

        self._trabaja_sim = tk.BooleanVar(value=True)
        btn_row = tk.Frame(ctrl, bg=BG_CARD)
        btn_row.pack(anchor="w")

        self._btn_trabaja = tk.Radiobutton(
            btn_row, text="  Trabaja  ", variable=self._trabaja_sim, value=True,
            font=("Palatino Linotype", 12, "bold"),
            fg=COLOR_RIESGO, bg=BG_CARD, selectcolor=COLOR_PURPLE,
            activebackground=BG_CARD, activeforeground=COLOR_RIESGO,
            command=self._recalcular, indicatoron=True)
        self._btn_trabaja.pack(side="left", padx=(0, 16))

        self._btn_no_trabaja = tk.Radiobutton(
            btn_row, text="  No trabaja  ", variable=self._trabaja_sim, value=False,
            font=("Palatino Linotype", 12, "bold"),
            fg=COLOR_ALTO, bg=BG_CARD, selectcolor=COLOR_PURPLE,
            activebackground=BG_CARD, activeforeground=COLOR_ALTO,
            command=self._recalcular, indicatoron=True)
        self._btn_no_trabaja.pack(side="left")

        GothicButton(ctrl, text="⚖  Pronunciar el Juicio",
                     accent=True, command=self._recalcular).pack(pady=(10, 0))

        # ── Procedimiento del cálculo ─────────────────────────────────
        calc_card = GothicCard(parent, padx=0, pady=0)
        calc_card.pack(padx=24, fill="x", pady=(0, 8))

        hdr_calc = tk.Frame(calc_card, bg="#111111")
        hdr_calc.pack(fill="x")
        tk.Label(hdr_calc, text="∑",
                 font=("Palatino Linotype", 14, "bold"),
                 fg=COLOR_GOLD, bg="#111111", width=4, pady=6).pack(side="left", padx=(8, 0))
        tk.Label(hdr_calc, text="Procedimiento del Cálculo — Fórmulas con datos reales",
                 font=("Palatino Linotype", 11, "bold"),
                 fg=COLOR_GOLD, bg="#111111", anchor="w").pack(side="left", padx=6)
        tk.Frame(calc_card, bg=COLOR_BORDER, height=1).pack(fill="x")

        self._calculo_body = tk.Frame(calc_card, bg=BG_CARD, padx=16, pady=8)
        self._calculo_body.pack(fill="x")

        _filas = [
            ("grupo_sim",    "Grupo simulado:"),
            ("media_grupo",  "Media del grupo  (μ):"),
            ("desv_grupo",   "Desv. estándar grupo  (σ):"),
            ("horas",        "Horas de estudio del alumno:"),
            ("ajuste_form",  "Ajuste por horas  (fórmula):"),
            ("ajuste_val",   "Ajuste calculado:"),
            ("cal_form",     "Calificación predicha  (fórmula):"),
            ("cal_val",      "Calificación predicha  (resultado):"),
            ("prob_form",    "P(aprobar ≥ 6)  (fórmula):"),
            ("prob_val",     "P(aprobar ≥ 6)  (resultado):"),
            ("delta",        "Δ respecto a situación real:"),
        ]
        self._calculo_vars = {}
        for key, etiqueta in _filas:
            var = tk.StringVar(value="—")
            self._calculo_vars[key] = var
            row = tk.Frame(self._calculo_body, bg=BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=etiqueta,
                     font=("Palatino Linotype", 9, "bold"),
                     fg=COLOR_BORDER_LT, bg=BG_CARD,
                     width=30, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var,
                     font=("Courier New", 10),
                     fg=COLOR_GOLD_DIM, bg=BG_CARD,
                     anchor="w", justify="left", wraplength=700).pack(side="left", fill="x", expand=True)

        # ── Área de resultado ─────────────────────────────────────────
        result_row = tk.Frame(parent, bg=BG_MAIN)
        result_row.pack(fill="both", expand=True, padx=24, pady=4)

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

        right = tk.Frame(result_row, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True)

        self._lbl_profecia = tk.Label(right, text="",
                                       font=("Palatino Linotype", 12, "italic"),
                                       fg=COLOR_GOLD_DIM, bg=BG_MAIN,
                                       wraplength=450, justify="left")
        self._lbl_profecia.pack(anchor="w", pady=(0, 8))

        self._fig_frame = tk.Frame(right, bg=BG_MAIN)
        self._fig_frame.pack(fill="both", expand=True)

        self._al_cambiar_estudiante(est)

    # ── Helpers ───────────────────────────────────────────────────────
    def _al_cambiar_estudiante(self, est):
        nombre = self._var_est.get()
        e = next((x for x in est if str(x) == nombre), None)
        if e and self._trabaja_sim is not None:
            self._trabaja_sim.set(e.trabaja)
        self._recalcular()

    def _recalcular(self):
        ds = DataStore.get()
        est = ds.estudiantes
        nombre = self._var_est.get()
        e = next((x for x in est if str(x) == nombre), None)
        if e is None:
            return

        trabaja_sim  = self._trabaja_sim.get()
        resultado    = self._oraculo.predecir(trabaja_sim,  e.horas_estudio)
        res_real     = self._oraculo.predecir(e.trabaja,    e.horas_estudio)

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
            delta = resultado.calificacion_predicha - res_real.calificacion_predicha
            signo = "+" if delta >= 0 else ""
            estado_real = "Trabaja" if e.trabaja else "No trabaja"
            estado_sim  = "Trabaja" if trabaja_sim  else "No trabaja"
            self._lbl_profecia.config(
                text=f'"{resultado.profecia}"\n\n'
                     f'Real ({estado_real}): {res_real.calificacion_predicha:.2f}  →  '
                     f'Sim. ({estado_sim}): {resultado.calificacion_predicha:.2f}  '
                     f'({signo}{delta:.2f})'
            )

        # ── Actualizar procedimiento del cálculo ──────────────────────
        if self._calculo_vars:
            self._actualizar_calculo(e, trabaja_sim, resultado, res_real)

        self._grafica_comparativa(e, trabaja_sim)

    def _actualizar_calculo(self, e, trabaja_sim: bool, resultado, res_real):
        orac = self._oraculo
        mu   = orac.media_trabaja   if trabaja_sim else orac.media_no_trabaja
        se   = orac._s_trab         if trabaja_sim else orac._s_no
        hrs  = e.horas_estudio
        ajuste_raw = (hrs - 10) * 0.04
        cal_raw    = mu + ajuste_raw
        cal        = min(10.0, max(0.0, cal_raw))
        prob_ap    = float(sp_stats.norm.sf(5.9, loc=cal, scale=se))
        prob_ap    = max(0.0, min(1.0, prob_ap))

        grupo_str  = "Trabaja" if trabaja_sim else "No trabaja"
        delta      = resultado.calificacion_predicha - res_real.calificacion_predicha
        delta_sign = f"+{delta:.4f}" if delta >= 0 else f"{delta:.4f}"
        real_str   = "Trabaja" if e.trabaja else "No trabaja"

        v = self._calculo_vars
        v["grupo_sim"].set(grupo_str)
        v["media_grupo"].set(
            f"{mu:.4f}   ← promedio observado de todos los alumnos del grupo '{grupo_str}'"
        )
        v["desv_grupo"].set(
            f"{se:.4f}   ← desviación estándar del grupo '{grupo_str}'"
        )
        v["horas"].set(f"{hrs:.1f} hrs/sem")
        v["ajuste_form"].set("ajuste  =  (horas_estudio − 10)  ×  0.04")
        v["ajuste_val"].set(
            f"({hrs:.1f} − 10)  ×  0.04  =  {hrs-10:.1f}  ×  0.04  =  {ajuste_raw:+.4f} puntos"
        )
        if cal_raw == cal:
            v["cal_form"].set("calificación  =  μ  +  ajuste")
            v["cal_val"].set(
                f"{mu:.4f}  +  ({ajuste_raw:+.4f})  =  {cal:.4f}"
            )
        else:
            v["cal_form"].set("calificación  =  clamp(μ + ajuste, 0, 10)")
            v["cal_val"].set(
                f"clamp({mu:.4f} + ({ajuste_raw:+.4f}), 0, 10)  =  clamp({cal_raw:.4f}, 0, 10)  =  {cal:.4f}"
            )
        v["prob_form"].set(
            "P(aprobar)  =  P(X ≥ 6)  =  1 − Φ((5.9 − μ_pred) / σ_grupo)"
        )
        z_val = (5.9 - cal) / se if se > 0 else 0
        v["prob_val"].set(
            f"1 − Φ((5.9 − {cal:.4f}) / {se:.4f})  "
            f"=  1 − Φ({z_val:.4f})  =  {prob_ap:.4f}  ({prob_ap*100:.1f}%)"
        )
        v["delta"].set(
            f"Sim. ({grupo_str}): {resultado.calificacion_predicha:.4f}  −  "
            f"Real ({real_str}): {res_real.calificacion_predicha:.4f}  =  {delta_sign}"
        )

    def _grafica_comparativa(self, e, trabaja_sim: bool):
        if self._fig_frame is None:
            return
        for w in self._fig_frame.winfo_children():
            w.destroy()

        m_trab = self._oraculo.media_trabaja
        m_no   = self._oraculo.media_no_trabaja

        fig = plt.Figure(figsize=(6, 3.2), facecolor=BG_MAIN)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(BG_CARD)

        grupos  = ["Trabaja", "No trabaja"]
        medias  = [m_trab, m_no]
        colores = [COLOR_RIESGO, COLOR_ALTO]
        bars = ax.bar(grupos, medias, color=colores, alpha=0.75,
                      edgecolor=COLOR_BORDER, linewidth=0.8, width=0.4)
        ax.bar_label(bars, fmt="%.2f", color=COLOR_GOLD, fontsize=9, padding=3)

        ax.axhline(e.promedio_final, color=COLOR_GOLD,
                   linestyle="--", linewidth=1.5,
                   label=f"Promedio real de {e.nombre.split()[0]}: {e.promedio_final:.2f}")
        ax.axhline(6, color=COLOR_RIESGO, linestyle=":", linewidth=1, alpha=0.5,
                   label="Mínimo aprobatorio (6)")

        ax.set_ylim(0, 10.5)
        ax.set_title("Promedio Esperado por Situación Laboral", color=COLOR_GOLD)
        ax.set_ylabel("Promedio Esperado")
        ax.legend(fontsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
