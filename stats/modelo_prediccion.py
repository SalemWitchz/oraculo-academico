# -*- coding: utf-8 -*-
"""Modelo predictivo basado en Hipótesis B (situación laboral → promedio).

Usa las medias y desviaciones del grupo "trabaja" vs "no trabaja" para
estimar la calificación esperada y la probabilidad de aprobar.
"""
import numpy as np
from scipy import stats as sp_stats
from dataclasses import dataclass


@dataclass
class ResultadoPrediccion:
    calificacion_predicha: float
    prob_aprobar: float         # P(Y >= 6)
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


def _recomendaciones(trabaja: bool, horas_estudio: float, nivel: str) -> list[str]:
    rec = []
    if trabaja:
        rec.append(
            "Tu situación laboral reduce el tiempo disponible para estudiar. "
            "Organiza un horario fijo y protege tus horas de estudio."
        )
        if nivel in ("En Riesgo", "Medio"):
            rec.append(
                "Evalúa reducir horas de trabajo si es posible, "
                "o busca apoyo institucional (becas, tutorías)."
            )
    if horas_estudio < 10:
        extra = 10 - int(horas_estudio)
        rec.append(f"Incrementa tu tiempo de estudio — al menos {extra} hrs/sem más harán diferencia.")
    if nivel == "En Riesgo":
        rec.append("Solicita asesoría académica con tu docente esta semana.")
        rec.append("Usa plataformas educativas (Khan Academy, YouTube) para reforzar temas.")
    if nivel in ("En Riesgo", "Medio"):
        rec.append("Forma un grupo de estudio con compañeros de alto rendimiento.")
    if not rec:
        rec.append("¡Mantén el ritmo! Sigue estudiando con constancia y disciplina.")
    return rec


class Oraculo:
    """Predice el promedio usando estadísticas del grupo (trabaja / no trabaja)."""

    def __init__(self):
        self._m_trab: float = 7.0
        self._s_trab: float = 1.0
        self._m_no:   float = 7.5
        self._s_no:   float = 1.0
        self._trained: bool = False

    def entrenar(self, promedios_trabaja: list[float], promedios_no_trabaja: list[float]):
        g1 = [x for x in promedios_trabaja   if x is not None]
        g2 = [x for x in promedios_no_trabaja if x is not None]
        if len(g1) >= 2:
            self._m_trab = float(np.mean(g1))
            self._s_trab = max(float(np.std(g1, ddof=1)), 0.1)
        if len(g2) >= 2:
            self._m_no = float(np.mean(g2))
            self._s_no = max(float(np.std(g2, ddof=1)), 0.1)
        self._trained = True

    def predecir(self, trabaja: bool, horas_estudio: float = 0.0,
                 seed: int = 0) -> ResultadoPrediccion:
        base = self._m_trab if trabaja else self._m_no
        se   = self._s_trab if trabaja else self._s_no

        ajuste = (horas_estudio - 10) * 0.04
        cal = round(min(10.0, max(0.0, base + ajuste)), 2)

        prob_ap = float(sp_stats.norm.sf(5.9, loc=cal, scale=se))
        prob_ap = max(0.0, min(1.0, prob_ap))

        if cal >= 8.5:
            nivel = "Alto Rendimiento"
        elif cal >= 7.0:
            nivel = "Medio"
        else:
            nivel = "En Riesgo"

        return ResultadoPrediccion(
            calificacion_predicha=cal,
            prob_aprobar=prob_ap,
            prob_reprobar=1 - prob_ap,
            nivel=nivel,
            profecia=_profecia(nivel, seed),
            recomendaciones=_recomendaciones(trabaja, horas_estudio, nivel),
        )

    @property
    def media_trabaja(self) -> float:
        return self._m_trab

    @property
    def media_no_trabaja(self) -> float:
        return self._m_no
