# -*- coding: utf-8 -*-
"""Importa/exporta datos de estudiantes en CSV.

Soporta dos formatos:
  1. Google Forms (detectado por columna 'Marca temporal').
  2. Formato propio (snake_case, columnas simples).
"""
import csv
import re
import unicodedata
from pathlib import Path
from data.estudiante import Estudiante


# ── Helpers generales ─────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Quita acentos, pone en minúsculas, elimina espacios."""
    nfkd = unicodedata.normalize("NFD", str(s))
    sin_acento = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return sin_acento.strip().lower()


def _to_float(s: str) -> float | None:
    """Extrae el primer número de una cadena; None si no hay."""
    s = s.strip()
    if not s or _norm(s) in ("no confirmado", "n/a", "-", "na", ""):
        return None
    try:
        return float(s)
    except ValueError:
        m = re.search(r"\d+\.?\d*", s)
        return float(m.group()) if m else None


def _rango_h(s: str) -> float:
    """Convierte un rango textual de horas a número (promedio del rango)."""
    v = _norm(s)
    if not v or "0 hora" in v or v == "0":
        return 0.0
    if "menos de 1" in v:
        return 0.5
    if "menos de 2" in v:
        return 1.0
    if "1 a 2" in v or "1-2" in v:
        return 1.5
    if "2 a 4" in v or "2-4" in v:
        return 3.0
    if "3 a 4" in v or "3-4" in v:
        return 3.5
    if "5 a 7" in v or "5-7" in v:
        return 6.0
    if "5 a 8" in v or "5-8" in v:
        return 6.5
    if "mas de 8" in v:
        return 9.0
    if "mas de 7" in v:
        return 8.0
    if "mas de 6" in v:
        return 7.0
    f = _to_float(s)
    return f if f is not None else 0.0


def _parse_bool_lab(s: str) -> bool:
    """'Trabaja' → True, 'No trabaja' → False."""
    v = _norm(s)
    return "trabaja" in v and "no" not in v.split("trabaja")[0].strip().split()[-1:]


