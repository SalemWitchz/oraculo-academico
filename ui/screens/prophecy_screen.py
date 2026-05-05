# -*- coding: utf-8 -*-
"""✦ La Profecía — Predicción individual gótica."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_GOLD_BRIGHT, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_TINY, FONT_PROPHECY,
)
from data.data_store import DataStore
from stats.modelo_prediccion import Oraculo
from ui.widgets import (GothicCard, GothicButton, ornamento,
                         Medidor, BarraProbabilidad, color_nivel, TablaSimple)


class ProphecyScreen:
    def __init__(self, win):
        self.win = win
        self._oraculo = Oraculo()
        self._result_frame: tk.Frame | None = None

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        estudiantes = ds.estudiantes

        # ── Encabezado ────────────────────────────────────────────────
        tk.Label(parent, text="", bg=BG_MAIN).pack(pady=4)
        tk.Label(parent, text="✦  LA PROFECÍA  ✦",
                 font=("Palatino Linotype", 22, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack()
        tk.Label(parent,
                 text='"El oráculo lee tu destino académico en las sombras de los datos"',
                 font=FONT_PROPHECY, fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(2, 10))

        # ── Selector de estudiante ─────────────────────────────────────
        sel_card = GothicCard(parent, padx=20, pady=12)
        sel_card.pack(padx=30, fill="x")

        tk.Label(sel_card, text="Selecciona al consultante del oráculo:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")

        nombres = [str(e) for e in estudiantes] if estudiantes else ["(sin datos)"]
        self._var = tk.StringVar(value=nombres[0])
        opt = tk.OptionMenu(sel_card, self._var, *nombres)
        opt.config(font=FONT_BODY, bg=BG_SECONDARY, fg=COLOR_GOLD,
                   activebackground=COLOR_PURPLE, activeforeground=COLOR_GOLD,
                   relief="flat", bd=0, highlightthickness=0)
        opt["menu"].config(bg=BG_SECONDARY, fg=COLOR_GOLD, font=FONT_SMALL,
                           activebackground=COLOR_PURPLE)
        opt.pack(fill="x", pady=6)

        GothicButton(sel_card, text="✦  Consultar el Oráculo",
                     accent=True,
                     command=lambda: self._predecir(parent, estudiantes)
                     ).pack(pady=4)

        # Área de resultado
        self._result_frame = tk.Frame(parent, bg=BG_MAIN)
        self._result_frame.pack(fill="both", expand=True, padx=30, pady=8)

        # Si hay datos, mostrar el primero automáticamente
        if estudiantes:
            self._entrenar_y_mostrar(estudiantes[0], parent, estudiantes)

    # ── Lógica ────────────────────────────────────────────────────────
    def _predecir(self, parent, estudiantes):
        nombre_sel = self._var.get()
        e = next((x for x in estudiantes if str(x) == nombre_sel), None)
        if e is None:
            return
        self._entrenar_y_mostrar(e, parent, estudiantes)

    def _entrenar_y_mostrar(self, e, parent, todos):
        if len(todos) >= 3:
            self._oraculo.entrenar(
                [x.porcentaje_asistencia for x in todos],
                [x.promedio_final for x in todos],
            )
        for w in self._result_frame.winfo_children():
            w.destroy()
        self._mostrar_resultado(e)

    def _mostrar_resultado(self, e):
        frame = self._result_frame
        resultado = self._oraculo.predecir(
            e.porcentaje_asistencia, e.horas_estudio, e.trabaja,
            seed=hash(e.nombre) % 3,
        )

        # ── Fila principal ────────────────────────────────────────────
        main_row = tk.Frame(frame, bg=BG_MAIN)
        main_row.pack(fill="x")

        # Medidor
        left = GothicCard(main_row, padx=16, pady=14)
        left.pack(side="left", fill="y", padx=(0, 8))
        tk.Label(left, text=e.nombre, font=("Palatino Linotype", 14, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack()
        tk.Label(left, text=f"{e.carrera} · Sem. {e.semestre}",
                 font=FONT_SMALL, fg=COLOR_GOLD_DIM, bg=BG_CARD).pack(pady=(0, 6))

        medidor = Medidor(left)
        medidor.pack()
        medidor.set_value(resultado.calificacion_predicha)

        color_niv = color_nivel(resultado.nivel)
        tk.Label(left, text=resultado.nivel,
                 font=("Palatino Linotype", 12, "bold"),
                 fg=color_niv, bg=BG_CARD).pack(pady=4)

        # Probabilidad
        tk.Label(left, text="Probabilidad de destino:",
                 font=FONT_TINY, fg=COLOR_GOLD_DIM, bg=BG_CARD).pack()
        barra = BarraProbabilidad(left, width=200)
        barra.pack(pady=4)
        frame.update_idletasks()
        barra.set_value(resultado.prob_aprobar)

        # ── Profecía + métricas ────────────────────────────────────────
        right = tk.Frame(main_row, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True)

        # Texto de profecía
        prof_card = GothicCard(right, padx=16, pady=12)
        prof_card.pack(fill="x", pady=(0, 6))
        tk.Label(prof_card, text="⚝  La Profecía Habla:",
                 font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")
        tk.Label(prof_card,
                 text=f'"{resultado.profecia}"',
                 font=FONT_PROPHECY,
                 fg="#A09060", bg=BG_CARD,
                 wraplength=500, justify="left").pack(anchor="w", pady=6)

        # Datos del estudiante
        metrics_card = GothicCard(right, padx=0, pady=0)
        metrics_card.pack(fill="x", pady=(0, 6))
        tk.Label(metrics_card, text="Lecturas del Grimorio",
                 font=("Palatino Linotype", 11, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, padx=10, pady=6).pack(anchor="w")
        filas = [
            ("Asistencia (%)",       f"{e.porcentaje_asistencia:.1f} %"),
            ("Horas de estudio/sem", f"{e.horas_estudio:.0f} hrs"),
            ("Promedio actual",      f"{e.promedio_final:.2f}"),
            ("Calificación predicha",f"{resultado.calificacion_predicha:.2f}"),
            ("P(Aprobar)",           f"{resultado.prob_aprobar*100:.1f} %"),
            ("P(Reprobar)",          f"{resultado.prob_reprobar*100:.1f} %"),
            ("Trabaja",              "Sí" if e.trabaja else "No"),
        ]
        TablaSimple(metrics_card, filas, bg=BG_CARD).pack(fill="x", padx=0)

        # ── Rituales recomendados ──────────────────────────────────────
        rit_card = GothicCard(right, padx=16, pady=10)
        rit_card.pack(fill="x")
        tk.Label(rit_card, text="☽  Rituales Recomendados:",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 4))
        for i, rec in enumerate(resultado.recomendaciones, 1):
            tk.Label(rit_card, text=f"  {i}. {rec}",
                     font=FONT_SMALL, fg="#A09060", bg=BG_CARD,
                     anchor="w", justify="left", wraplength=490).pack(anchor="w", pady=1)
