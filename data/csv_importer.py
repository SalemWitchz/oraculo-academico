# -*- coding: utf-8 -*-
"""Importa/exporta datos de estudiantes en CSV.

Soporta dos formatos:
  1. Google Forms (detectado por columna 'Marca temporal').
  2. Formato propio (snake_case, columnas simples).

Las asistencias se simulan deterministicamente cuando no están en el CSV.
"""
import csv
import re
import hashlib
import random
import unicodedata
from pathlib import Path
from data.estudiante import Estudiante


# ── Helpers generales ─────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", str(s))
    sin_acento = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return sin_acento.strip().lower()


def _to_float(s: str) -> float | None:
    s = s.strip()
    if not s or _norm(s) in ("no confirmado", "n/a", "-", "na", ""):
        return None
    try:
        return float(s)
    except ValueError:
        m = re.search(r"\d+\.?\d*", s)
        return float(m.group()) if m else None


def _rango_h(s: str) -> float:
    """Convierte un rango textual de horas a su punto medio."""
    v = _norm(s)
    if not v or "0 hora" in v or v == "0":
        return 0.0
    if "menos de 1" in v:
        return 0.5
    if "menos de 2" in v:
        return 1.0
    if "1 a 2" in v or "1-2" in v:
        return 1.5
    if "1 a 4" in v or "1-4" in v:
        return 2.5
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
    v = _norm(s)
    return "trabaja" in v and "no" not in v.split("trabaja")[0].strip().split()[-1:]


def _parse_bool_si(s: str) -> bool:
    v = _norm(s)
    return v in ("si", "s", "yes", "1", "verdadero", "true")


def _parse_n_reprobadas(s: str) -> int:
    v = _norm(s)
    if not v:
        return 0
    m = re.search(r"\d+", v)
    return int(m.group()) if m else 0


def _capitalizar(s: str) -> str:
    return s.strip().capitalize() if s else ""


