# -*- coding: utf-8 -*-
"""Estadística descriptiva manual + numpy."""
import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass


@dataclass
class ResumenDescriptivo:
    n: int
    media: float
    mediana: float
    moda: float
    varianza: float
    desv_std: float
    coef_variacion: float
    sesgo: float
    curtosis: float
    minimo: float
    maximo: float
    rango: float
    q1: float
    q3: float
    iqr: float

    def tabla(self) -> list[tuple[str, str]]:
        return [
            ("n (muestra)",          str(self.n)),
            ("Media (x̄)",            f"{self.media:.4f}"),
            ("Mediana",              f"{self.mediana:.4f}"),
            ("Moda",                 f"{self.moda:.4f}"),
            ("Varianza (s²)",        f"{self.varianza:.4f}"),
            ("Desv. Estándar (s)",   f"{self.desv_std:.4f}"),
            ("Coef. Variación (%)",  f"{self.coef_variacion:.2f}%"),
            ("Sesgo (skewness)",     f"{self.sesgo:.4f}"),
            ("Curtosis",             f"{self.curtosis:.4f}"),
            ("Mínimo",               f"{self.minimo:.4f}"),
            ("Máximo",               f"{self.maximo:.4f}"),
            ("Rango",                f"{self.rango:.4f}"),
            ("Q1 (25%)",             f"{self.q1:.4f}"),
            ("Q3 (75%)",             f"{self.q3:.4f}"),
            ("IQR",                  f"{self.iqr:.4f}"),
        ]


def calcular(datos: list[float]) -> ResumenDescriptivo:
    x = np.array(datos, dtype=float)
    n = len(x)
    media = float(np.mean(x))
    mediana = float(np.median(x))
    moda_res = sp_stats.mode(x, keepdims=True)
    moda = float(moda_res.mode[0])
    varianza = float(np.var(x, ddof=1))
    desv_std = float(np.std(x, ddof=1))
    cv = (desv_std / media * 100) if media != 0 else 0.0
    sesgo = float(sp_stats.skew(x))
    curtosis = float(sp_stats.kurtosis(x))
    q1 = float(np.percentile(x, 25))
    q3 = float(np.percentile(x, 75))
    return ResumenDescriptivo(
        n=n, media=media, mediana=mediana, moda=moda,
        varianza=varianza, desv_std=desv_std, coef_variacion=cv,
        sesgo=sesgo, curtosis=curtosis,
        minimo=float(x.min()), maximo=float(x.max()),
        rango=float(x.max() - x.min()),
        q1=q1, q3=q3, iqr=float(q3 - q1),
    )


def frecuencias(datos: list[float], n_bins: int = 6) -> dict[str, int]:
    x = np.array(datos, dtype=float)
    counts, edges = np.histogram(x, bins=n_bins)
    result = {}
    for i, c in enumerate(counts):
        key = f"{edges[i]:.1f}–{edges[i+1]:.1f}"
        result[key] = int(c)
    return result


def intervalo_confianza_media(datos: list[float], nivel: float = 0.95) -> tuple[float, float]:
    x = np.array(datos, dtype=float)
    n = len(x)
    media = np.mean(x)
    se = sp_stats.sem(x)
    t = sp_stats.t.ppf((1 + nivel) / 2, df=n - 1)
    margen = t * se
    return float(media - margen), float(media + margen)
