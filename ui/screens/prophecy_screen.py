# -*- coding: utf-8 -*-
"""✦ La Profecía — Predicción individual gótica (Hipótesis B)."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY, BG_INPUT,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_GOLD_BRIGHT, COLOR_BORDER, COLOR_BORDER_LT,
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
        self._listbox:       tk.Listbox | None = None
        self._search_var:    tk.StringVar | None = None
        self._filtrados:     list = []
        self._todos:         list = []

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        estudiantes = ds.estudiantes
        self._todos = list(estudiantes)

        # Encabezado
        tk.Label(parent, text="", bg=BG_MAIN).pack(pady=4)
        tk.Label(parent, text="✦  LA PROFECÍA  ✦",
                 font=("Palatino Linotype", 22, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack()
        tk.Label(parent,
                 text='"El oráculo lee tu destino académico en las sombras de los datos"',
                 font=FONT_PROPHECY, fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(2, 10))

        # Selector con búsqueda
        sel_card = GothicCard(parent, padx=20, pady=12)
        sel_card.pack(padx=30, fill="x")

        tk.Label(sel_card, text="Buscar consultante del oráculo:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w")

        # Barra de búsqueda
        search_row = tk.Frame(sel_card, bg=BG_CARD)
        search_row.pack(fill="x", pady=(4, 2))

        self._search_var = tk.StringVar()
        entry = tk.Entry(search_row, textvariable=self._search_var,
                         font=FONT_BODY, bg=BG_INPUT, fg=COLOR_GOLD,
                         insertbackground=COLOR_GOLD,
                         relief="flat", bd=0,
                         highlightbackground=COLOR_BORDER,
                         highlightcolor=COLOR_BORDER_LT,
                         highlightthickness=1)
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))

        tk.Label(search_row, text="nombre o matrícula",
                 font=("Palatino Linotype", 9, "italic"),
                 fg=COLOR_BORDER_LT, bg=BG_CARD).pack(side="left")

        # Lista de resultados
        list_frame = tk.Frame(sel_card, bg=BG_CARD,
                              highlightbackground=COLOR_BORDER,
                              highlightthickness=1)
        list_frame.pack(fill="x", pady=(0, 4))

        self._listbox = tk.Listbox(
            list_frame,
            font=FONT_SMALL,
            bg=BG_SECONDARY, fg=COLOR_GOLD,
            selectbackground=COLOR_PURPLE, selectforeground=COLOR_GOLD,
            activestyle="none",
            height=6, relief="flat", bd=0,
            highlightthickness=0,
        )
        vsb = tk.Scrollbar(list_frame, orient="vertical",
                           command=self._listbox.yview,
                           bg=BG_CARD, troughcolor=BG_SECONDARY)
        self._listbox.configure(yscrollcommand=vsb.set)
        self._listbox.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")

        # Selección al hacer clic
        self._listbox.bind("<<ListboxSelect>>",
                           lambda e: self._al_seleccionar(parent, estudiantes))

        # Filtrado en tiempo real
        self._search_var.trace_add("write",
                                   lambda *_: self._filtrar(parent, estudiantes))

        # Botón de consulta
        GothicButton(sel_card, text="✦  Consultar el Oráculo",
                     accent=True,
                     command=lambda: self._predecir(parent, estudiantes)
                     ).pack(pady=4)

        # Área de resultado
        self._result_frame = tk.Frame(parent, bg=BG_MAIN)
        self._result_frame.pack(fill="both", expand=True, padx=30, pady=8)

        # Poblar lista inicial y mostrar el primero
        self._poblar_lista(estudiantes)
        if estudiantes:
            self._listbox.selection_set(0)
            self._entrenar_y_mostrar(estudiantes[0], parent, estudiantes)

    # Búsqueda y selección
    def _poblar_lista(self, estudiantes):
        self._filtrados = list(estudiantes)
        if self._listbox is None:
            return
        self._listbox.delete(0, "end")
        for e in self._filtrados:
            self._listbox.insert("end", f"  {e.nombre}  [{e.id}]")

    def _filtrar(self, parent, estudiantes):
        if self._listbox is None or self._search_var is None:
            return
        q = self._search_var.get().strip().lower()
        self._filtrados = [
            e for e in estudiantes
            if not q or q in e.nombre.lower() or q in e.id.lower()
        ]
        self._listbox.delete(0, "end")
        for e in self._filtrados:
            self._listbox.insert("end", f"  {e.nombre}  [{e.id}]")
        if self._filtrados:
            self._listbox.selection_set(0)

    def _al_seleccionar(self, parent, estudiantes):
        e = self._get_seleccionado()
        if e:
            self._entrenar_y_mostrar(e, parent, estudiantes)

    def _get_seleccionado(self):
        if self._listbox is None:
            return None
        sel = self._listbox.curselection()
        if not sel or not self._filtrados:
            return None
        idx = sel[0]
        return self._filtrados[idx] if idx < len(self._filtrados) else None

    # Lógica
    def _predecir(self, parent, estudiantes):
        e = self._get_seleccionado()
        if e is None and self._filtrados:
            e = self._filtrados[0]
        if e is None:
            return
        self._entrenar_y_mostrar(e, parent, estudiantes)

    def _entrenar_y_mostrar(self, e, parent, todos):
        if len(todos) >= 3:
            prom_trab = [x.promedio_final for x in todos if     x.trabaja]
            prom_no   = [x.promedio_final for x in todos if not x.trabaja]
            self._oraculo.entrenar(prom_trab, prom_no)
        for w in self._result_frame.winfo_children():
            w.destroy()
        self._mostrar_resultado(e)

    def _mostrar_resultado(self, e):
        frame = self._result_frame
        resultado = self._oraculo.predecir(
            e.trabaja, e.horas_estudio,
            promedio_actual=e.promedio_final,
            seed=hash(e.nombre) % 3,
        )

        # Fila principal
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

        # Profecía + métricas
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
                 fg=COLOR_GOLD_DIM, bg=BG_CARD,
                 wraplength=500, justify="left").pack(anchor="w", pady=6)

        # Datos del estudiante
        metrics_card = GothicCard(right, padx=0, pady=0)
        metrics_card.pack(fill="x", pady=(0, 6))
        tk.Label(metrics_card, text="Lecturas del Grimorio",
                 font=("Palatino Linotype", 11, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD, padx=10, pady=6).pack(anchor="w")
        filas = [
            ("Situación laboral",    "Trabaja" if e.trabaja else "No trabaja"),
            ("Horas trabajo/sem",    f"{e.horas_trabajo} hrs" if e.trabaja else "—"),
            ("Horas de estudio/sem", f"{e.horas_estudio:.0f} hrs"),
            ("Asistencia (%)",       f"{e.porcentaje_asistencia:.1f} %"),
            ("Promedio actual",      f"{e.promedio_final:.2f}"),
            ("Calificación predicha",f"{resultado.calificacion_predicha:.2f}"),
            ("P(Aprobar)",           f"{resultado.prob_aprobar*100:.1f} %"),
            ("P(Reprobar)",          f"{resultado.prob_reprobar*100:.1f} %"),
        ]
        TablaSimple(metrics_card, filas, bg=BG_CARD).pack(fill="x", padx=0)

        # Rituales recomendados
        rit_card = GothicCard(right, padx=16, pady=10)
        rit_card.pack(fill="x")
        tk.Label(rit_card, text="☽  Rituales Recomendados:",
                 font=("Palatino Linotype", 12, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 4))
        for i, rec in enumerate(resultado.recomendaciones, 1):
            tk.Label(rit_card, text=f"  {i}. {rec}",
                     font=FONT_SMALL, fg=COLOR_GOLD_DIM, bg=BG_CARD,
                     anchor="w", justify="left", wraplength=490).pack(anchor="w", pady=1)
