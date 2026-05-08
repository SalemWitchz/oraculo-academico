# -*- coding: utf-8 -*-
from dataclasses import dataclass, field


@dataclass
class Estudiante:
    id: str
    nombre: str
    carrera: str
    semestre: int
    materia: str

    parcial1: float
    parcial2: float
    parcial3: float
    tareas: float
    proyecto: float

    porcentaje_asistencia: float   # 0–100 (simulada si no hay dato)
    horas_estudio: float           # semanales
    horas_plataformas: float       # diarias
    trabaja: bool
    horas_trabajo: int             # semanales (0 si no trabaja)

    # Campos extendidos del formulario (opcionales)
    genero:              str  = ""
    frecuencia_estudio:  str  = ""    # Siempre / Frecuentemente / A veces / Nunca
    estilo_aprendizaje:  str  = ""    # Mixto / Practico / Visual / Teorico
    usa_herramientas:    bool = False
    usa_plataformas:     bool = False
    nivel_estres:        str  = ""    # Alto / Medio / Bajo
    buena_gestion:       bool = False
    penso_abandonar:     bool = False
    dificultad_principal: str = ""
    se_siente_preparado: bool = False
    reprobo:             bool = False
    n_reprobadas:        int  = 0

    # Calculados automáticamente
    promedio_final: float = field(init=False)
    nivel:          str   = field(init=False)

    def __post_init__(self):
        self.recalcular()

    def recalcular(self):
        self.promedio_final = round(
            min(10.0, max(0.0,
                self.parcial1 * 0.25 +
                self.parcial2 * 0.25 +
                self.parcial3 * 0.25 +
                self.tareas   * 0.15 +
                self.proyecto * 0.10
            )), 4)
        self._clasificar()

    def _clasificar(self):
        if self.promedio_final >= 8.5 and self.porcentaje_asistencia >= 85:
            self.nivel = "Alto Rendimiento"
        elif self.promedio_final >= 7.0 and self.porcentaje_asistencia >= 70:
            self.nivel = "Medio"
        else:
            self.nivel = "En Riesgo"

    def __str__(self):
        return f"{self.nombre} ({self.id})"
