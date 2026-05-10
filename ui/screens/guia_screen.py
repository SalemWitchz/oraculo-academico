# -*- coding: utf-8 -*-
"""? Guía de Uso — Manual interactivo de la aplicación."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY, BG_INPUT,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER, COLOR_BORDER_LT,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from ui.widgets import GothicCard, GothicButton, ScrollableFrame, SectionTitle


# Contenido de cada sección
_SECCIONES = [
    {
        "icono": "⊕",
        "titulo": "Paso 1 — Cargar Datos",
        "resumen": "Antes de usar cualquier análisis necesitas datos de estudiantes.",
        "pasos": [
            ("Importar CSV de Google Forms",
             "Haz clic en '⤓ Importar CSV'. El sistema detecta automáticamente el formato "
             "de Google Forms si el archivo contiene una columna 'Marca temporal'. "
             "Mapea columnas de nombre, carrera, promedio, horas de estudio, situación laboral y más."),
            ("Cargar datos de muestra",
             "Usa '★ Cargar datos de muestra' para cargar 35 estudiantes de ejemplo "
             "y explorar todas las funciones sin necesidad de un CSV real."),
            ("Agregar manualmente",
             "Haz clic en '+ Agregar estudiante manualmente' y llena el formulario. "
             "Ingresa las calificaciones de cada parcial, tareas, proyecto, asistencia y situación laboral."),
            ("Exportar",
             "Usa '⤑ Exportar CSV actual' para guardar los datos cargados en formato CSV estándar."),
        ],
        "tip": "El CSV de Google Forms debe incluir al menos: promedio/calificaciones, "
               "situación laboral (trabaja/no trabaja) y horas de trabajo.",
    },
    {
        "icono": "✦",
        "titulo": "Paso 2 — La Profecía (Predicción Individual)",
        "resumen": "Consulta la predicción de calificación para un estudiante específico.",
        "pasos": [
            ("Seleccionar estudiante",
             "Elige un estudiante del menú desplegable superior."),
            ("Consultar el Oráculo",
             "Presiona '✦ Consultar el Oráculo'. El sistema calcula la calificación "
             "predicha basándose en si el estudiante trabaja o no (Hipótesis B)."),
            ("Leer el medidor",
             "El arco circular muestra la calificación predicha sobre 10. "
             "Blanco = Alto Rendimiento (≥8.5), Gris = Nivel Medio (≥7.0), Rojo = En Riesgo (<7.0)."),
            ("Barra de probabilidad",
             "La barra bicolor muestra la probabilidad de aprobar (blanco) vs. reprobar (gris oscuro)."),
            ("Recomendaciones",
             "Abajo aparecen rituales/acciones recomendadas según el nivel y situación laboral."),
        ],
        "tip": "La predicción usa la media del grupo correspondiente "
               "(trabaja vs. no trabaja) más un ajuste por horas de estudio.",
    },
    {
        "icono": "✧",
        "titulo": "Paso 3 — El Grimorio (Estadística Completa)",
        "resumen": "Análisis estadístico completo: descriptiva, prueba de hipótesis y gráficas.",
        "pasos": [
            ("Estadística descriptiva",
             "Las dos primeras tablas muestran media, mediana, varianza, desviación estándar, "
             "sesgo, curtosis, IQR y el intervalo de confianza al 95% para promedios y asistencia."),
            ("Comparación de grupos",
             "La tabla 'Comparación de Grupos' muestra n, media y desviación estándar "
             "separados entre estudiantes que trabajan y los que no trabajan."),
            ("Prueba de Hipótesis B",
             "Muestra el resultado de la prueba t de Student: estadístico t, grados de libertad "
             "(n₁+n₂−2), p-valor (una cola), IC 95% de la diferencia, d de Cohen y conclusión."),
            ("Gráficas",
             "4 gráficas: distribución de promedios, histogramas superpuestos por grupo laboral, "
             "boxplots por carrera y pastel de niveles académicos."),
        ],
        "tip": "La prueba t de Student asume varianzas iguales entre grupos. "
               "Si p-valor < 0.05 aparece la conclusión en verde (se rechaza H₀). "
               "Si p-valor ≥ 0.05 aparece en rojo (no hay evidencia suficiente).",
    },
    {
        "icono": "⚖",
        "titulo": "Paso 4 — El Juicio Final (Simulación)",
        "resumen": "Simula cómo cambiaría la predicción si el estudiante cambia su situación laboral.",
        "pasos": [
            ("Elegir estudiante",
             "Selecciona al estudiante que quieres evaluar."),
            ("Cambiar la situación laboral",
             "Usa los botones de radio 'Trabaja' / 'No trabaja' para simular el escenario."),
            ("Pronunciar el Juicio",
             "Presiona '⚖ Pronunciar el Juicio' (o cambia el radio directamente). "
             "El medidor y la barra se actualizan en tiempo real."),
            ("Interpretar el resultado",
             "El texto muestra la diferencia entre el escenario real y el simulado. "
             "La barra de barras compara las medias grupales con el promedio real del estudiante."),
        ],
        "tip": "La gráfica de barras muestra la media del grupo 'Trabaja' en blanco "
               "y 'No trabaja' en gris. La línea punteada es el promedio real del estudiante.",
    },
    {
        "icono": "☽",
        "titulo": "Paso 5 — Los Rituales (Recomendaciones)",
        "resumen": "Lista de acciones recomendadas para cada estudiante según su nivel de riesgo.",
        "pasos": [
            ("Filtrar por nivel",
             "Usa los botones 'Todos / En Riesgo / Medio / Alto Rendimiento' "
             "para filtrar qué estudiantes ver."),
            ("Leer recomendaciones",
             "Cada tarjeta muestra nombre, carrera, promedio, asistencia, horas de estudio, "
             "si trabaja, y una lista de acciones concretas recomendadas."),
            ("Exportar rituales",
             "Haz clic en '⤓ Exportar CSV' para guardar todas las recomendaciones "
             "en un archivo CSV listo para compartir."),
        ],
        "tip": "Los estudiantes 'En Riesgo' reciben automáticamente recomendaciones "
               "sobre asesoría docente, grupos de estudio y plataformas de apoyo.",
    },
    {
        "icono": "H",
        "titulo": "Interpretación Estadística — Hipótesis B",
        "resumen": "Cómo leer e interpretar la prueba de hipótesis del sistema.",
        "pasos": [
            ("Hipótesis nula (H₀)",
             "H₀: μ_trabaja ≥ μ_no_trabaja — Se asume que trabajar NO reduce el promedio. "
             "Es lo que queremos refutar."),
            ("Hipótesis alternativa (H₁)",
             "H₁: μ_trabaja < μ_no_trabaja — Los que trabajan tienen promedio MENOR. "
             "Es lo que queremos demostrar con evidencia estadística."),
            ("Prueba t de Student (una cola izquierda)",
             "Se asume que las varianzas de ambos grupos son iguales (varianza combinada pooled). "
             "alternative='less' evalúa si el grupo 1 (trabaja) tiene media menor que el grupo 2. "
             "Grados de libertad: n₁ + n₂ − 2."),
            ("p-valor",
             "Si p < α (0.05): hay evidencia estadística para RECHAZAR H₀ → los que trabajan "
             "tienen promedio significativamente menor. "
             "Si p ≥ 0.05: no hay suficiente evidencia → no se rechaza H₀."),
            ("d de Cohen (tamaño del efecto)",
             "Mide la magnitud real de la diferencia. "
             "|d| < 0.2 = pequeño, 0.2–0.5 = mediano, 0.5–0.8 = grande, > 0.8 = muy grande."),
            ("IC 95% de la diferencia",
             "Intervalo de confianza para μ_trabaja − μ_no_trabaja. "
             "Si el intervalo es completamente negativo, confirma que el grupo 'trabaja' tiene menor media."),
        ],
        "tip": "α = 0.05 significa que aceptamos un 5% de probabilidad de error tipo I "
               "(rechazar H₀ cuando en realidad es verdadera).",
    },
    {
        "icono": "CSV",
        "titulo": "Formato del Archivo CSV",
        "resumen": "Qué columnas necesita el sistema para importar datos correctamente.",
        "pasos": [
            ("Formato propio (snake_case)",
             "Columnas mínimas: nombre, carrera, semestre, materia, parcial1, parcial2, parcial3, "
             "tareas, proyecto, porcentaje_asistencia, horas_estudio, horas_plataformas, "
             "trabaja (true/false/si/1), horas_trabajo."),
            ("Formato Google Forms (auto-detectado)",
             "Si el archivo tiene columna 'Marca temporal', se activa el parser de Google Forms. "
             "El sistema mapea automáticamente columnas largas como "
             "'Ingrese su promedio general de este 3 semestre:' → promedio."),
            ("Encoding",
             "El sistema prueba utf-8-sig → utf-8 → latin-1 → cp1252 automáticamente. "
             "Los archivos exportados desde Google Forms son usualmente utf-8 o latin-1."),
            ("Rangos de horas",
             "El parser convierte rangos textuales: '1 a 2 horas' → 1.5, '5 a 8 horas' → 6.5, "
             "'Más de 8 horas' → 9. Las horas diarias se multiplican x5 para obtener horas semanales."),
        ],
        "tip": "Si alguna columna importante no se reconoce, revisa el diagnóstico que aparece "
               "al importar — lista qué columnas se mapearon y cuáles fueron ignoradas.",
    },
]


class GuiaScreen:
    def __init__(self, win):
        self.win = win
        self._abiertos: dict[int, bool] = {}

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)

        # Encabezado
        hdr = tk.Frame(parent, bg=BG_MAIN)
        hdr.pack(fill="x", padx=24, pady=(12, 4))

        tk.Label(hdr, text="GUÍA DE USO",
                 font=("Palatino Linotype", 26, "bold"),
                 fg="#FFFFFF", bg=BG_MAIN, anchor="w").pack(side="left")
        tk.Frame(hdr, bg=COLOR_BORDER_LT, width=3).pack(
            side="left", fill="y", padx=14, pady=4)
        tk.Label(hdr,
                 text="Manual interactivo — haz clic en cada sección para expandirla",
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN, anchor="w").pack(side="left")

        tk.Frame(parent, bg=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=(4, 8))

        # Resumen de pantallas
        self._tarjetas_resumen(parent)

        # Secciones expandibles
        scroll = ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        inner = scroll.inner

        for idx, sec in enumerate(_SECCIONES):
            self._seccion(inner, idx, sec)

        tk.Label(inner, text="", bg=BG_MAIN).pack(pady=12)

    # Tarjetas de resumen
    def _tarjetas_resumen(self, parent):
        row = tk.Frame(parent, bg=BG_MAIN)
        row.pack(fill="x", padx=20, pady=(0, 8))
        items = [
            ("⊕", "Datos",       "Importar / editar"),
            ("✦", "Profecía",    "Predicción individual"),
            ("✧", "Grimorio",    "Estadística + hipótesis"),
            ("⚖", "Juicio",      "Simulación laboral"),
            ("☽", "Rituales",    "Recomendaciones"),
            ("?", "Guía",        "Este manual"),
        ]
        for icono, nombre, desc in items:
            card = tk.Frame(row, bg=BG_CARD,
                            highlightbackground=COLOR_BORDER,
                            highlightthickness=1)
            card.pack(side="left", fill="y", padx=4, pady=2, ipadx=10, ipady=8)
            tk.Label(card, text=icono,
                     font=("Palatino Linotype", 20, "bold"),
                     fg=COLOR_GOLD, bg=BG_CARD).pack()
            tk.Label(card, text=nombre,
                     font=("Palatino Linotype", 11, "bold"),
                     fg=COLOR_GOLD, bg=BG_CARD).pack()
            tk.Label(card, text=desc,
                     font=("Palatino Linotype", 9),
                     fg=COLOR_GOLD_DIM, bg=BG_CARD).pack()

    # Sección expandible
    def _seccion(self, parent, idx: int, sec: dict):
        self._abiertos[idx] = False

        wrapper = tk.Frame(parent, bg=BG_MAIN)
        wrapper.pack(fill="x", pady=3)

        # Cabecera (clickable)
        header = tk.Frame(wrapper, bg=BG_CARD,
                          highlightbackground=COLOR_BORDER,
                          highlightthickness=1)
        header.pack(fill="x")

        icono_lbl = tk.Label(header,
                             text=sec["icono"],
                             font=("Palatino Linotype", 18, "bold"),
                             fg=COLOR_GOLD, bg=BG_CARD,
                             width=4)
        icono_lbl.pack(side="left", padx=(8, 0), pady=8)

        titulo_lbl = tk.Label(header,
                              text=sec["titulo"],
                              font=("Palatino Linotype", 13, "bold"),
                              fg=COLOR_GOLD, bg=BG_CARD, anchor="w")
        titulo_lbl.pack(side="left", padx=10, fill="x", expand=True)

        resumen_lbl = tk.Label(header,
                               text=sec["resumen"],
                               font=("Palatino Linotype", 10, "italic"),
                               fg=COLOR_GOLD_DIM, bg=BG_CARD, anchor="w")
        resumen_lbl.pack(side="left", padx=10, fill="x", expand=True)

        arrow = tk.Label(header, text="▸",
                         font=("Palatino Linotype", 14),
                         fg=COLOR_GOLD_DIM, bg=BG_CARD)
        arrow.pack(side="right", padx=14)

        # Contenido (oculto inicialmente)
        body = tk.Frame(wrapper, bg=BG_INPUT,
                        highlightbackground=COLOR_BORDER,
                        highlightthickness=1)

        def toggle(event=None, idx=idx, body=body, arrow=arrow):
            if self._abiertos[idx]:
                body.pack_forget()
                arrow.config(text="▸")
                self._abiertos[idx] = False
            else:
                body.pack(fill="x")
                arrow.config(text="▾")
                self._abiertos[idx] = True

        for widget in (header, icono_lbl, titulo_lbl, resumen_lbl, arrow):
            widget.bind("<Button-1>", toggle)
            widget.configure(cursor="hand2")
        header.bind("<Enter>",
                    lambda e, h=header: h.configure(highlightbackground=COLOR_BORDER_LT))
        header.bind("<Leave>",
                    lambda e, h=header: h.configure(highlightbackground=COLOR_BORDER))

        # Contenido interno
        self._body_content(body, sec)

    def _body_content(self, body: tk.Frame, sec: dict):
        inner = tk.Frame(body, bg=BG_INPUT, padx=16, pady=10)
        inner.pack(fill="x")

        for i, (titulo_paso, desc_paso) in enumerate(sec["pasos"]):
            row = tk.Frame(inner, bg=BG_INPUT)
            row.pack(fill="x", pady=4)

            # Número del paso
            num = tk.Label(row, text=str(i + 1),
                           font=("Palatino Linotype", 13, "bold"),
                           fg="#FFFFFF", bg="#252525",
                           width=2, anchor="center",
                           padx=6, pady=4)
            num.pack(side="left", anchor="n")

            # Contenido del paso
            col = tk.Frame(row, bg=BG_INPUT)
            col.pack(side="left", fill="x", expand=True, padx=(10, 0))
            tk.Label(col, text=titulo_paso,
                     font=("Palatino Linotype", 11, "bold"),
                     fg=COLOR_GOLD, bg=BG_INPUT, anchor="w").pack(anchor="w")
            tk.Label(col, text=desc_paso,
                     font=("Palatino Linotype", 10),
                     fg=COLOR_GOLD_DIM, bg=BG_INPUT,
                     anchor="w", justify="left", wraplength=850).pack(anchor="w")

        # Tip
        if sec.get("tip"):
            tip_frame = tk.Frame(inner, bg="#1E1E1E",
                                 highlightbackground=COLOR_BORDER_LT,
                                 highlightthickness=1)
            tip_frame.pack(fill="x", pady=(8, 0))
            tip_inner = tk.Frame(tip_frame, bg="#1E1E1E", padx=12, pady=8)
            tip_inner.pack(fill="x")
            tk.Label(tip_inner, text="CONSEJO",
                     font=("Palatino Linotype", 8, "bold"),
                     fg=COLOR_BORDER_LT, bg="#1E1E1E").pack(anchor="w")
            tk.Label(tip_inner, text=sec["tip"],
                     font=("Palatino Linotype", 10, "italic"),
                     fg=COLOR_GOLD_DIM, bg="#1E1E1E",
                     anchor="w", justify="left", wraplength=850).pack(anchor="w")