def _detect_encoding(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                f.read(1024)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"


# ── Simulación determinista de asistencia ─────────────────────────────────────

def _simular_asistencia(nombre: str, trabaja: bool, h_trabajo_dia: float,
                         frecuencia: str, estres: str, gestion: bool) -> float:
    seed = int(hashlib.md5(nombre.encode("utf-8", errors="replace")).hexdigest()[:8], 16)
    rng  = random.Random(seed)

    base = 84.0

    if trabaja:
        base -= min(h_trabajo_dia * 1.8, 14.0)

    freq_map = {"siempre": 9, "frecuentemente": 4, "a veces": 0, "nunca": -9}
    base += freq_map.get(_norm(frecuencia), 0)

    base += 4 if gestion else -3

    stress_map = {"bajo": 3, "medio": 0, "alto": -5}
    base += stress_map.get(_norm(estres), 0)

    return round(min(100.0, max(58.0, base + rng.uniform(-6, 6))), 1)


# ── Diagnóstico global ────────────────────────────────────────────────────────
_ultimo_diagnostico: dict = {}


def get_diagnostico() -> dict:
    return _ultimo_diagnostico


# ── Detección de formato ──────────────────────────────────────────────────────

def _is_google_forms(fieldnames: list[str]) -> bool:
    return any("marca temporal" in _norm(h) for h in fieldnames)


# ── Búsqueda de columnas ──────────────────────────────────────────────────────

def _find_col(col_n: dict[str, str], *keywords) -> str | None:
    for kw in keywords:
        for n, orig in col_n.items():
            if kw in n:
                return orig
    return None


def _find_work_hours_col(col_n: dict[str, str]) -> str | None:
    candidates = []
    for n, orig in col_n.items():
        if "cuantas horas al dia" in n or "cuantas horas al d" in n:
            if ("estudio" not in n and "computadora" not in n
                    and "actividades" not in n and "dedicas" not in n):
                candidates.append((len(n), orig))
    candidates.sort()
    return candidates[0][1] if candidates else None


def _grade_columns(col_n: dict[str, str]) -> list[str]:
    result = []
    for n, orig in col_n.items():
        if "calificacion de" in n and "promedio" not in n:
            result.append(orig)
    return result


# ── Parser: Google Forms ──────────────────────────────────────────────────────

def _importar_google_forms(reader, fieldnames: list[str]) -> tuple[list[Estudiante], dict]:
    col_n = {_norm(h): h for h in fieldnames}

    c_nombre   = _find_col(col_n, "nombre completo", "tu nombre", "apellidos")
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

    # Campos extendidos
    c_genero       = _find_col(col_n, "genero", "sexo")
    c_frecuencia   = _find_col(col_n, "frecuencia estudias", "frecuencia de manera")
    c_herramientas = _find_col(col_n, "herramientas digitales")
    c_estilo       = _find_col(col_n, "tipo de aprendizaje", "aprendizaje prefieres")
    c_plat_usa     = _find_col(col_n, "usa usted plataformas", "plataformas educativas")
    c_estres       = _find_col(col_n, "nivel de estres", "estres academico")
    c_gestion      = _find_col(col_n, "gestion del tiempo", "buena gestion")
    c_abandonar    = _find_col(col_n, "abandonar la carrera", "pensado en abandonar")
    c_dificultad   = _find_col(col_n, "principal dificultad", "dificultad academica")
    c_preparado    = _find_col(col_n, "sientes preparado", "exigencias academicas")
    c_reprobo      = _find_col(col_n, "reprobado alguna materia", "has reprobado alguna")
    c_n_reprobadas = _find_col(col_n, "cuantas materias has reprobado")

    mapeadas = {k: v for k, v in {
        "nombre":             c_nombre,
        "id/matricula":       c_id,
        "carrera":            c_carrera,
        "promedio_final":     c_promedio,
        "horas_estudio":      c_estudio,
        "horas_plataformas":  c_compu,
        "trabaja":            c_laboral,
        "horas_trabajo":      c_h_trab,
        "genero":             c_genero,
        "frecuencia_estudio": c_frecuencia,
        "herramientas":       c_herramientas,
        "estilo_aprendizaje": c_estilo,
        "usa_plataformas":    c_plat_usa,
        "nivel_estres":       c_estres,
        "buena_gestion":      c_gestion,
        "penso_abandonar":    c_abandonar,
        "dificultad":         c_dificultad,
        "preparado":          c_preparado,
        "reprobo":            c_reprobo,
        "n_reprobadas":       c_n_reprobadas,
    }.items() if v}

    _ignore = {"marca temporal", "timestamp", "direccion de correo electronico",
               "correo electronico", "email", "cuales",
               "en caso de haber respondido", "si respondiste si",
               "edad", "si respondiste s"}
    columnas_usadas = set(mapeadas.values()) | set(grade_cols)
    sin_mapear = [h for h in fieldnames if h not in columnas_usadas
                  and not any(ig in _norm(h) for ig in _ignore)]

    estudiantes: list[Estudiante] = []
    errores: list[str] = []

    for i, row in enumerate(reader, start=1):
        def get(col, default=""):
            return (row.get(col) or default).strip() if col else default

        nombre  = get(c_nombre)  or f"Estudiante {i}"
        id_     = get(c_id)      or str(i)
        carrera = get(c_carrera) or "No especificada"

        # Promedio
        prom = _to_float(get(c_promedio))
        if prom is None or prom < 1.0:
            grades = [_to_float(row.get(c, "")) for c in grade_cols]
            grades = [g for g in grades if g is not None and 1.0 <= g <= 10.0]
            if not grades:
                errores.append(f"Fila {i} ({nombre}): sin promedio válido, omitida.")
                continue
            prom = sum(grades) / len(grades)
        prom = round(min(10.0, max(0.0, prom)), 4)

        # Horas
        h_est      = round(_rango_h(get(c_estudio)) * 5, 1)
        h_plat     = round(_rango_h(get(c_compu)), 1)
        lab        = get(c_laboral)
        trabaja    = _parse_bool_lab(lab)
        h_trab_dia = _rango_h(get(c_h_trab)) if trabaja else 0.0
        h_trab     = int(h_trab_dia * 5)

        # Campos extendidos
        genero           = get(c_genero)
        frecuencia_raw   = get(c_frecuencia)
        frecuencia       = _capitalizar(_norm(frecuencia_raw))
        estilo_raw       = get(c_estilo)
        estilo           = _capitalizar(_norm(estilo_raw))
        usa_herramientas = _parse_bool_si(get(c_herramientas))
        usa_plat         = _parse_bool_si(get(c_plat_usa))
        estres_raw       = get(c_estres)
        estres           = _capitalizar(_norm(estres_raw))
        buena_gestion    = _parse_bool_si(get(c_gestion))
        penso_abandonar  = _parse_bool_si(get(c_abandonar))
        dificultad       = get(c_dificultad)
        preparado        = _parse_bool_si(get(c_preparado))
        reprobo          = _parse_bool_si(get(c_reprobo))
        n_reprobadas     = _parse_n_reprobadas(get(c_n_reprobadas))

        # Asistencia simulada
        asistencia = _simular_asistencia(
            nombre, trabaja, h_trab_dia,
            frecuencia_raw, estres_raw, buena_gestion
        )

        try:
            e = Estudiante(
                id=id_, nombre=nombre, carrera=carrera,
                semestre=4, materia="Rendimiento General",
                parcial1=prom, parcial2=prom, parcial3=prom,
                tareas=prom,   proyecto=prom,
                porcentaje_asistencia=asistencia,
                horas_estudio=h_est,
                horas_plataformas=h_plat,
                trabaja=trabaja,
                horas_trabajo=h_trab,
                genero=genero,
                frecuencia_estudio=frecuencia,
                estilo_aprendizaje=estilo,
                usa_herramientas=usa_herramientas,
                usa_plataformas=usa_plat,
                nivel_estres=estres,
                buena_gestion=buena_gestion,
                penso_abandonar=penso_abandonar,
                dificultad_principal=dificultad,
                se_siente_preparado=preparado,
                reprobo=reprobo,
                n_reprobadas=n_reprobadas,
            )
            estudiantes.append(e)
        except Exception as ex:
            errores.append(f"Fila {i} ({nombre}): {ex}")

    diagnostico = {
        "formato":                 "Google Forms",
        "encoding":                "detectado",
        "columnas_mapeadas":       mapeadas,
        "columnas_sin_mapear":     sin_mapear,
        "columnas_calificaciones": grade_cols,
        "errores":                 errores,
    }
    return estudiantes, diagnostico


# ── Parser: Formato propio ────────────────────────────────────────────────────

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
    "genero": "genero", "nivel_estres": "nivel_estres",
    "frecuencia_estudio": "frecuencia_estudio",
    "estilo_aprendizaje": "estilo_aprendizaje",
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
                        ("true", "si", "1", "yes", "verdadero"),
                horas_trabajo=int(float(d.get("horas_trabajo", 0))),
                genero=d.get("genero", ""),
                nivel_estres=d.get("nivel_estres", ""),
                frecuencia_estudio=d.get("frecuencia_estudio", ""),
                estilo_aprendizaje=d.get("estilo_aprendizaje", ""),
            )
            estudiantes.append(e)
        except Exception as ex:
            errores.append(f"Fila {i}: {ex}")

    diagnostico = {
        "formato":           "Propio",
        "columnas_mapeadas": {v: v for v in mapeo.values()},
        "columnas_sin_mapear": sin_mapear,
        "errores":           errores,
    }
    return estudiantes, diagnostico


