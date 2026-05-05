# -*- coding: utf-8 -*-
"""Importa/exporta datos de estudiantes en CSV.

Soporta dos formatos:
  1. Formato propio (columnas en inglés snake_case).
  2. Exportación de Google Forms (detecta por columna 'Marca temporal').
"""
import csv
import os
from pathlib import Path
from data.estudiante import Estudiante


# Mapeo de posibles nombres de columna del Google Form → campo interno
_MAP = {
    "nombre":                          "nombre",
    "carrera":                         "carrera",
    "semestre":                        "semestre",
    "materia":                         "materia",
    "parcial 1":                       "parcial1",
    "calificación parcial 1":          "parcial1",
    "parcial 2":                       "parcial2",
    "calificación parcial 2":          "parcial2",
    "parcial 3":                       "parcial3",
    "calificación parcial 3":          "parcial3",
    "tareas":                          "tareas",
    "promedio de tareas":              "tareas",
    "proyecto":                        "proyecto",
    "calificación del proyecto":       "proyecto",
    "porcentaje_asistencia":           "porcentaje_asistencia",
    "asistencia (%)":                  "porcentaje_asistencia",
    "% asistencia":                    "porcentaje_asistencia",
    "horas_estudio":                   "horas_estudio",
    "horas de estudio por semana":     "horas_estudio",
    "horas_plataformas":               "horas_plataformas",
    "horas de uso de plataformas":     "horas_plataformas",
    "trabaja":                         "trabaja",
    "¿trabaja actualmente?":           "trabaja",
    "horas_trabajo":                   "horas_trabajo",
    "horas de trabajo por semana":     "horas_trabajo",
}


def _norm(s: str) -> str:
    return s.strip().lower()


def importar(ruta: str) -> list[Estudiante]:
    estudiantes = []
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = {_norm(h): h for h in reader.fieldnames or []}

        for i, row in enumerate(reader, start=1):
            d = {}
            for norm_h, orig_h in headers.items():
                campo = _MAP.get(norm_h)
                if campo:
                    d[campo] = row[orig_h].strip()

            try:
                e = Estudiante(
                    id=d.get("id", str(i)),
                    nombre=d.get("nombre", f"Estudiante {i}"),
                    carrera=d.get("carrera", "No especificada"),
                    semestre=int(d.get("semestre", 1)),
                    materia=d.get("materia", "No especificada"),
                    parcial1=float(d.get("parcial1", 0)),
                    parcial2=float(d.get("parcial2", 0)),
                    parcial3=float(d.get("parcial3", 0)),
                    tareas=float(d.get("tareas", 0)),
                    proyecto=float(d.get("proyecto", 0)),
                    porcentaje_asistencia=float(d.get("porcentaje_asistencia", 0)),
                    horas_estudio=float(d.get("horas_estudio", 0)),
                    horas_plataformas=float(d.get("horas_plataformas", 0)),
                    trabaja=str(d.get("trabaja", "false")).lower() in ("true", "sí", "si", "1", "yes"),
                    horas_trabajo=int(float(d.get("horas_trabajo", 0))),
                )
                estudiantes.append(e)
            except (ValueError, KeyError):
                continue  # fila malformada, se omite

    return estudiantes


def exportar(estudiantes: list[Estudiante], ruta: str):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "nombre", "carrera", "semestre", "materia",
            "parcial1", "parcial2", "parcial3", "tareas", "proyecto",
            "porcentaje_asistencia", "horas_estudio", "horas_plataformas",
            "trabaja", "horas_trabajo", "promedio_final", "nivel",
        ])
        for e in estudiantes:
            writer.writerow([
                e.id, e.nombre, e.carrera, e.semestre, e.materia,
                e.parcial1, e.parcial2, e.parcial3, e.tareas, e.proyecto,
                e.porcentaje_asistencia, e.horas_estudio, e.horas_plataformas,
                e.trabaja, e.horas_trabajo, round(e.promedio_final, 2), e.nivel,
            ])
