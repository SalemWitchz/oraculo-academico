# -*- coding: utf-8 -*-
"""Generador de reporte PDF usando matplotlib.backends.backend_pdf."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")           # Sin ventana para el PDF
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import norm as _norm

from data.data_store import DataStore
from stats import descriptiva as desc_mod
from stats.prueba_hipotesis import prueba_hipotesis_B

# ── Paleta (reproduce la app sin importar tkinter) ────────────────────────────
_BG    = "#0A0A0A"
_CARD  = "#1A1A1A"
_GOLD  = "#F0F0F0"
_DIM   = "#999999"
_BORD  = "#2E2E2E"
_ALTO  = "#EEEEEE"
_RISK  = "#DD3322"
_MED   = "#888888"
_PURP  = "#383838"

_MPL = {
    "figure.facecolor":  _BG,
    "axes.facecolor":    _CARD,
    "axes.edgecolor":    _BORD,
    "axes.labelcolor":   _DIM,
    "axes.titlecolor":   _GOLD,
    "axes.titlesize":    11,
    "axes.labelsize":    9,
    "axes.grid":         True,
    "grid.color":        "#252525",
    "grid.alpha":        0.6,
    "grid.linestyle":    "--",
    "xtick.color":       _DIM,
    "ytick.color":       _DIM,
    "text.color":        _GOLD,
    "legend.facecolor":  _CARD,
    "legend.edgecolor":  _BORD,
    "legend.labelcolor": _DIM,
    "legend.fontsize":   8,
}

_EQUIPO = [
    "Rodrigo Axel Pineda Arce",
    "Felix Eduardo Torres Grajales",
    "Aldo Egalin Roblero Pérez",
    "Fátima Vázquez Méndez",
    "Sergio Alberto Solís Díaz",
]


# ── Helpers de tabla matplotlib ───────────────────────────────────────────────
def _tabla_fig(ax, filas: list[tuple], col_widths=None):
    ax.axis("off")
    if not filas:
        return
    n_cols = len(filas[0])
    if col_widths is None:
        col_widths = [1 / n_cols] * n_cols
    tbl = ax.table(
        cellText=[list(f) for f in filas],
        cellLoc="left",
        loc="center",
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_facecolor(_CARD if r % 2 == 0 else "#111111")
        cell.set_edgecolor(_BORD)
        cell.set_text_props(color=_GOLD if r == 0 else _DIM)
        if r == 0:
            cell.set_facecolor("#111111")
            cell.set_text_props(color=_GOLD, fontweight="bold")


def _titulo_ax(ax, texto: str, sub: str = ""):
    ax.axis("off")
    ax.text(0.5, 0.65, texto,
            transform=ax.transAxes, fontsize=13, fontweight="bold",
            color=_GOLD, ha="center", va="center")
    if sub:
        ax.text(0.5, 0.38, sub,
                transform=ax.transAxes, fontsize=9, style="italic",
                color=_DIM, ha="center", va="center")


# ── Generador principal ───────────────────────────────────────────────────────
def generar_reporte(ruta: str | None = None) -> str:
    """Genera el PDF y devuelve la ruta del archivo creado."""
    ds  = DataStore.get()
    est = ds.estudiantes

    if not est:
        raise ValueError("No hay datos cargados.")

    promedios   = ds.promedios()
    asistencias = ds.asistencias()
    prom_trab   = [e.promedio_final for e in est if     e.trabaja]
    prom_no     = [e.promedio_final for e in est if not e.trabaja]

    if ruta is None:
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = str(Path.home() / "Desktop" / f"Reporte_Estadistico_{ts}.pdf")

    plt.rcParams.update(_MPL)

    with PdfPages(ruta) as pdf:
        _pagina_portada(pdf, len(est))
        _pagina_descriptiva(pdf, promedios, asistencias)
        if len(prom_trab) >= 2 and len(prom_no) >= 2:
            _pagina_hipotesis(pdf, prom_trab, prom_no)
        _pagina_graficas(pdf, est, prom_trab, prom_no, promedios)

    # Restaurar backend interactivo
    matplotlib.use("TkAgg")
    plt.rcParams.update({"figure.facecolor": _BG})
    return ruta


# ── Páginas del PDF ───────────────────────────────────────────────────────────
def _pagina_portada(pdf: PdfPages, n: int):
    fig = plt.figure(figsize=(8.5, 11), facecolor=_BG)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(_BG)
    ax.axis("off")

    # Banda superior
    ax.add_patch(plt.Rectangle((0, 0.88), 1, 0.12,
                 transform=ax.transAxes, facecolor="#111111", zorder=1))
    ax.text(0.5, 0.935, "SISTEMA DE ANÁLISIS ESTADÍSTICO ACADÉMICO",
            transform=ax.transAxes, fontsize=14, fontweight="bold",
            color=_GOLD, ha="center", va="center", zorder=2)

    # Título central
    ax.text(0.5, 0.72, "REPORTE ESTADÍSTICO COMPLETO",
            transform=ax.transAxes, fontsize=20, fontweight="bold",
            color=_GOLD, ha="center", va="center")
    ax.text(0.5, 0.65, "Hipótesis B — Impacto de la Situación Laboral en el Rendimiento Académico",
            transform=ax.transAxes, fontsize=11, style="italic",
            color=_DIM, ha="center", va="center")

    # Línea decorativa
    ax.axhline(0.60, xmin=0.15, xmax=0.85, color=_BORD, linewidth=1.5)
    ax.text(0.5, 0.585, "◆  ◆  ◆", transform=ax.transAxes,
            fontsize=10, color=_BORD, ha="center", va="center")
    ax.axhline(0.57, xmin=0.15, xmax=0.85, color=_BORD, linewidth=1.5)

    # Info proyecto
    info = [
        f"Muestra analizada:  {n} estudiantes",
        "Prueba estadística:  t de Student (dos muestras independientes, una cola)",
        f"Nivel de significancia:  α = 0.05",
        f"Fecha de generación:  {datetime.now().strftime('%d/%m/%Y  %H:%M')}",
    ]
    for i, line in enumerate(info):
        ax.text(0.5, 0.50 - i * 0.055, line,
                transform=ax.transAxes, fontsize=10,
                color=_DIM, ha="center", va="center")

    # Equipo
    ax.text(0.5, 0.27, "EQUIPO DE TRABAJO",
            transform=ax.transAxes, fontsize=10, fontweight="bold",
            color=_GOLD, ha="center", va="center")
    for i, nombre in enumerate(_EQUIPO):
        ax.text(0.5, 0.22 - i * 0.04, nombre,
                transform=ax.transAxes, fontsize=9,
                color=_DIM, ha="center", va="center")

    ax.text(0.5, 0.02,
            "Materia: Probabilidad y Estadística  ·  Docente: Ing. Víctor Sol Hernández  ·  4° \"O\"  ·  Ing. en Desarrollo y Tecnologías de Software",
            transform=ax.transAxes, fontsize=7.5,
            color=_BORD, ha="center", va="bottom")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _pagina_descriptiva(pdf: PdfPages, promedios: list, asistencias: list):
    fig = plt.figure(figsize=(8.5, 11), facecolor=_BG)
    fig.suptitle("ESTADÍSTICA DESCRIPTIVA", fontsize=13, fontweight="bold",
                 color=_GOLD, y=0.97)

    gs = gridspec.GridSpec(3, 2, figure=fig,
                           hspace=0.45, wspace=0.3,
                           top=0.93, bottom=0.05, left=0.05, right=0.97)

    # Tablas
    for col_idx, (datos, etq) in enumerate(
            [(promedios, "Promedio Final"), (asistencias, "Asistencia (%)")]):
        res = desc_mod.calcular(datos)
        ic_inf, ic_sup = desc_mod.intervalo_confianza_media(datos)
        filas = [("Estadístico", etq)] + res.tabla() + [
            ("IC 95% (inf)", f"{ic_inf:.4f}"),
            ("IC 95% (sup)", f"{ic_sup:.4f}"),
        ]
        ax = fig.add_subplot(gs[0, col_idx])
        _tabla_fig(ax, filas, [0.58, 0.42])

    # Histogramas con curva normal
    for col_idx, (datos, etq) in enumerate(
            [(promedios, "Promedio Final"), (asistencias, "Asistencia (%)")]):
        ax = fig.add_subplot(gs[1, col_idx])
        x  = np.array(datos)
        mu, sig = x.mean(), x.std(ddof=1)
        ax.hist(x, bins=8, color=_PURP, edgecolor=_BORD,
                linewidth=0.8, alpha=0.9, density=True)
        xr = np.linspace(mu - 4*sig, mu + 4*sig, 200)
        ax.plot(xr, _norm.pdf(xr, mu, sig), color=_GOLD, linewidth=2,
                label=f"N(μ={mu:.2f},σ={sig:.2f})")
        ax.axvline(mu, color=_GOLD, linestyle="--", linewidth=1.2,
                   label=f"Media={mu:.2f}")
        ax.set_title(f"Distribución — {etq} (densidad, área=1)")
        ax.set_xlabel(etq)
        ax.set_ylabel("Densidad")
        ax.legend(fontsize=7)

    # Boxplot de promedios
    ax_box = fig.add_subplot(gs[2, :])
    ax_box.set_facecolor(_CARD)
    ax_box.boxplot(promedios, vert=False, patch_artist=True,
                   medianprops=dict(color=_GOLD, linewidth=2),
                   boxprops=dict(facecolor=_PURP, alpha=0.8),
                   whiskerprops=dict(color=_DIM),
                   capprops=dict(color=_DIM),
                   flierprops=dict(markerfacecolor=_RISK, markersize=5))
    ax_box.set_title("Boxplot — Promedio Final")
    ax_box.set_xlabel("Promedio Final")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _pagina_hipotesis(pdf: PdfPages, prom_trab: list, prom_no: list):
    fig = plt.figure(figsize=(8.5, 11), facecolor=_BG)
    fig.suptitle("PRUEBA DE HIPÓTESIS — t DE STUDENT  (Hipótesis B)",
                 fontsize=13, fontweight="bold", color=_GOLD, y=0.97)

    gs = gridspec.GridSpec(3, 1, figure=fig,
                           hspace=0.4, top=0.93, bottom=0.05,
                           left=0.05, right=0.97)

    res = prueba_hipotesis_B(prom_trab, prom_no)

    # Tabla de grupos
    ax1 = fig.add_subplot(gs[0])
    _tabla_fig(ax1, res.tabla_grupos(), [0.50, 0.25, 0.25])

    # Tabla de prueba
    ax2 = fig.add_subplot(gs[1])
    _tabla_fig(ax2, res.tabla_prueba()[:-1], [0.50, 0.50])

    # Conclusión visual
    ax3 = fig.add_subplot(gs[2])
    ax3.axis("off")
    color_c = _ALTO if res.rechazar_h0 else _RISK
    ax3.add_patch(plt.Rectangle((0.05, 0.25), 0.90, 0.50,
                  transform=ax3.transAxes,
                  facecolor="#1A1A1A", edgecolor=color_c, linewidth=2))
    ax3.text(0.5, 0.65, "CONCLUSIÓN", transform=ax3.transAxes,
             fontsize=10, fontweight="bold", color=color_c,
             ha="center", va="center")
    ax3.text(0.5, 0.45, res.conclusion,
             transform=ax3.transAxes, fontsize=9, color=_GOLD,
             ha="center", va="center", wrap=True,
             multialignment="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _pagina_graficas(pdf: PdfPages, est, prom_trab, prom_no, promedios):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5), facecolor=_BG)
    fig.suptitle("VISUALIZACIONES DEL ANÁLISIS",
                 fontsize=13, fontweight="bold", color=_GOLD)

    # 1) Histograma superpuesto con curva normal
    ax = axes[0, 0]
    ax.set_facecolor(_CARD)
    lo = min(min(prom_trab, default=0), min(prom_no, default=0))
    hi = max(max(prom_trab, default=10), max(prom_no, default=10))
    bins = np.linspace(lo, hi, 10)
    xr   = np.linspace(lo - 1, hi + 1, 300)
    if prom_trab:
        mu1, sg1 = np.mean(prom_trab), np.std(prom_trab, ddof=1)
        ax.hist(prom_trab, bins=bins, alpha=0.55, density=True,
                color=_RISK, edgecolor=_BORD, label=f"Trabaja (n={len(prom_trab)})")
        ax.plot(xr, _norm.pdf(xr, mu1, sg1), color=_RISK, linewidth=2)
        ax.axvline(mu1, color=_RISK, linestyle="--", linewidth=1.2,
                   label=f"x̄={mu1:.2f}")
    if prom_no:
        mu2, sg2 = np.mean(prom_no), np.std(prom_no, ddof=1)
        ax.hist(prom_no, bins=bins, alpha=0.55, density=True,
                color=_ALTO, edgecolor=_BORD, label=f"No trabaja (n={len(prom_no)})")
        ax.plot(xr, _norm.pdf(xr, mu2, sg2), color=_ALTO, linewidth=2)
        ax.axvline(mu2, color=_ALTO, linestyle="--", linewidth=1.2,
                   label=f"x̄={mu2:.2f}")
    ax.set_title("Promedio por Situación Laboral (densidad, área=1)")
    ax.set_xlabel("Promedio Final")
    ax.set_ylabel("Densidad de probabilidad")
    ax.legend(fontsize=7)

    # 2) Boxplot por carrera
    ax = axes[0, 1]
    ax.set_facecolor(_CARD)
    carreras = sorted(set(e.carrera for e in est))
    data_bp  = [[e.promedio_final for e in est if e.carrera == c] for c in carreras]
    etqs     = [c.replace("Ingeniería en ", "Ing. ").replace("Ingeniería ", "Ing. ")
                for c in carreras]
    bp = ax.boxplot(data_bp, patch_artist=True, labels=etqs,
                    medianprops=dict(color=_GOLD, linewidth=2),
                    whiskerprops=dict(color=_DIM), capprops=dict(color=_DIM),
                    flierprops=dict(markerfacecolor=_RISK, markersize=4))
    for patch in bp["boxes"]:
        patch.set_facecolor(_PURP)
        patch.set_alpha(0.75)
    ax.set_title("Promedios por Carrera")
    ax.tick_params(axis="x", labelsize=6, rotation=20)
    ax.set_ylabel("Promedio Final")

    # 3) Barras de medias grupales
    ax = axes[1, 0]
    ax.set_facecolor(_CARD)
    grupos  = ["Trabaja", "No trabaja"]
    medias  = [np.mean(prom_trab) if prom_trab else 0,
               np.mean(prom_no)   if prom_no   else 0]
    colores = [_RISK, _ALTO]
    bars = ax.bar(grupos, medias, color=colores, alpha=0.8,
                  edgecolor=_BORD, linewidth=0.8, width=0.4)
    ax.bar_label(bars, fmt="%.2f", color=_GOLD, fontsize=9, padding=3)
    ax.set_title("Media por Situación Laboral")
    ax.set_ylabel("Promedio Esperado")
    ax.set_ylim(0, 10.5)

    # 4) Pie de niveles
    ax = axes[1, 1]
    ax.set_facecolor(_CARD)
    counts  = {"Alto Rendimiento": 0, "Medio": 0, "En Riesgo": 0}
    for e in est:
        counts[e.nivel] += 1
    sizes  = list(counts.values())
    labels = list(counts.keys())
    colors_pie = [_ALTO, _MED, _RISK]
    wedges, _, auto = ax.pie(
        sizes, labels=None, colors=colors_pie,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(edgecolor=_CARD, linewidth=2),
    )
    for t in auto:
        t.set_color(_BG)
        t.set_fontsize(9)
    ax.legend(wedges, labels, loc="lower center", fontsize=8, framealpha=0.2)
    ax.set_title("Clasificación de Estudiantes")

    fig.tight_layout(pad=2.5)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
