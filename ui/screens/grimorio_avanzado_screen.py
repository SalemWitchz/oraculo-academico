# -*- coding: utf-8 -*-
"""✦ Grimorio Avanzado — Procedimientos estadísticos paso a paso."""
import tkinter as tk
import numpy as np
from scipy import stats as sp_stats

from config import (
    BG_MAIN, BG_CARD, BG_INPUT,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER, COLOR_BORDER_LT,
    COLOR_RIESGO, COLOR_ALTO,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from ui.widgets import GothicCard, ScrollableFrame, SectionTitle


class GrimorioAvanzadoScreen:
    def __init__(self, win):
        self.win = win

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds  = DataStore.get()
        est = ds.estudiantes

        if not est:
            tk.Label(parent,
                     text="⚠ Sin datos. Ve a ⊕ Datos e importa un archivo.",
                     font=FONT_BODY, fg=COLOR_RIESGO, bg=BG_MAIN).pack(pady=40)
            return

        promedios   = ds.promedios()
        asistencias = ds.asistencias()
        prom_trab   = [e.promedio_final for e in est if     e.trabaja]
        prom_no     = [e.promedio_final for e in est if not e.trabaja]
        horas_est   = [e.horas_estudio  for e in est]

        scroll = ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # ── Título ────────────────────────────────────────────────────
        tk.Label(inner, text="✦  GRIMORIO AVANZADO  ✦",
                 font=("Palatino Linotype", 20, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(inner,
                 text='"Cada fórmula resuelta con los datos reales — procedimiento completo"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 12))

        # ── I. Estadística Descriptiva ─────────────────────────────────
        SectionTitle(inner, "I. Estadística Descriptiva — Promedios Finales", bg=BG_MAIN
                     ).pack(anchor="w", padx=18, pady=(6, 2))
        self._paso_media(inner, promedios)
        self._paso_varianza(inner, promedios)
        self._paso_desv_std(inner, promedios)
        self._paso_ic(inner, promedios)

        # ── II. Prueba t de Student ────────────────────────────────────
        SectionTitle(inner, "II. Prueba t de Student — Hipótesis B (Situación Laboral)", bg=BG_MAIN
                     ).pack(anchor="w", padx=18, pady=(14, 2))
        if len(prom_trab) >= 2 and len(prom_no) >= 2:
            self._paso_t_student(inner, prom_trab, prom_no)
            self._paso_cohen(inner, prom_trab, prom_no)
            self._paso_ic_diferencia(inner, prom_trab, prom_no)
        else:
            tk.Label(inner,
                     text="⚠ Se necesitan al menos 2 estudiantes en cada grupo (trabaja / no trabaja).",
                     font=FONT_SMALL, fg=COLOR_RIESGO, bg=BG_MAIN, padx=20).pack(anchor="w")

        # ── III. Regresión Lineal Simple ───────────────────────────────
        SectionTitle(inner, "III. Regresión Lineal Simple (Mínimos Cuadrados) — Promedio vs Horas de Estudio", bg=BG_MAIN
                     ).pack(anchor="w", padx=18, pady=(14, 2))
        self._paso_regresion(inner, promedios, horas_est)

        tk.Label(inner, text="", bg=BG_MAIN).pack(pady=10)

    # ══════════════════════════════════════════════════════════════════
    # Helpers de layout
    # ══════════════════════════════════════════════════════════════════
    def _card(self, parent, titulo: str, icono: str = "∑") -> tk.Frame:
        card = GothicCard(parent, padx=0, pady=0)
        card.pack(fill="x", padx=18, pady=5)

        hdr = tk.Frame(card, bg="#111111")
        hdr.pack(fill="x")
        tk.Label(hdr, text=icono,
                 font=("Palatino Linotype", 14, "bold"),
                 fg=COLOR_GOLD, bg="#111111", width=4, pady=6).pack(side="left", padx=(8, 0))
        tk.Label(hdr, text=titulo,
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg="#111111", anchor="w").pack(side="left", padx=6)
        tk.Frame(card, bg=COLOR_BORDER, height=1).pack(fill="x")

        body = tk.Frame(card, bg=BG_CARD, padx=16, pady=10)
        body.pack(fill="x")
        return body

    def _fila(self, parent, etiqueta: str, valor: str, color: str = None):
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(fill="x", pady=1)
        tk.Label(f, text=etiqueta,
                 font=("Palatino Linotype", 9, "bold"),
                 fg=COLOR_BORDER_LT, bg=BG_CARD,
                 width=22, anchor="w").pack(side="left")
        tk.Label(f, text=valor,
                 font=("Courier New", 10),
                 fg=color or COLOR_GOLD_DIM, bg=BG_CARD,
                 anchor="w", justify="left", wraplength=820).pack(side="left", fill="x", expand=True)

    def _resultado(self, parent, valor: str, color: str = None):
        f = tk.Frame(parent, bg=BG_INPUT,
                     highlightbackground=COLOR_BORDER_LT,
                     highlightthickness=1)
        f.pack(fill="x", pady=(8, 2))
        tk.Label(f, text=f"  ▶  RESULTADO:  {valor}",
                 font=("Palatino Linotype", 11, "bold"),
                 fg=color or COLOR_GOLD, bg=BG_INPUT,
                 anchor="w", pady=7, padx=6).pack(anchor="w")

    @staticmethod
    def _muestra_str(vals, n_max: int = 5) -> str:
        s = [f"{v:.2f}" for v in vals[:n_max]]
        if len(vals) > n_max:
            s.append(f"… ({len(vals)} datos)")
        return ",  ".join(s)

    # ══════════════════════════════════════════════════════════════════
    # Pasos — Estadística Descriptiva
    # ══════════════════════════════════════════════════════════════════
    def _paso_media(self, parent, datos):
        x  = np.array(datos, dtype=float)
        n  = len(x)
        mu = float(x.mean())

        body = self._card(parent, "Media Aritmética (x̄) — Estimación Puntual", "x̄")
        self._fila(body, "Fórmula:",
                   "x̄  =  (x₁ + x₂ + … + xₙ) / n  =  Σxᵢ / n")
        self._fila(body, "Datos (muestra):", self._muestra_str(x))
        self._fila(body, "Suma  Σxᵢ:", f"{x.sum():.4f}")
        self._fila(body, "n (tamaño):", str(n))
        self._fila(body, "Sustitución:", f"x̄  =  {x.sum():.4f}  /  {n}")
        self._resultado(body, f"x̄  =  {mu:.4f}")

    def _paso_varianza(self, parent, datos):
        x     = np.array(datos, dtype=float)
        n     = len(x)
        mu    = float(x.mean())
        diffs = (x - mu) ** 2
        s2    = float(np.var(x, ddof=1))

        body = self._card(parent, "Varianza Muestral (s²) — Dispersión respecto a la Media", "s²")
        self._fila(body, "Fórmula:",
                   "s²  =  Σ(xᵢ − x̄)²  /  (n − 1)")
        self._fila(body, "x̄  =", f"{mu:.4f}")
        ejm = ",  ".join(f"({v:.2f}−{mu:.2f})²={d:.4f}"
                          for v, d in zip(x[:4], diffs[:4]))
        if n > 4:
            ejm += "  …"
        self._fila(body, "Diferencias al²:", ejm)
        self._fila(body, "Suma Σ(xᵢ−x̄)²:", f"{diffs.sum():.4f}")
        self._fila(body, "Denominador  n−1:", str(n - 1))
        self._fila(body, "Sustitución:",
                   f"s²  =  {diffs.sum():.4f}  /  {n - 1}")
        self._resultado(body, f"s²  =  {s2:.4f}")

    def _paso_desv_std(self, parent, datos):
        x  = np.array(datos, dtype=float)
        s2 = float(np.var(x, ddof=1))
        s  = float(np.std(x, ddof=1))

        body = self._card(parent, "Desviación Estándar Muestral (s) — Raíz de la Varianza", "s")
        self._fila(body, "Fórmula:",
                   "s  =  √s²")
        self._fila(body, "s² (calculada):", f"{s2:.4f}")
        self._fila(body, "Sustitución:",
                   f"s  =  √{s2:.4f}  =  {s:.4f}")
        self._fila(body, "Interpretación:",
                   f"Los promedios se desvían en promedio ±{s:.4f} puntos respecto a la media")
        self._resultado(body, f"s  =  {s:.4f}")

    def _paso_ic(self, parent, datos):
        x      = np.array(datos, dtype=float)
        n      = len(x)
        mu     = float(x.mean())
        s      = float(x.std(ddof=1))
        se     = s / np.sqrt(n)
        gl     = n - 1
        t_crit = float(sp_stats.t.ppf(0.975, df=gl))
        margen = t_crit * se
        ic_inf = mu - margen
        ic_sup = mu + margen

        body = self._card(parent, "Intervalo de Confianza al 95% para la Media — Estimación por Intervalos", "IC")
        self._fila(body, "Fórmula:",
                   "IC₉₅%  =  x̄  ±  t_(α/2, n−1) · (s / √n)")
        self._fila(body, "Parámetros:",
                   f"x̄ = {mu:.4f},   s = {s:.4f},   n = {n},   α = 0.05,   gl = n−1 = {gl}")
        self._fila(body, "Error estándar SE:",
                   f"s / √n  =  {s:.4f} / √{n}  =  {s:.4f} / {np.sqrt(n):.4f}  =  {se:.4f}")
        self._fila(body, "t crítico:",
                   f"t_(0.025, gl={gl})  =  {t_crit:.4f}   ← tabla distribución t de Student, 2 colas")
        self._fila(body, "Margen de error E:",
                   f"t · SE  =  {t_crit:.4f} × {se:.4f}  =  {margen:.4f}")
        self._fila(body, "Límite inferior:",
                   f"x̄ − E  =  {mu:.4f} − {margen:.4f}  =  {ic_inf:.4f}")
        self._fila(body, "Límite superior:",
                   f"x̄ + E  =  {mu:.4f} + {margen:.4f}  =  {ic_sup:.4f}")
        self._resultado(body,
                        f"IC₉₅%  =  [{ic_inf:.4f},  {ic_sup:.4f}]   "
                        f"(con 95% de confianza, μ está en este intervalo)")

    # ══════════════════════════════════════════════════════════════════
    # Pasos — Prueba t de Student
    # ══════════════════════════════════════════════════════════════════
    def _paso_t_student(self, parent, g1, g2):
        a1, a2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
        n1, n2 = len(a1), len(a2)
        m1, m2 = float(a1.mean()), float(a2.mean())
        s1, s2 = float(a1.std(ddof=1)), float(a2.std(ddof=1))
        sp     = float(np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2)))
        factor = float(np.sqrt(1.0/n1 + 1.0/n2))
        se     = sp * factor
        gl     = n1 + n2 - 2
        t_stat, p_val = sp_stats.ttest_ind(a1, a2, equal_var=True, alternative="less")
        t_stat, p_val = float(t_stat), float(p_val)
        t_crit = float(sp_stats.t.ppf(0.05, df=gl))
        rechaza = p_val < 0.05

        body = self._card(parent, "Prueba t de Student — Dos Muestras Independientes, Una Cola Izquierda", "t")
        self._fila(body, "Hipótesis nula H₀:",
                   "μ_trabaja  ≥  μ_no_trabaja   (trabajar NO reduce el promedio)")
        self._fila(body, "Hipótesis alt. H₁:",
                   "μ_trabaja  <  μ_no_trabaja   (los que trabajan tienen MENOR promedio) ← una cola")
        self._fila(body, "Fórmula:",
                   "t  =  (x̄₁ − x̄₂)  /  [sp · √(1/n₁ + 1/n₂)]")
        self._fila(body, "Diferencia x̄₁−x̄₂:",
                   f"{m1:.4f} − {m2:.4f}  =  {m1-m2:.4f}")
        self._fila(body, "sp (pooled):", f"{sp:.4f}")
        self._fila(body, "√(1/n₁ + 1/n₂):",
                   f"√(1/{n1} + 1/{n2})  =  √{1.0/n1+1.0/n2:.6f}  =  {factor:.4f}")
        self._fila(body, "Denominador sp·√(…):",
                   f"{sp:.4f} × {factor:.4f}  =  {se:.4f}")
        self._fila(body, "Sustitución t:",
                   f"({m1:.4f} − {m2:.4f})  /  {se:.4f}  =  {m1-m2:.4f}  /  {se:.4f}")
        self._fila(body, "Grados de libertad:",
                   f"gl  =  n₁ + n₂ − 2  =  {n1} + {n2} − 2  =  {gl}")
        self._fila(body, "t estadístico:", f"{t_stat:.4f}")
        self._fila(body, "t crítico (α=0.05):",
                   f"t_(0.05, gl={gl})  =  {t_crit:.4f}   ← tabla t de Student, una cola izquierda")
        self._fila(body, "Regla de rechazo:",
                   f"Rechazar H₀ si  t < t_crítico  →  {t_stat:.4f} {'<' if t_stat < t_crit else '≥'} {t_crit:.4f}")
        self._fila(body, "p-valor (una cola):",
                   f"P(T < {t_stat:.4f} | gl={gl})  =  {p_val:.4f}")
        self._fila(body, "Criterio p-valor:",
                   f"Rechazar H₀ si  p < α = 0.05  →  {p_val:.4f} {'<' if rechaza else '≥'} 0.05")
        color_res = COLOR_ALTO if rechaza else COLOR_RIESGO
        decision  = ("SÍ se rechaza H₀ — evidencia de que trabajar reduce el promedio"
                     if rechaza else
                     "NO se rechaza H₀ — no hay evidencia suficiente")
        self._resultado(body,
                        f"t = {t_stat:.4f},  p = {p_val:.4f}  →  {decision}",
                        color=color_res)

    def _paso_cohen(self, parent, g1, g2):
        a1, a2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
        n1, n2 = len(a1), len(a2)
        m1, m2 = float(a1.mean()), float(a2.mean())
        s1, s2 = float(a1.std(ddof=1)), float(a2.std(ddof=1))
        sp  = float(np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2)))
        d   = (m1 - m2) / sp if sp > 0 else 0.0
        mag = ("pequeño"    if abs(d) < 0.2 else
               "mediano"    if abs(d) < 0.5 else
               "grande"     if abs(d) < 0.8 else
               "muy grande")

        body = self._card(parent, "d de Cohen — Tamaño del Efecto Estandarizado", "d")
        self._fila(body, "Fórmula:",
                   "d  =  (x̄₁ − x̄₂)  /  sp")
        self._fila(body, "x̄₁ − x̄₂:", f"{m1:.4f} − {m2:.4f}  =  {m1-m2:.4f}")
        self._fila(body, "sp (pooled):", f"{sp:.4f}")
        self._fila(body, "Sustitución:",
                   f"d  =  {m1-m2:.4f}  /  {sp:.4f}  =  {d:.4f}")
        self._fila(body, "Escala de Cohen:",
                   "|d| < 0.2 = pequeño   0.2–0.5 = mediano   0.5–0.8 = grande   > 0.8 = muy grande")
        self._resultado(body, f"d  =  {d:.4f}   →  Tamaño del efecto: {mag}")

    def _paso_ic_diferencia(self, parent, g1, g2):
        a1, a2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
        n1, n2 = len(a1), len(a2)
        m1, m2 = float(a1.mean()), float(a2.mean())
        s1, s2 = float(a1.std(ddof=1)), float(a2.std(ddof=1))
        sp  = float(np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2)))
        se  = sp * float(np.sqrt(1.0/n1 + 1.0/n2))
        gl  = n1 + n2 - 2
        t_c = float(sp_stats.t.ppf(0.975, df=gl))
        dif = m1 - m2
        inf, sup = dif - t_c * se, dif + t_c * se

        body = self._card(parent, "IC 95% para la Diferencia de Medias (μ₁ − μ₂)", "IC∆")
        self._fila(body, "Fórmula:",
                   "(x̄₁−x̄₂)  ±  t_(α/2, gl) · sp · √(1/n₁+1/n₂)")
        self._fila(body, "Diferencia:",
                   f"x̄₁−x̄₂  =  {m1:.4f} − {m2:.4f}  =  {dif:.4f}")
        self._fila(body, "t crítico (bilateral):",
                   f"t_(0.025, gl={gl})  =  {t_c:.4f}")
        self._fila(body, "Margen E:",
                   f"{t_c:.4f} × {se:.4f}  =  {t_c*se:.4f}")
        self._fila(body, "Límite inferior:",
                   f"{dif:.4f} − {t_c*se:.4f}  =  {inf:.4f}")
        self._fila(body, "Límite superior:",
                   f"{dif:.4f} + {t_c*se:.4f}  =  {sup:.4f}")
        interp = ("El intervalo es completamente negativo → el grupo 'trabaja' tiene menor media"
                  if sup < 0 else
                  "El intervalo cruza cero → la diferencia no es concluyente" if inf < 0 < sup else
                  "El intervalo es positivo → el grupo 'trabaja' tiene mayor media")
        self._fila(body, "Interpretación:", interp)
        self._resultado(body, f"IC₉₅%(μ₁−μ₂)  =  [{inf:.4f},  {sup:.4f}]")

    # ══════════════════════════════════════════════════════════════════
    # Pasos — Regresión
    # ══════════════════════════════════════════════════════════════════
    def _paso_regresion(self, parent, prom, horas):
        x   = np.array(horas, dtype=float)
        y   = np.array(prom,  dtype=float)
        n   = len(x)
        xm  = float(x.mean())
        ym  = float(y.mean())
        sxy = float(np.sum((x - xm) * (y - ym)))
        sxx = float(np.sum((x - xm)**2))
        b1  = sxy / sxx if sxx != 0 else 0.0
        b0  = ym - b1 * xm
        y_p = b0 + b1 * x
        ssr = float(np.sum((y - y_p)**2))
        sst = float(np.sum((y - ym)**2))
        r2  = 1.0 - ssr / sst if sst != 0 else 0.0

        body = self._card(parent,
                          "Regresión Lineal Simple — Método de Mínimos Cuadrados", "β")
        self._fila(body, "Modelo:",
                   "ŷ  =  β₀  +  β₁·x     donde  x = horas de estudio,  ŷ = promedio predicho")
        self._fila(body, "Fórmulas:",
                   "β₁ = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)²     β₀ = ȳ − β₁·x̄")
        self._fila(body, "x̄  (horas):", f"{xm:.4f}")
        self._fila(body, "ȳ  (promedio):", f"{ym:.4f}")
        self._fila(body, "Σ(xᵢ−x̄)(yᵢ−ȳ):", f"{sxy:.4f}")
        self._fila(body, "Σ(xᵢ−x̄)²:", f"{sxx:.4f}")
        self._fila(body, "β₁ (pendiente):",
                   f"{sxy:.4f}  /  {sxx:.4f}  =  {b1:.4f}   "
                   f"← por cada hora más de estudio, el promedio cambia en {b1:.4f} puntos")
        self._fila(body, "β₀ (intercepto):",
                   f"ȳ − β₁·x̄  =  {ym:.4f} − {b1:.4f}×{xm:.4f}  =  {b0:.4f}")
        self._fila(body, "Ecuación final:",
                   f"ŷ  =  {b0:.4f}  +  {b1:.4f}·x")
        self._fila(body, "SS_residual:", f"{ssr:.4f}")
        self._fila(body, "SS_total:", f"{sst:.4f}")
        self._fila(body, "R²  =  1 − SS_res/SS_tot:",
                   f"1 − ({ssr:.4f}/{sst:.4f})  =  {r2:.4f}   "
                   f"({r2*100:.1f}% de la varianza del promedio explicada por las horas)")
        self._resultado(body,
                        f"ŷ  =  {b0:.4f}  +  {b1:.4f}·x     R²  =  {r2:.4f}")

