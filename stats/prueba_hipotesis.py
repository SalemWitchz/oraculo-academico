# -*- coding: utf-8 -*-
"""Pruebas de hipótesis para la Hipótesis A.

H₀: ρ ≤ 0  (la asistencia NO influye positivamente en el promedio)
H₁: ρ > 0  (la asistencia SÍ influye positivamente — cola derecha)

Prueba t para el coeficiente de correlación de Pearson.
"""
import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass


@dataclass
class ResultadoPrueba:
    hipotesis_nula: str
    hipotesis_alt: str
    r: float
    t_estadistico: float
    grados_libertad: int
    p_valor: float          # una cola (derecha)
    alpha: float
    rechazar_h0: bool
    ic_r_inf: float         # intervalo de confianza para ρ (Fisher)
    ic_r_sup: float
    conclusion: str

    def tabla(self) -> list[tuple[str, str]]:
        return [
            ("Hipótesis nula H₀",          self.hipotesis_nula),
            ("Hipótesis alternativa H₁",   self.hipotesis_alt),
            ("Correlación de Pearson (r)",  f"{self.r:.4f}"),
            ("Estadístico t",               f"{self.t_estadistico:.4f}"),
            ("Grados de libertad",          str(self.grados_libertad)),
            ("p-valor (una cola)",          f"{self.p_valor:.4f}"),
            ("Nivel de significancia α",    f"{self.alpha}"),
            ("¿Rechazar H₀?",              "SÍ ✓" if self.rechazar_h0 else "NO ✗"),
            ("IC 95% para ρ",              f"[{self.ic_r_inf:.4f}, {self.ic_r_sup:.4f}]"),
            ("Conclusión",                 self.conclusion),
        ]


def prueba_correlacion(x: list[float], y: list[float], alpha: float = 0.05) -> ResultadoPrueba:
    xa = np.array(x, dtype=float)
    ya = np.array(y, dtype=float)
    n = len(xa)

    r, _ = sp_stats.pearsonr(xa, ya)
    t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
    gl = n - 2
    p_val = float(sp_stats.t.sf(t_stat, df=gl))   # cola derecha

    # Intervalo de confianza usando transformación z de Fisher (95 %)
    z = np.arctanh(r)
    se_z = 1.0 / np.sqrt(n - 3)
    z_crit = sp_stats.norm.ppf(0.975)
    ic_inf = float(np.tanh(z - z_crit * se_z))
    ic_sup = float(np.tanh(z + z_crit * se_z))

    rechazar = p_val < alpha
    if rechazar:
        conclusion = (
            f"Con α = {alpha}, se RECHAZA H₀. Existe evidencia estadística suficiente "
            f"de correlación positiva entre asistencia y promedio (p = {p_val:.4f})."
        )
    else:
        conclusion = (
            f"Con α = {alpha}, NO se rechaza H₀. No hay evidencia suficiente "
            f"de correlación positiva (p = {p_val:.4f})."
        )

    return ResultadoPrueba(
        hipotesis_nula="ρ ≤ 0 (sin correlación positiva)",
        hipotesis_alt="ρ > 0 (correlación positiva entre asistencia y promedio)",
        r=float(r),
        t_estadistico=float(t_stat),
        grados_libertad=gl,
        p_valor=p_val,
        alpha=alpha,
        rechazar_h0=rechazar,
        ic_r_inf=ic_inf,
        ic_r_sup=ic_sup,
        conclusion=conclusion,
    )
