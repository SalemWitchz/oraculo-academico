# -*- coding: utf-8 -*-
"""✧ El Grimorio de Datos — Estadística descriptiva, gráficas e hipótesis."""
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import (
    BG_MAIN, BG_CARD, COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT, COLOR_RED,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from stats import descriptiva as desc_mod
from stats.regresion_lineal import ajustar
from stats.prueba_hipotesis import prueba_correlacion
from ui.widgets import GothicCard, ScrollableFrame, SectionTitle, TablaSimple, ornamento


class GrimorioScreen:
    def __init__(self, win):
        self.win = win

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        est = ds.estudiantes

        if not est:
            tk.Label(parent, text="⚠ Sin datos. Ve a ⊕ Datos e importa un archivo.",
                     font=FONT_BODY, fg=COLOR_RIESGO, bg=BG_MAIN).pack(pady=40)
            return

        promedios   = ds.promedios()
        asistencias = ds.asistencias()

        scroll = ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # ── Título ────────────────────────────────────────────────────
        tk.Label(inner, text="✧  EL GRIMORIO DE DATOS  ✧",
                 font=("Palatino Linotype", 20, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(inner,
                 text='"Aquí yacen los secretos estadísticos del destino académico"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 10))

        # ── Fila: Descriptiva Promedios + Asistencia ─────────────────
        row1 = tk.Frame(inner, bg=BG_MAIN)
        row1.pack(fill="x", padx=16, pady=4)
        self._tabla_descriptiva(row1, promedios, "Promedio Final")
        self._tabla_descriptiva(row1, asistencias, "Asistencia (%)")

        # ── Fila: Regresión + Prueba de Hipótesis ────────────────────
        row2 = tk.Frame(inner, bg=BG_MAIN)
        row2.pack(fill="x", padx=16, pady=4)
        self._tabla_regresion(row2, asistencias, promedios)
        self._tabla_hipotesis(row2, asistencias, promedios)

        # ── Gráficas ─────────────────────────────────────────────────
        SectionTitle(inner, "Visualizaciones del Grimorio", bg=BG_MAIN
                     ).pack(anchor="w", padx=18, pady=(10, 4))

        self._graficas(inner, est, asistencias, promedios)

        tk.Label(inner, text="", bg=BG_MAIN).pack(pady=10)

    # ── Secciones ─────────────────────────────────────────────────────
    def _tabla_descriptiva(self, parent, datos, titulo):
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        tk.Label(card, text=f"Estadística Descriptiva · {titulo}",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, pady=6).pack(anchor="w", padx=10)
        resumen = desc_mod.calcular(datos)
        ic_inf, ic_sup = desc_mod.intervalo_confianza_media(datos)
        filas = resumen.tabla() + [
            ("IC 95% Media (inf)", f"{ic_inf:.4f}"),
            ("IC 95% Media (sup)", f"{ic_sup:.4f}"),
        ]
        TablaSimple(card, filas, bg=BG_CARD).pack(fill="x")

    def _tabla_regresion(self, parent, x, y):
        modelo = ajustar(x, y)
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        tk.Label(card, text="Regresión Lineal · Asistencia → Promedio",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, pady=6).pack(anchor="w", padx=10)
        TablaSimple(card, modelo.tabla(), bg=BG_CARD).pack(fill="x")

    def _tabla_hipotesis(self, parent, x, y):
        resultado = prueba_correlacion(x, y)
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)

        color_veredicto = COLOR_ALTO if resultado.rechazar_h0 else COLOR_RIESGO
        tk.Label(card, text="Prueba de Hipótesis — Hipótesis A",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, pady=6).pack(anchor="w", padx=10)
        TablaSimple(card, resultado.tabla()[:-1], bg=BG_CARD).pack(fill="x")
        # Conclusión resaltada
        concl = tk.Frame(card, bg=color_veredicto)
        concl.pack(fill="x", padx=0, pady=2)
        tk.Label(concl, text=resultado.conclusion,
                 font=("Palatino Linotype", 10, "italic"),
                 fg=BG_MAIN, bg=color_veredicto,
                 wraplength=320, justify="left", padx=8, pady=6).pack()

    # ── Gráficas matplotlib ───────────────────────────────────────────
    def _graficas(self, parent, est, asistencias, promedios):
        fig = plt.Figure(figsize=(12, 8), facecolor=BG_MAIN)

        # 1) Histograma de promedios
        ax1 = fig.add_subplot(2, 2, 1)
        self._hist_promedios(ax1, promedios)

        # 2) Dispersión asistencia vs promedio + recta
        ax2 = fig.add_subplot(2, 2, 2)
        self._scatter_regresion(ax2, asistencias, promedios)

        # 3) Boxplot por carrera
        ax3 = fig.add_subplot(2, 2, 3)
        self._boxplot_carrera(ax3, est)

        # 4) Pie de niveles
        ax4 = fig.add_subplot(2, 2, 4)
        self._pie_niveles(ax4, est)

        fig.tight_layout(pad=3)

        canvas_frame = tk.Frame(parent, bg=BG_MAIN)
        canvas_frame.pack(fill="x", padx=16, pady=4)
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _hist_promedios(self, ax, promedios):
        ax.set_facecolor(BG_CARD)
        ax.hist(promedios, bins=8, color=COLOR_PURPLE_LT,
                edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.9)
        ax.axvline(np.mean(promedios), color=COLOR_GOLD, linestyle="--",
                   linewidth=1.5, label=f"Media={np.mean(promedios):.2f}")
        ax.axvline(np.median(promedios), color=COLOR_RIESGO, linestyle=":",
                   linewidth=1.5, label=f"Mediana={np.median(promedios):.2f}")
        ax.set_title("Distribución de Promedios", color=COLOR_GOLD)
        ax.set_xlabel("Promedio Final")
        ax.set_ylabel("Frecuencia")
        ax.legend(fontsize=8)

    def _scatter_regresion(self, ax, x, y):
        ax.set_facecolor(BG_CARD)
        modelo = ajustar(x, y)
        xn = np.linspace(min(x), max(x), 100)
        yn = modelo.beta0 + modelo.beta1 * xn
        ax.scatter(x, y, color="#9B59B6", s=60, alpha=0.8, zorder=5,
                   edgecolors=COLOR_BORDER, linewidth=0.5, label="Estudiantes")
        ax.plot(xn, yn, color=COLOR_GOLD, linewidth=2,
                label=f"{modelo.ecuacion()}  R²={modelo.r2:.3f}")
        ax.set_title("Flujo del Destino: Asistencia → Promedio", color=COLOR_GOLD)
        ax.set_xlabel("Asistencia (%)")
        ax.set_ylabel("Promedio Final")
        ax.legend(fontsize=8)

    def _boxplot_carrera(self, ax, est):
        ax.set_facecolor(BG_CARD)
        carreras = sorted(set(e.carrera for e in est))
        data = [[e.promedio_final for e in est if e.carrera == c] for c in carreras]
        etqs = [c.replace("Ingeniería en ", "Ing. ").replace("Ingeniería ", "Ing. ")
                for c in carreras]
        bp = ax.boxplot(data, patch_artist=True, labels=etqs,
                        medianprops=dict(color=COLOR_GOLD, linewidth=2),
                        whiskerprops=dict(color=COLOR_GOLD_DIM),
                        capprops=dict(color=COLOR_GOLD_DIM),
                        flierprops=dict(markerfacecolor=COLOR_RED, markersize=5))
        for patch in bp["boxes"]:
            patch.set_facecolor(COLOR_PURPLE)
            patch.set_alpha(0.7)
        ax.set_title("Promedios por Carrera", color=COLOR_GOLD)
        ax.tick_params(axis="x", labelsize=7, rotation=15)
        ax.set_ylabel("Promedio Final")

    def _pie_niveles(self, ax, est):
        counts = {"Alto Rendimiento": 0, "Medio": 0, "En Riesgo": 0}
        for e in est:
            counts[e.nivel] += 1
        sizes  = list(counts.values())
        labels = list(counts.keys())
        colors = [COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO]
        wedges, texts, auto = ax.pie(
            sizes, labels=None, colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(edgecolor=BG_CARD, linewidth=2),
        )
        for t in auto:
            t.set_color(BG_MAIN)
            t.set_fontsize(9)
        ax.legend(wedges, labels, loc="lower center",
                  fontsize=8, framealpha=0.2)
        ax.set_facecolor(BG_CARD)
        ax.set_title("Clasificación de Destinos", color=COLOR_GOLD)
