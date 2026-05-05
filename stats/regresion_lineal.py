# -*- coding: utf-8 -*-
"""Regresión lineal simple (mínimos cuadrados, implementación manual).

Variable independiente (X): porcentaje de asistencia
Variable dependiente   (Y): promedio final
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class ModeloRegresion:
    beta0: float        # intercepto
    beta1: float        # pendiente
    r: float            # correlación de Pearson
    r2: float           # coeficiente de determinación
    error_std: float    # error estándar de la regresión
    n: int
    x_mean: float
    y_mean: float

    # ── Predicción ────────────────────────────────────────────────────
    def predecir(self, x: float) -> float:
        return self.beta0 + self.beta1 * x

    # ── Representación ────────────────────────────────────────────────
    def ecuacion(self) -> str:
        signo = "+" if self.beta0 >= 0 else "-"
        return f"y^ = {self.beta1:.4f}*x {signo} {abs(self.beta0):.4f}"

    def tabla(self) -> list[tuple[str, str]]:
        return [
            ("Intercepto (β₀)",         f"{self.beta0:.4f}"),
            ("Pendiente (β₁)",          f"{self.beta1:.4f}"),
            ("Correlación de Pearson r",f"{self.r:.4f}"),
            ("Coef. Determinación R²",  f"{self.r2:.4f}"),
            ("Error Estándar (SE)",     f"{self.error_std:.4f}"),
            ("Muestra (n)",             str(self.n)),
            ("Ecuación",               self.ecuacion()),
        ]


def ajustar(x_vals: list[float], y_vals: list[float]) -> ModeloRegresion:
    x = np.array(x_vals, dtype=float)
    y = np.array(y_vals, dtype=float)
    n = len(x)

    x_m = x.mean()
    y_m = y.mean()

    ss_xy = np.sum((x - x_m) * (y - y_m))
    ss_xx = np.sum((x - x_m) ** 2)
    ss_yy = np.sum((y - y_m) ** 2)

    beta1 = ss_xy / ss_xx
    beta0 = y_m - beta1 * x_m
    r = ss_xy / np.sqrt(ss_xx * ss_yy)

    y_hat = beta0 + beta1 * x
    ss_res = np.sum((y - y_hat) ** 2)
    se = np.sqrt(ss_res / (n - 2)) if n > 2 else 0.0

    return ModeloRegresion(
        beta0=float(beta0), beta1=float(beta1),
        r=float(r), r2=float(r ** 2),
        error_std=float(se), n=n,
        x_mean=float(x_m), y_mean=float(y_m),
    )
