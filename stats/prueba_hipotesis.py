# -*- coding: utf-8 -*-
"""Prueba de hipótesis — Hipótesis B (Opción B).

H₀: μ_trabaja ≥ μ_no_trabaja   (trabajar no reduce el promedio)
H₁: μ_trabaja < μ_no_trabaja   (los que trabajan tienen promedio MENOR)

Prueba t de Student para dos muestras independientes, una cola izquierda.
Asume varianzas iguales; usa varianza combinada (pooled variance).
"""
import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass


@dataclass
class ResultadoPruebaB:
    hipotesis_nula: str
    hipotesis_alt:  str
    n_trabaja:      int
    n_no_trabaja:   int
    media_trabaja:  float
    media_no_trabaja: float
    diferencia:     float          # media_trabaja - media_no_trabaja
    std_trabaja:    float
    std_no_trabaja: float
    t_estadistico:  float
    grados_libertad: float
    p_valor:        float          # una cola (izquierda)
    alpha:          float
    rechazar_h0:    bool
    ic_dif_inf:     float          # IC 95% de la diferencia
    ic_dif_sup:     float
    d_cohen:        float          # tamaño del efecto
    conclusion:     str

    def tabla_grupos(self) -> list[tuple[str, str, str]]:
        """Encabezado + 2 filas: (campo, trabaja, no_trabaja)."""
        return [
            ("",                   "Trabaja",                    "No Trabaja"),
            ("n",                  str(self.n_trabaja),          str(self.n_no_trabaja)),
            ("Media (x̄)",         f"{self.media_trabaja:.4f}",  f"{self.media_no_trabaja:.4f}"),
            ("Desv. estándar (s)", f"{self.std_trabaja:.4f}",    f"{self.std_no_trabaja:.4f}"),
        ]

    def tabla_prueba(self) -> list[tuple[str, str]]:
        return [
            ("Hipótesis nula H₀",          self.hipotesis_nula),
            ("Hipótesis alternativa H₁",   self.hipotesis_alt),
            ("Diferencia (μ₁ − μ₂)",       f"{self.diferencia:.4f}"),
            ("Estadístico t (Student)",     f"{self.t_estadistico:.4f}"),
            ("Grados de libertad",          f"{self.grados_libertad:.0f}"),
            ("p-valor (una cola)",          f"{self.p_valor:.4f}"),
            ("Nivel de significancia α",    str(self.alpha)),
            ("¿Rechazar H₀?",              "SÍ ✓" if self.rechazar_h0 else "NO ✗"),
            ("IC 95% diferencia",          f"[{self.ic_dif_inf:.4f}, {self.ic_dif_sup:.4f}]"),
            ("d de Cohen (tamaño efecto)", f"{self.d_cohen:.4f}"),
            ("Conclusión",                 self.conclusion),
        ]


def prueba_hipotesis_B(
    promedios_trabaja: list[float],
    promedios_no_trabaja: list[float],
    alpha: float = 0.05,
) -> ResultadoPruebaB:
    """Prueba t de Student unilateral izquierda para Hipótesis B (varianzas iguales)."""
    g1 = np.array(promedios_trabaja,    dtype=float)
    g2 = np.array(promedios_no_trabaja, dtype=float)

    n1, n2 = len(g1), len(g2)
    m1, m2 = g1.mean(), g2.mean()
    s1, s2 = g1.std(ddof=1), g2.std(ddof=1)

    # t de Student (varianzas iguales), alternative='less' → H₁: mean(g1) < mean(g2)
    t_stat, p_val = sp_stats.ttest_ind(g1, g2, equal_var=True, alternative="less")

    # Grados de libertad de Student: n1 + n2 - 2
    gl = float(n1 + n2 - 2)

    # Varianza combinada (pooled variance) y error estándar
    sp_pool = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    se = sp_pool * np.sqrt(1.0 / n1 + 1.0 / n2)

    # IC 95% para la diferencia de medias (bilateral)
    t_crit = sp_stats.t.ppf(0.975, df=gl)
    dif = m1 - m2
    ic_inf, ic_sup = dif - t_crit * se, dif + t_crit * se

    # d de Cohen (pooled std)
    d_cohen = dif / sp_pool if sp_pool > 0 else 0.0

    rechazar = bool(p_val < alpha)
    if rechazar:
        conclusion = (
            f"Con α = {alpha} se RECHAZA H₀. Los estudiantes que trabajan tienen "
            f"un promedio significativamente menor (Δ = {dif:.2f}, p = {p_val:.4f})."
        )
    else:
        conclusion = (
            f"Con α = {alpha} NO se rechaza H₀. No hay evidencia suficiente de que "
            f"trabajar reduzca el promedio (p = {p_val:.4f})."
        )

    return ResultadoPruebaB(
        hipotesis_nula="μ_trabaja ≥ μ_no_trabaja (trabajar no afecta el promedio)",
        hipotesis_alt="μ_trabaja < μ_no_trabaja (los que trabajan tienen menor promedio)",
        n_trabaja=n1, n_no_trabaja=n2,
        media_trabaja=float(m1), media_no_trabaja=float(m2),
        diferencia=float(dif),
        std_trabaja=float(s1), std_no_trabaja=float(s2),
        t_estadistico=float(t_stat),
        grados_libertad=float(gl),
        p_valor=float(p_val),
        alpha=alpha,
        rechazar_h0=rechazar,
        ic_dif_inf=float(ic_inf), ic_dif_sup=float(ic_sup),
        d_cohen=float(d_cohen),
        conclusion=conclusion,
    )