def _detect_encoding(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                f.read(1024)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"


# ── Diagnóstico global (leído por la UI) ──────────────────────────────────────
_ultimo_diagnostico: dict = {}


def get_diagnostico() -> dict:
    return _ultimo_diagnostico


# ── Detección de formato ──────────────────────────────────────────────────────

def _is_google_forms(fieldnames: list[str]) -> bool:
    return any("marca temporal" in _norm(h) for h in fieldnames)


# ── Parser: Google Forms ──────────────────────────────────────────────────────

def _find_col(col_n: dict[str, str], *keywords) -> str | None:
    """Devuelve el nombre original de la primera columna que contiene algún keyword."""
    for kw in keywords:
        for n, orig in col_n.items():
            if kw in n:
                return orig
    return None


def _find_work_hours_col(col_n: dict[str, str]) -> str | None:
    """'¿Cuántas horas al día?' sin calificador (para horas de trabajo)."""
    candidates = []
    for n, orig in col_n.items():
        if "cuantas horas al dia" in n or "cuantas horas al d" in n:
            if "estudio" not in n and "computadora" not in n and "actividades" not in n:
                candidates.append((len(n), orig))
    candidates.sort()
    return candidates[0][1] if candidates else None


def _grade_columns(col_n: dict[str, str]) -> list[str]:
    """Columnas que representan calificaciones de materias individuales."""
    result = []
    for n, orig in col_n.items():
        if "calificacion de" in n and "promedio" not in n:
            result.append(orig)
    return result


def _importar_google_forms(reader, fieldnames: list[str]) -> tuple[list[Estudiante], dict]:
    col_n = {_norm(h): h for h in fieldnames}

    # ── Mapeo de columnas ──────────────────────────────────────────────
    c_nombre   = _find_col(col_n, "nombre completo", "tu nombre")
    c_id       = _find_col(col_n, "matricula", "matricul", "num. control",
                            "numero de control", "no. de cuenta", "cuenta")
    c_carrera  = _find_col(col_n, "carrera")
    c_promedio = _find_col(col_n, "promedio general", "promedio")
    c_estudio  = _find_col(col_n, "horas al dia dedicas al estudio",
                            "estudio fuera del horario", "horas de estudio")
    c_compu    = _find_col(col_n, "horas al dia usas la computadora",
                            "computadora para actividades academicas",
                            "horas en computadora")
    c_laboral  = _find_col(col_n, "situacion laboral")
    c_h_trab   = _find_work_hours_col(col_n)
    grade_cols = _grade_columns(col_n)

    mapeadas = {k: v for k, v in {
        "nombre":           c_nombre,
        "id/matricula":     c_id,
        "carrera":          c_carrera,
        "promedio_final":   c_promedio,
        "horas_estudio":    c_estudio,
        "horas_plataformas":c_compu,
        "trabaja":          c_laboral,
        "horas_trabajo":    c_h_trab,
    }.items() if v}

    columnas_usadas = set(mapeadas.values()) | set(grade_cols)
    sin_mapear = [h for h in fieldnames if h not in columnas_usadas
                  and _norm(h) not in ("marca temporal", "timestamp",
                                       "direccion de correo electronico",
                                       "correo electronico", "email")]

    estudiantes: list[Estudiante] = []
    errores: list[str] = []

    for i, row in enumerate(reader, start=1):
        def get(col, default=""):
            return (row.get(col) or default).strip() if col else default

        nombre  = get(c_nombre)  or f"Estudiante {i}"
        id_     = get(c_id)      or str(i)
        carrera = get(c_carrera) or "No especificada"

        # ── Promedio final ─────────────────────────────────────────────
        prom = _to_float(get(c_promedio))
        if prom is None:
            # Calcular como promedio de calificaciones individuales válidas
            grades = [_to_float(row.get(c, "")) for c in grade_cols]
            grades = [g for g in grades if g is not None and 0 <= g <= 10]
            if not grades:
                errores.append(f"Fila {i} ({nombre}): sin promedio válido, omitida.")
                continue
            prom = sum(grades) / len(grades)
        prom = round(min(10.0, max(0.0, prom)), 4)

        # ── Horas (daily → weekly para estudio y trabajo) ──────────────
        h_est  = round(_rango_h(get(c_estudio))  * 5, 1)   # dias/semana
        h_plat = round(_rango_h(get(c_compu)),    1)        # horas/día
        lab    = get(c_laboral)
        trabaja = _parse_bool_lab(lab)
        h_trab = int(_rango_h(get(c_h_trab)) * 5) if trabaja else 0

        try:
            # Usamos el promedio reportado en todos los campos de nota
            # para que Estudiante.recalcular() devuelva exactamente ese valor
            e = Estudiante(
                id=id_,
                nombre=nombre,
                carrera=carrera,
                semestre=4,                    # implícito en el form
                materia="Rendimiento General",
                parcial1=prom,
                parcial2=prom,
                parcial3=prom,
                tareas=prom,
                proyecto=prom,
                porcentaje_asistencia=0.0,     # el profesor lo agrega aparte
                horas_estudio=h_est,
                horas_plataformas=h_plat,
                trabaja=trabaja,
                horas_trabajo=h_trab,
            )
            estudiantes.append(e)
        except Exception as ex:
            errores.append(f"Fila {i} ({nombre}): {ex}")

    diagnostico = {
        "formato": "Google Forms",
        "encoding": "detectado",
        "columnas_mapeadas": mapeadas,
        "columnas_sin_mapear": sin_mapear,
        "columnas_calificaciones": grade_cols,
        "errores": errores,
    }
    return estudiantes, diagnostico


# ── Parser: Formato propio (snake_case) ───────────────────────────────────────

_MAP_PROPIO: dict[str, str] = {
    "nombre": "nombre", "carrera": "carrera", "semestre": "semestre",
    "materia": "materia", "parcial1": "parcial1", "parcial 1": "parcial1",
    "parcial2": "parcial2", "parcial 2": "parcial2",
    "parcial3": "parcial3", "parcial 3": "parcial3",
    "tareas": "tareas", "proyecto": "proyecto",
    "porcentaje_asistencia": "porcentaje_asistencia",
    "asistencia (%)": "porcentaje_asistencia", "asistencia": "porcentaje_asistencia",
    "horas_estudio": "horas_estudio", "horas de estudio": "horas_estudio",
    "horas_plataformas": "horas_plataformas",
    "trabaja": "trabaja", "horas_trabajo": "horas_trabajo",
}


def _importar_formato_propio(reader, fieldnames: list[str]) -> tuple[list[Estudiante], dict]:
    col_n = {_norm(h): h for h in fieldnames}
    mapeo: dict[str, str] = {}
    for n, orig in col_n.items():
        campo = _MAP_PROPIO.get(n)
        if campo and campo not in mapeo.values():
            mapeo[orig] = campo

    sin_mapear = [h for h in fieldnames if h not in mapeo]
    estudiantes: list[Estudiante] = []
    errores: list[str] = []

    for i, row in enumerate(reader, start=1):
        d = {campo: (row.get(orig) or "").strip()
             for orig, campo in mapeo.items()}
        try:
            e = Estudiante(
                id=d.get("id", str(i)),
                nombre=d.get("nombre", f"Estudiante {i}"),
                carrera=d.get("carrera", "No especificada"),
                semestre=int(float(d.get("semestre", 1))),
                materia=d.get("materia", "No especificada"),
                parcial1=float(d.get("parcial1", 0)),
                parcial2=float(d.get("parcial2", 0)),
                parcial3=float(d.get("parcial3", 0)),
                tareas=float(d.get("tareas", 0)),
                proyecto=float(d.get("proyecto", 0)),
                porcentaje_asistencia=float(d.get("porcentaje_asistencia", 0)),
                horas_estudio=float(d.get("horas_estudio", 0)),
                horas_plataformas=float(d.get("horas_plataformas", 0)),
                trabaja=_norm(d.get("trabaja", "")) in
                        ("true", "si", "si", "1", "yes", "verdadero"),
                horas_trabajo=int(float(d.get("horas_trabajo", 0))),
            )
            estudiantes.append(e)
        except Exception as ex:
            errores.append(f"Fila {i}: {ex}")

    diagnostico = {
        "formato": "Propio",
        "columnas_mapeadas": {v: v for v in mapeo.values()},
        "columnas_sin_mapear": sin_mapear,
        "errores": errores,
    }
    return estudiantes, diagnostico


# ── Función pública principal ─────────────────────────────────────────────────

def importar(ruta: str) -> list[Estudiante]:
    global _ultimo_diagnostico
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    enc = _detect_encoding(path)

    with open(path, newline="", encoding=enc) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        if _is_google_forms(fieldnames):
            estudiantes, diag = _importar_google_forms(reader, fieldnames)
        else:
            estudiantes, diag = _importar_formato_propio(reader, fieldnames)

    diag["encoding"] = enc
    diag["total_cargados"] = len(estudiantes)
    _ultimo_diagnostico = diag
    return estudiantes


# ── Exportar ──────────────────────────────────────────────────────────────────

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
                e.trabaja, e.horas_trabajo,
                round(e.promedio_final, 2), e.nivel,
            ])
