# -*- coding: utf-8 -*-
"""⊕ Datos — Importar CSV o agregar estudiantes manualmente."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY,
    COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO, COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_TINY, CARRERAS, MATERIAS, SEMESTRES,
)
from data.data_store import DataStore
from data.csv_importer import importar, exportar, get_diagnostico
from data.estudiante import Estudiante
from data.sample_generator import generar_datos_muestra
from ui.widgets import GothicCard, GothicButton, color_nivel


class DataEntryScreen:
    def __init__(self, win):
        self.win = win

    def render(self, parent: tk.Frame):
        parent.configure(bg=BG_MAIN)
        ds = DataStore.get()

        tk.Label(parent, text="⊕  DATOS DEL GRIMORIO  ⊕",
                 font=("Palatino Linotype", 20, "bold"),
                 fg=COLOR_GOLD, bg=BG_MAIN).pack(pady=(8, 0))
        tk.Label(parent,
                 text='"Alimenta el oráculo con los datos de las almas"',
                 font=("Palatino Linotype", 11, "italic"),
                 fg=COLOR_GOLD_DIM, bg=BG_MAIN).pack(pady=(0, 8))

        # ── Acciones de importación ────────────────────────────────────
        acc = GothicCard(parent, padx=20, pady=12)
        acc.pack(padx=20, fill="x", pady=(0, 8))
        tk.Label(acc, text="Fuentes de datos:",
                 font=FONT_BODY, fg=COLOR_GOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 6))

        btn_row = tk.Frame(acc, bg=BG_CARD)
        btn_row.pack(fill="x")
        GothicButton(btn_row, text="⤓ Importar CSV (Google Forms o propio)",
                     command=lambda: self._importar(parent, ds)).pack(side="left", padx=(0, 8))
        GothicButton(btn_row, text="★ Cargar datos de muestra",
                     command=lambda: self._cargar_muestra(parent, ds)).pack(side="left", padx=(0, 8))
        GothicButton(btn_row, text="⤑ Exportar CSV actual",
                     command=lambda: self._exportar(ds)).pack(side="left", padx=(0, 8))
        GothicButton(btn_row, text="✕ Limpiar datos",
                     accent=True,
                     command=lambda: self._limpiar(parent, ds)).pack(side="right")

        tk.Label(acc,
                 text="El CSV de Google Forms debe incluir: nombre, carrera, semestre, materia, "
                      "parcial 1-3, tareas, proyecto, horas de estudio, horas de plataformas, "
                      "¿trabaja?, horas de trabajo.\n"
                      "La asistencia se agrega manualmente (columna: porcentaje_asistencia).",
                 font=("Palatino Linotype", 9),
                 fg=COLOR_BORDER, bg=BG_CARD, justify="left", wraplength=700).pack(anchor="w", pady=(6, 0))

        # ── Formulario manual ──────────────────────────────────────────
        form_toggle = GothicButton(parent,
                                   text="+ Agregar estudiante manualmente",
                                   command=lambda: self._toggle_form(form_area))
        form_toggle.pack(pady=4)
        form_area = tk.Frame(parent, bg=BG_MAIN)
        form_area.pack(padx=20, fill="x")
        self._form_visible = False
        self._form_widgets = {}

        # ── Tabla de datos ────────────────────────────────────────────
        self._tabla_frame = tk.Frame(parent, bg=BG_MAIN)
        self._tabla_frame.pack(fill="both", expand=True, padx=20, pady=6)
        self._actualizar_tabla(ds)

    # ── Importar / Exportar ───────────────────────────────────────────
    def _importar(self, parent, ds: DataStore):
        ruta = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            title="Seleccionar CSV")
        if not ruta:
            return
        try:
            nuevos = importar(ruta)
            diag = get_diagnostico()
            if not nuevos:
                self._mostrar_diagnostico(diag, exito=False)
                return
            ds.set_estudiantes(nuevos)
            self._actualizar_tabla(ds)
            self._mostrar_diagnostico(diag, exito=True, n=len(nuevos))
        except Exception as ex:
            messagebox.showerror("Error del oráculo", str(ex))

    def _mostrar_diagnostico(self, diag: dict, exito: bool, n: int = 0):
        mapeadas = diag.get("columnas_mapeadas", {})
        sin_mapear = diag.get("columnas_sin_mapear", [])
        errores = diag.get("errores", [])
        encoding = diag.get("encoding", "?")

        lineas = []
        if exito:
            lineas.append(f"✓ {n} almas cargadas correctamente (encoding: {encoding})\n")
        else:
            lineas.append("✗ No se encontraron filas válidas.\n")

        lineas.append("── Columnas detectadas y mapeadas ──")
        if mapeadas:
            for col, campo in mapeadas.items():
                lineas.append(f"  '{col}'  →  {campo}")
        else:
            lineas.append("  (ninguna)")

        if sin_mapear:
            ignoradas = [c for c in sin_mapear if c.lower() not in ("marca temporal", "timestamp", "")]
            if ignoradas:
                lineas.append("\n── Columnas NO reconocidas (ignoradas) ──")
                for c in ignoradas:
                    lineas.append(f"  '{c}'")
                lineas.append(
                    "\nSi alguna columna importante no fue reconocida, "
                    "comunica el nombre exacto para agregarlo al mapeador."
                )

        if errores:
            lineas.append(f"\n── Filas con error ({len(errores)}) ──")
            for e in errores[:5]:
                lineas.append(f"  {e}")

        titulo = "Importación exitosa" if exito else "Sin datos válidos"
        messagebox.showinfo(titulo, "\n".join(lineas))

    def _cargar_muestra(self, parent, ds: DataStore):
        ds.set_estudiantes(generar_datos_muestra())
        self._actualizar_tabla(ds)

    def _exportar(self, ds: DataStore):
        if not ds.estudiantes:
            messagebox.showwarning("Oráculo", "No hay datos para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Guardar CSV")
        if ruta:
            exportar(ds.estudiantes, ruta)
            messagebox.showinfo("Oráculo", f"Datos exportados a:\n{ruta}")

    def _limpiar(self, parent, ds: DataStore):
        if messagebox.askyesno("Oráculo", "¿Borrar todos los datos cargados?"):
            ds.clear()
            self._actualizar_tabla(ds)

    # ── Formulario manual ──────────────────────────────────────────────
    def _toggle_form(self, frame: tk.Frame):
        if self._form_visible:
            frame.pack_forget()
            self._form_visible = False
        else:
            self._build_form(frame)
            frame.pack(padx=0, fill="x")
            self._form_visible = True

    def _build_form(self, parent: tk.Frame):
        for w in parent.winfo_children():
            w.destroy()
        card = GothicCard(parent, padx=16, pady=12)
        card.pack(fill="x")
        tk.Label(card, text="Nuevo estudiante:", font=("Palatino Linotype", 13, "bold"),
                 fg=COLOR_GOLD, bg=BG_CARD).grid(row=0, column=0, columnspan=4,
                                                  sticky="w", pady=(0, 6))
        campos = [
            ("Nombre", "nombre", "entry"), ("Carrera", "carrera", CARRERAS),
            ("Semestre", "semestre", SEMESTRES), ("Materia", "materia", MATERIAS),
            ("Parcial 1", "parcial1", "num"), ("Parcial 2", "parcial2", "num"),
            ("Parcial 3", "parcial3", "num"), ("Tareas",   "tareas",   "num"),
            ("Proyecto", "proyecto", "num"),
            ("Asistencia %", "porcentaje_asistencia", "num"),
            ("Hrs. Estudio/sem", "horas_estudio", "num"),
            ("Hrs. Plataformas/día", "horas_plataformas", "num"),
            ("Trabaja (1=Sí)", "trabaja", "num"),
            ("Hrs. Trabajo/sem", "horas_trabajo", "num"),
        ]
        self._form_widgets = {}
        for i, (label, key, tipo) in enumerate(campos):
            r, c = divmod(i, 4)
            tk.Label(card, text=label, font=FONT_TINY, fg=COLOR_GOLD_DIM,
                     bg=BG_CARD, anchor="w").grid(row=r*2+1, column=c, sticky="w", padx=4)
            if isinstance(tipo, list):
                var = tk.StringVar(value=str(tipo[0]))
                opt = tk.OptionMenu(card, var, *[str(x) for x in tipo])
                opt.config(bg=BG_SECONDARY, fg=COLOR_GOLD, relief="flat",
                           font=FONT_TINY, bd=0, width=14)
                opt["menu"].config(bg=BG_SECONDARY, fg=COLOR_GOLD, font=FONT_TINY)
                opt.grid(row=r*2+2, column=c, padx=4, pady=2, sticky="ew")
                self._form_widgets[key] = var
            else:
                var = tk.StringVar(value="")
                ent = tk.Entry(card, textvariable=var, font=FONT_SMALL,
                               bg=BG_SECONDARY, fg=COLOR_GOLD,
                               insertbackground=COLOR_GOLD,
                               relief="flat", bd=4, width=16)
                ent.grid(row=r*2+2, column=c, padx=4, pady=2, sticky="ew")
                self._form_widgets[key] = var

        GothicButton(card, text="✦ Agregar alma",
                     command=lambda: self._agregar_manual(DataStore.get())
                     ).grid(row=99, column=0, columnspan=4, pady=8)

    def _agregar_manual(self, ds: DataStore):
        fw = self._form_widgets
        try:
            e = Estudiante(
                id=str(len(ds.estudiantes) + 1),
                nombre=fw["nombre"].get().strip() or "Sin nombre",
                carrera=fw["carrera"].get(),
                semestre=int(fw["semestre"].get()),
                materia=fw["materia"].get(),
                parcial1=float(fw["parcial1"].get()),
                parcial2=float(fw["parcial2"].get()),
                parcial3=float(fw["parcial3"].get()),
                tareas=float(fw["tareas"].get()),
                proyecto=float(fw["proyecto"].get()),
                porcentaje_asistencia=float(fw["porcentaje_asistencia"].get()),
                horas_estudio=float(fw["horas_estudio"].get()),
                horas_plataformas=float(fw["horas_plataformas"].get()),
                trabaja=bool(int(fw["trabaja"].get())),
                horas_trabajo=int(float(fw["horas_trabajo"].get())),
            )
            ds.add(e)
            self._actualizar_tabla(ds)
        except ValueError as ex:
            messagebox.showerror("Error", f"Datos inválidos: {ex}")

    # ── Tabla ──────────────────────────────────────────────────────────
    def _actualizar_tabla(self, ds: DataStore):
        for w in self._tabla_frame.winfo_children():
            w.destroy()

        cols = ("Nombre", "Carrera", "Sem.", "Asistencia%", "Promedio", "Nivel")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Gothic.Treeview",
                        background=BG_CARD, foreground=COLOR_GOLD_DIM,
                        fieldbackground=BG_CARD, rowheight=22,
                        font=("Palatino Linotype", 10))
        style.configure("Gothic.Treeview.Heading",
                        background="#111111", foreground=COLOR_GOLD,
                        font=("Palatino Linotype", 10, "bold"), relief="flat")
        style.map("Gothic.Treeview",
                  background=[("selected", COLOR_PURPLE)],
                  foreground=[("selected", COLOR_GOLD)])

        tree = ttk.Treeview(self._tabla_frame, columns=cols,
                            show="headings", style="Gothic.Treeview", height=14)
        widths = [200, 180, 40, 90, 80, 120]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if w < 150 else "w")

        for e in ds.estudiantes:
            tree.insert("", "end", values=(
                e.nombre, e.carrera, e.semestre,
                f"{e.porcentaje_asistencia:.0f}%",
                f"{e.promedio_final:.2f}",
                e.nivel,
            ))

        sb = tk.Scrollbar(self._tabla_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