# ── Función pública ───────────────────────────────────────────────────────────

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

    diag["encoding"]       = enc
    diag["total_cargados"] = len(estudiantes)
    _ultimo_diagnostico    = diag
    return estudiantes


# ── Exportar ──────────────────────────────────────────────────────────────────

def exportar(estudiantes: list[Estudiante], ruta: str):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "nombre", "carrera", "semestre", "materia",
            "parcial1", "parcial2", "parcial3", "tareas", "proyecto",
            "porcentaje_asistencia", "horas_estudio", "horas_plataformas",
            "trabaja", "horas_trabajo",
            "genero", "frecuencia_estudio", "estilo_aprendizaje",
            "usa_herramientas", "usa_plataformas", "nivel_estres",
            "buena_gestion", "penso_abandonar", "dificultad_principal",
            "se_siente_preparado", "reprobo", "n_reprobadas",
            "promedio_final", "nivel",
        ])
        for e in estudiantes:
            writer.writerow([
                e.id, e.nombre, e.carrera, e.semestre, e.materia,
                e.parcial1, e.parcial2, e.parcial3, e.tareas, e.proyecto,
                e.porcentaje_asistencia, e.horas_estudio, e.horas_plataformas,
                e.trabaja, e.horas_trabajo,
                e.genero, e.frecuencia_estudio, e.estilo_aprendizaje,
                e.usa_herramientas, e.usa_plataformas, e.nivel_estres,
                e.buena_gestion, e.penso_abandonar, e.dificultad_principal,
                e.se_siente_preparado, e.reprobo, e.n_reprobadas,
                round(e.promedio_final, 2), e.nivel,
            ])
