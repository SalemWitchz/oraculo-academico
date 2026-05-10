# -*- coding: utf-8 -*-
"""☽ Los Rituales — Recomendaciones automáticas y alertas por riesgo."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE,
    FONT_BODY, FONT_SMALL, FONT_TINY,
)
from data.data_store import DataStore
from stats.modelo_prediccion import _recomendaciones as gen_recs
from ui.widgets import GothicCard, GothicButton, ScrollableFrame, color_nivel, ornamento


class RitualesScreen:
    def __init__(self, win):
        self.win = win
        self._filtro = tk.StringVar(value="Todos")

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()
        est = ds.estudiantes

        tk.Label(parent, text="☽  LOS RITUALES  ☽",
                 font=("Palatino Linotype", 22, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(parent,
                 text='"Acciones concretas para cambiar el destino académico"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 8))

        if not est:
            tk.Label(parent, text="⚠ Sin datos. Ve a ⊕ Datos e importa un archivo.",
                     font=FONT_BODY, fg=COLOR_RIESGO, bg=BG_MAIN).pack(pady=30)
            return

        # Resumen rápido
        counts = ds.count_by_nivel()
        resumen = GothicCard(parent, padx=20, pady=10)
        resumen.pack(padx=20, fill="x", pady=(0, 8))
        row_res = tk.Frame(resumen, bg=BG_CARD)
        row_res.pack(fill="x")

        for nivel, color in [("Alto Rendimiento", COLOR_ALTO),
                              ("Medio",            COLOR_MEDIO),
                              ("En Riesgo",        COLOR_RIESGO)]:
            f = tk.Frame(row_res, bg=BG_CARD, padx=16)
            f.pack(side="left")
            tk.Label(f, text=str(counts[nivel]),
                     font=("Palatino Linotype", 26, "bold"),
                     fg=color, bg=BG_CARD).pack()
            tk.Label(f, text=nivel, font=("Palatino Linotype", 10),
                     fg=COLOR_GOLD_DIM, bg=BG_CARD).pack()

        # Filtro
        fil_frame = GothicCard(parent, padx=16, pady=8)
        fil_frame.pack(padx=20, fill="x", pady=(0, 6))
        tk.Label(fil_frame, text="Filtrar por nivel:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(side="left", padx=(0, 10))
        for opcion in ("Todos", "En Riesgo", "Medio", "Alto Rendimiento"):
            rb = tk.Radiobutton(fil_frame, text=opcion, variable=self._filtro,
                                value=opcion, font=FONT_SMALL,
                                fg=COLOR_GOLD_DIM, bg=BG_CARD,
                                selectcolor="#252525", activebackground=BG_CARD,
                                command=lambda: self._refresh_lista(lista_frame, ds))
            rb.pack(side="left", padx=8)

        GothicButton(fil_frame, text="⤓ Exportar CSV",
                     command=lambda: self._exportar(ds)).pack(side="right")

        # Lista de rituales
        lista_frame = tk.Frame(parent, bg=BG_MAIN)
        lista_frame.pack(fill="both", expand=True, padx=20)
        self._refresh_lista(lista_frame, ds)

    # Helpers
    def _refresh_lista(self, frame: tk.Frame, ds: DataStore):
        for w in frame.winfo_children():
            w.destroy()

        filtro = self._filtro.get()
        scroll = ScrollableFrame(frame)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        estudiantes = ds.estudiantes
        if filtro != "Todos":
            estudiantes = [e for e in estudiantes if e.nivel == filtro]

        if not estudiantes:
            tk.Label(inner, text="Sin estudiantes en este nivel.",
                     font=FONT_BODY, fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=20)
            return

        for e in estudiantes:
            self._tarjeta_estudiante(inner, e)

    def _tarjeta_estudiante(self, parent, e):
        color = color_nivel(e.nivel)
        card = GothicCard(parent, padx=14, pady=10)
        card.pack(fill="x", pady=4)
        card.configure(highlightbackground=color, highlightthickness=1)

        head = tk.Frame(card, bg=BG_CARD)
        head.pack(fill="x")
        tk.Label(head, text=e.nombre,
                 font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).pack(side="left")
        tk.Label(head, text=e.nivel,
                 font=("Palatino Linotype", 11, "bold"),
                 fg=color, bg=BG_CARD).pack(side="right")

        info = tk.Frame(card, bg=BG_CARD)
        info.pack(fill="x", pady=2)
        items = [
            f"Carrera: {e.carrera}",
            f"Sem: {e.semestre}",
            f"Promedio: {e.promedio_final:.2f}",
            f"Asistencia: {e.porcentaje_asistencia:.0f}%",
            f"Estudio: {e.horas_estudio:.0f}h/sem",
            "Trabaja: Sí" if e.trabaja else "Trabaja: No",
        ]
        for item in items:
            tk.Label(info, text=item, font=FONT_TINY,
                     fg=COLOR_GOLD_DIM, bg=BG_CARD).pack(side="left", padx=6)

        recs = gen_recs(e.trabaja, e.horas_estudio, e.nivel)
        for i, r in enumerate(recs, 1):
            icono = "!" if e.nivel == "En Riesgo" else ">"
            tk.Label(card, text=f"  {icono} {i}. {r}",
                     font=("Palatino Linotype", 10),
                     fg=COLOR_GOLD_DIM,
                     bg=BG_CARD, anchor="w", justify="left", wraplength=780
                     ).pack(anchor="w", pady=1)

    def _exportar(self, ds: DataStore):
        from tkinter import filedialog
        import csv
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Exportar Rituales",
        )
        if not ruta:
            return
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Nombre", "Carrera", "Semestre", "Nivel",
                        "Promedio", "Asistencia%", "Ritual 1", "Ritual 2", "Ritual 3"])
            for e in ds.estudiantes:
                recs = gen_recs(e.trabaja, e.horas_estudio, e.nivel)
                recs += [""] * (3 - len(recs))
                w.writerow([e.nombre, e.carrera, e.semestre, e.nivel,
                            round(e.promedio_final, 2), e.porcentaje_asistencia] + recs[:3])
