# -*- coding: utf-8 -*-
"""✧ El Grimorio de Datos — Estadística descriptiva, gráficas e hipótesis B."""
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm as _norm

from config import (
    BG_MAIN, BG_CARD, COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT, COLOR_RED,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from stats import descriptiva as desc_mod
from stats.prueba_hipotesis import prueba_hipotesis_B
from ui.widgets import GothicCard, ScrollableFrame, SectionTitle, TablaSimple


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

        prom_trab  = [e.promedio_final for e in est if     e.trabaja]
        prom_no    = [e.promedio_final for e in est if not e.trabaja]

        scroll = ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # ── Título ────────────────────────────────────────────────────
        hdr_row = tk.Frame(inner, bg=BG_MAIN)
        hdr_row.pack(fill="x", padx=18, pady=(8, 0))

        tk.Label(hdr_row, text="✧  EL GRIMORIO DE DATOS  ✧",
                 font=("Palatino Linotype", 20, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(side="left")

        from ui.widgets import GothicButton
        GothicButton(hdr_row, text="⤓  Exportar PDF",
                     command=lambda: self._exportar_pdf(parent)).pack(
            side="right", padx=4)

        tk.Label(inner,
                 text='"Aquí yacen los secretos estadísticos del destino académico"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 10))

        # ── Fila: Descriptiva Promedios + Asistencia ─────────────────
        row1 = tk.Frame(inner, bg=BG_MAIN)
        row1.pack(fill="x", padx=16, pady=4)
        self._tabla_descriptiva(row1, promedios,   "Promedio Final")
        self._tabla_descriptiva(row1, asistencias, "Asistencia (%)")

        # ── Fila: Grupos (H_B) + Prueba de Hipótesis B ───────────────
        row2 = tk.Frame(inner, bg=BG_MAIN)
        row2.pack(fill="x", padx=16, pady=4)
        self._tabla_grupos(row2, prom_trab, prom_no)
        self._tabla_hipotesis_B(row2, prom_trab, prom_no)

        # ── Gráficas ─────────────────────────────────────────────────
        SectionTitle(inner, "Visualizaciones del Grimorio", bg=BG_MAIN
                     ).pack(anchor="w", padx=18, pady=(10, 4))

        self._graficas(inner, est, prom_trab, prom_no, promedios)

        # Extended charts — only when CSV extended fields are present
        if any(e.nivel_estres for e in est):
            SectionTitle(inner, "Estadísticas Ampliadas — Datos del Formulario", bg=BG_MAIN
                         ).pack(anchor="w", padx=18, pady=(10, 4))
            self._graficas_extendidas(inner, est)

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

    def _tabla_grupos(self, parent, prom_trab, prom_no):
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        tk.Label(card, text="Comparación de Grupos — Hipótesis B",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, pady=6).pack(anchor="w", padx=10)

        def fmt(vals):
            if not vals:
                return ("0", "—", "—")
            a = np.array(vals, dtype=float)
            return (str(len(a)), f"{a.mean():.4f}",
                    f"{a.std(ddof=1):.4f}" if len(a) > 1 else "—")

        n1, m1, s1 = fmt(prom_trab)
        n2, m2, s2 = fmt(prom_no)
        filas = [
            ("",                   "Trabaja",  "No trabaja"),
            ("n",                  n1,         n2),
            ("Media (x̄)",         m1,         m2),
            ("Desv. estándar (s)", s1,         s2),
        ]

        for i, fila in enumerate(filas):
            bg = BG_CARD if i % 2 == 0 else "#111111"
            row = tk.Frame(card, bg=bg)
            row.pack(fill="x")
            widths = [22, 12, 12]
            for j, (cell, w) in enumerate(zip(fila, widths)):
                anchor = "w" if j == 0 else "center"
                tk.Label(row, text=cell, font=FONT_SMALL,
                         fg=COLOR_GOLD if i == 0 else COLOR_GOLD_DIM,
                         bg=bg, width=w, anchor=anchor,
                         padx=6, pady=3).pack(side="left")

    def _tabla_hipotesis_B(self, parent, prom_trab, prom_no):
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        tk.Label(card, text="Prueba de Hipótesis — Hipótesis B (Student)",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, pady=6).pack(anchor="w", padx=10)

        if len(prom_trab) < 2 or len(prom_no) < 2:
            tk.Label(card,
                     text="⚠ Se necesitan al menos 2 estudiantes en cada grupo.",
                     font=FONT_SMALL, fg=COLOR_RIESGO, bg=BG_CARD,
                     padx=10, pady=6).pack(anchor="w")
            return

        res = prueba_hipotesis_B(prom_trab, prom_no)
        color_veredicto = COLOR_ALTO if res.rechazar_h0 else COLOR_RIESGO

        TablaSimple(card, res.tabla_prueba()[:-1], bg=BG_CARD).pack(fill="x")
        concl = tk.Frame(card, bg=color_veredicto)
        concl.pack(fill="x", padx=0, pady=2)
        tk.Label(concl, text=res.conclusion,
                 font=("Palatino Linotype", 10, "italic"),
                 fg=BG_MAIN, bg=color_veredicto,
                 wraplength=320, justify="left", padx=8, pady=6).pack()

    # ── Gráficas matplotlib ───────────────────────────────────────────
    def _graficas(self, parent, est, prom_trab, prom_no, promedios):
        fig = plt.Figure(figsize=(12, 8), facecolor=BG_MAIN)

        # 1) Histograma de promedios
        ax1 = fig.add_subplot(2, 2, 1)
        self._hist_promedios(ax1, promedios)

        # 2) Histogramas superpuestos: trabaja vs no trabaja
        ax2 = fig.add_subplot(2, 2, 2)
        self._hist_grupos(ax2, prom_trab, prom_no)

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
        mu  = np.mean(promedios)
        sig = np.std(promedios, ddof=1)
        ax.hist(promedios, bins=8, color=COLOR_PURPLE_LT,
                edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.9, density=True)
        x_rng = np.linspace(mu - 4 * sig, mu + 4 * sig, 300)
        ax.plot(x_rng, _norm.pdf(x_rng, mu, sig),
                color=COLOR_GOLD, linewidth=2,
                label=f"N(μ={mu:.2f}, σ={sig:.2f})")
        ax.axvline(mu, color=COLOR_GOLD, linestyle="--",
                   linewidth=1.5, label=f"Media={mu:.2f}")
        ax.axvline(np.median(promedios), color=COLOR_RIESGO, linestyle=":",
                   linewidth=1.5, label=f"Mediana={np.median(promedios):.2f}")
        ax.set_title("Distribución de Promedios (densidad, área=1)", color=COLOR_GOLD)
        ax.set_xlabel("Promedio Final")
        ax.set_ylabel("Densidad de probabilidad")
        ax.legend(fontsize=7)

    def _hist_grupos(self, ax, prom_trab, prom_no):
        ax.set_facecolor(BG_CARD)
        lo = min(min(prom_trab, default=0), min(prom_no, default=0))
        hi = max(max(prom_trab, default=10), max(prom_no, default=10))
        bins = np.linspace(lo, hi, 10)
        x_rng = np.linspace(lo - 1, hi + 1, 300)
        if prom_trab:
            mu1, sig1 = np.mean(prom_trab), np.std(prom_trab, ddof=1)
            ax.hist(prom_trab, bins=bins, alpha=0.55, density=True,
                    color=COLOR_RIESGO, edgecolor=COLOR_BORDER,
                    linewidth=0.8, label=f"Trabaja (n={len(prom_trab)})")
            ax.plot(x_rng, _norm.pdf(x_rng, mu1, sig1),
                    color=COLOR_RIESGO, linewidth=2)
            ax.axvline(mu1, color=COLOR_RIESGO, linestyle="--", linewidth=1.5,
                       label=f"x̄={mu1:.2f}")
        if prom_no:
            mu2, sig2 = np.mean(prom_no), np.std(prom_no, ddof=1)
            ax.hist(prom_no, bins=bins, alpha=0.55, density=True,
                    color=COLOR_ALTO, edgecolor=COLOR_BORDER,
                    linewidth=0.8, label=f"No trabaja (n={len(prom_no)})")
            ax.plot(x_rng, _norm.pdf(x_rng, mu2, sig2),
                    color=COLOR_ALTO, linewidth=2)
            ax.axvline(np.mean(prom_no), color=COLOR_ALTO,
                       linestyle="--", linewidth=1.5,
                       label=f"x̄={np.mean(prom_no):.2f}")
        ax.set_title("Promedio por Situación Laboral (densidad, área=1)", color=COLOR_GOLD)
        ax.set_xlabel("Promedio Final")
        ax.set_ylabel("Densidad de probabilidad")
        ax.legend(fontsize=7)

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

    # ── Gráficas ampliadas (datos formulario) ─────────────────────────
    def _graficas_extendidas(self, parent, est):
        fig = plt.Figure(figsize=(12, 8), facecolor=BG_MAIN)

        ax1 = fig.add_subplot(2, 2, 1)
        self._bar_estres(ax1, est)

        ax2 = fig.add_subplot(2, 2, 2)
        self._bar_frecuencia(ax2, est)

        ax3 = fig.add_subplot(2, 2, 3)
        self._bar_genero(ax3, est)

        ax4 = fig.add_subplot(2, 2, 4)
        self._bar_estilo(ax4, est)

        fig.tight_layout(pad=3)
        canvas_frame = tk.Frame(parent, bg=BG_MAIN)
        canvas_frame.pack(fill="x", padx=16, pady=4)
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _bar_estres(self, ax, est):
        ax.set_facecolor(BG_CARD)
        cats = ["Alto", "Medio", "Bajo"]
        colors = [COLOR_RIESGO, COLOR_MEDIO, COLOR_ALTO]
        means, ns = [], []
        for cat in cats:
            g = [e.promedio_final for e in est
                 if e.nivel_estres.strip().capitalize() == cat]
            means.append(np.mean(g) if g else 0)
            ns.append(len(g))
        bars = ax.bar(cats, means, color=colors,
                      edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.85)
        for bar, n, m in zip(bars, ns, means):
            if n:
                ax.text(bar.get_x() + bar.get_width() / 2, m + 0.1,
                        f"n={n}\n{m:.2f}", ha="center", va="bottom",
                        color=COLOR_GOLD_DIM, fontsize=8)
        ax.set_title("Nivel de Estrés vs Promedio", color=COLOR_GOLD)
        ax.set_ylabel("Promedio Final")
        ax.set_ylim(0, 11)

    def _bar_frecuencia(self, ax, est):
        ax.set_facecolor(BG_CARD)
        cats = ["Siempre", "Frecuentemente", "A veces", "Nunca"]
        means, ns = [], []
        for cat in cats:
            g = [e.promedio_final for e in est
                 if e.frecuencia_estudio.strip().lower() == cat.lower()]
            means.append(np.mean(g) if g else 0)
            ns.append(len(g))
        bars = ax.bar(cats, means, color=COLOR_PURPLE_LT,
                      edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.85)
        for bar, n, m in zip(bars, ns, means):
            if n:
                ax.text(bar.get_x() + bar.get_width() / 2, m + 0.1,
                        f"n={n}\n{m:.2f}", ha="center", va="bottom",
                        color=COLOR_GOLD_DIM, fontsize=8)
        ax.set_title("Frecuencia de Estudio vs Promedio", color=COLOR_GOLD)
        ax.set_ylabel("Promedio Final")
        ax.set_ylim(0, 11)
        ax.tick_params(axis="x", labelsize=8)

    def _bar_genero(self, ax, est):
        ax.set_facecolor(BG_CARD)
        generos = sorted(set(e.genero for e in est if e.genero))
        means, ns = [], []
        for g in generos:
            grupo = [e.promedio_final for e in est if e.genero == g]
            means.append(np.mean(grupo) if grupo else 0)
            ns.append(len(grupo))
        bars = ax.bar(generos, means, color=COLOR_GOLD_DIM,
                      edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.85)
        for bar, n, m in zip(bars, ns, means):
            if n:
                ax.text(bar.get_x() + bar.get_width() / 2, m + 0.1,
                        f"n={n}\n{m:.2f}", ha="center", va="bottom",
                        color=BG_MAIN, fontsize=8)
        ax.set_title("Género vs Promedio Final", color=COLOR_GOLD)
        ax.set_ylabel("Promedio Final")
        ax.set_ylim(0, 11)

    def _bar_estilo(self, ax, est):
        ax.set_facecolor(BG_CARD)
        estilos = sorted(set(e.estilo_aprendizaje for e in est if e.estilo_aprendizaje))
        means, ns = [], []
        for s in estilos:
            g = [e.promedio_final for e in est if e.estilo_aprendizaje == s]
            means.append(np.mean(g) if g else 0)
            ns.append(len(g))
        bars = ax.bar(estilos, means, color=COLOR_ALTO,
                      edgecolor=COLOR_BORDER, linewidth=0.8, alpha=0.85)
        for bar, n, m in zip(bars, ns, means):
            if n:
                ax.text(bar.get_x() + bar.get_width() / 2, m + 0.1,
                        f"n={n}\n{m:.2f}", ha="center", va="bottom",
                        color=BG_MAIN, fontsize=8)
        ax.set_title("Estilo de Aprendizaje vs Promedio", color=COLOR_GOLD)
        ax.set_ylabel("Promedio Final")
        ax.set_ylim(0, 11)
        ax.tick_params(axis="x", labelsize=8)

    # ── Exportar PDF ──────────────────────────────────────────────────
    def _exportar_pdf(self, parent):
        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        from stats.exportar_pdf import generar_reporte

        ruta = fd.asksaveasfilename(
            title="Guardar reporte PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
            initialfile="Reporte_Estadistico.pdf",
        )
        if not ruta:
            return
        try:
            generar_reporte(ruta)
            mb.showinfo("PDF generado",
                        f"Reporte guardado exitosamente en:\n{ruta}")
        except Exception as exc:
            mb.showerror("Error al exportar PDF", str(exc))
