# -*- coding: utf-8 -*-
"""Singleton que centraliza todos los datos cargados en la sesión."""
from __future__ import annotations
from typing import List, Callable
import pandas as pd
from data.estudiante import Estudiante


class DataStore:
    _instance: "DataStore | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._estudiantes: List[Estudiante] = []
            cls._instance._observers: List[Callable] = []
        return cls._instance

    @classmethod
    def get(cls) -> "DataStore":
        return cls()

    # Acceso
    @property
    def estudiantes(self) -> List[Estudiante]:
        return self._estudiantes

    def set_estudiantes(self, lista: List[Estudiante]):
        self._estudiantes = lista
        self._notify()

    def add(self, e: Estudiante):
        self._estudiantes.append(e)
        self._notify()

    def remove(self, idx: int):
        del self._estudiantes[idx]
        self._notify()

    def clear(self):
        self._estudiantes.clear()
        self._notify()

    # Observadores
    def subscribe(self, fn: Callable):
        self._observers.append(fn)

    def _notify(self):
        for fn in self._observers:
            fn()

    # Utilidades
    def to_df(self) -> pd.DataFrame:
        if not self._estudiantes:
            return pd.DataFrame()
        rows = [
            {
                "ID": e.id,
                "Nombre": e.nombre,
                "Carrera": e.carrera,
                "Semestre": e.semestre,
                "Materia": e.materia,
                "Parcial 1": e.parcial1,
                "Parcial 2": e.parcial2,
                "Parcial 3": e.parcial3,
                "Tareas": e.tareas,
                "Proyecto": e.proyecto,
                "Asistencia %": e.porcentaje_asistencia,
                "Hrs. Estudio": e.horas_estudio,
                "Hrs. Plataformas": e.horas_plataformas,
                "Trabaja": "Sí" if e.trabaja else "No",
                "Hrs. Trabajo": e.horas_trabajo,
                "Promedio": round(e.promedio_final, 2),
                "Nivel": e.nivel,
            }
            for e in self._estudiantes
        ]
        return pd.DataFrame(rows)

    def count_by_nivel(self) -> dict:
        c = {"Alto Rendimiento": 0, "Medio": 0, "En Riesgo": 0}
        for e in self._estudiantes:
            c[e.nivel] += 1
        return c

    def asistencias(self) -> list:
        return [e.porcentaje_asistencia for e in self._estudiantes]

    def promedios(self) -> list:
        return [e.promedio_final for e in self._estudiantes]
