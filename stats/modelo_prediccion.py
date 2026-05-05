# -*- coding: utf-8 -*-
"""Modelo predictivo: combina regresión lineal con distribución normal
para estimar la calificación esperada y la probabilidad de aprobar."""
import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass
from stats.regresion_lineal import ModeloRegresion, ajustar


@dataclass
class ResultadoPrediccion:
    calificacion_predicha: float
    prob_aprobar: float         # P(Y ≥ 6)
    prob_reprobar: float        # P(Y < 6)
    nivel: str
    profecia: str
    recomendaciones: list[str]


_PROFECIAS = {
    "Alto Rendimiento": [
        "Tu destino académico brilla con luz propia. Las estrellas conspiran a tu favor.",
        "El oráculo ve un camino de gloria. La oscuridad no alcanzará a quien tanto estudia.",
        "Las runas del conocimiento te sonríen. Tu futuro académico es radiante.",
    ],
    "Medio": [
        "Tu destino pende en el filo de la balanza. Luz y sombra luchan por tu alma académica.",
        "El oráculo percibe potencial sin alcanzar. Las sombras aún pueden disiparse.",
        "Estás en la encrucijada del destino. Cada hora de estudio inclina la balanza a tu favor.",
    ],
    "En Riesgo": [
        "Las profecías más oscuras te rodean... pero el destino aún puede cambiar.",
        "El abismo académico se acerca. Solo la perseverancia puede alterar esta profecía.",
        "Las sombras se ciernen. Actúa ahora antes de que el oráculo selle tu destino.",
    ],
}


def _profecia(nivel: str, seed: int = 0) -> str:
    opciones = _PROFECIAS.get(nivel, _PROFECIAS["Medio"])
    return opciones[seed % len(opciones)]


def _recomendaciones(asistencia: float, horas_estudio: float,
                     trabaja: bool, nivel: str) -> list[str]:
    rec = []
    if asistencia < 85:
        faltantes = max(0, round((85 - asistencia) / 100 * 16))
        rec.append(f"Aumenta tu asistencia — faltan ≈{faltantes} clases para llegar a 85 %.")
    if horas_estudio < 10:
        rec.append(f"Estudia al menos {10 - int(horas_estudio)} horas más por semana.")
    if trabaja:
        rec.append("Organiza un horario fijo: el trabajo no debe competir con la asistencia.")
    if nivel == "En Riesgo":
        rec.append("Solicita asesoría académica con tu docente esta semana.")
        rec.append("Usa plataformas educativas (Khan Academy, YouTube) para reforzar temas.")
    if nivel in ("En Riesgo", "Medio"):
        rec.append("Forma un grupo de estudio con compañeros de alto rendimiento.")
    if not rec:
        rec.append("¡Mantén el ritmo! Sigue asistiendo y estudiando con constancia.")
    return rec


class Oraculo:
    def __init__(self):
        self._modelo: ModeloRegresion | None = None

    def entrenar(self, asistencias: list[float], promedios: list[float]):
        self._modelo = ajustar(asistencias, promedios)

    def predecir(self, asistencia: float, horas_estudio: float,
                 trabaja: bool = False, seed: int = 0) -> ResultadoPrediccion:
        if self._modelo is None:
            raise RuntimeError("Modelo no entrenado. Llama a entrenar() primero.")

        cal = self._modelo.predecir(asistencia)
        # Ajuste leve por horas de estudio (contribución secundaria)
        cal += (horas_estudio - self._modelo.x_mean * 0.12) * 0.03
        cal = round(min(10.0, max(0.0, cal)), 2)

        # Probabilidad usando distribución normal centrada en la predicción
        se = max(self._modelo.error_std, 0.1)
        prob_ap = float(sp_stats.norm.sf(5.9, loc=cal, scale=se))
        prob_ap = max(0.0, min(1.0, prob_ap))

        # Clasificación
        if cal >= 8.5 and asistencia >= 85:
            nivel = "Alto Rendimiento"
        elif cal >= 7.0 and asistencia >= 70:
            nivel = "Medio"
        else:
            nivel = "En Riesgo"

        return ResultadoPrediccion(
            calificacion_predicha=cal,
            prob_aprobar=prob_ap,
            prob_reprobar=1 - prob_ap,
            nivel=nivel,
            profecia=_profecia(nivel, seed),
            recomendaciones=_recomendaciones(asistencia, horas_estudio, trabaja, nivel),
        )

    @property
    def modelo(self) -> ModeloRegresion | None:
        return self._modelo
