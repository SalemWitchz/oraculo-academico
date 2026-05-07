# -*- coding: utf-8 -*-
"""Ventana principal con barra lateral de navegación."""
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from config import (
    BG_MAIN, BG_SIDEBAR, COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER,
    COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_NAV, FONT_TINY,
    WIN_W, WIN_H, SIDEBAR_W, MPL_STYLE,
)
from data.data_store import DataStore

# Aplicar tema gótico a matplotlib una sola vez
plt.rcParams.update(MPL_STYLE)


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Oráculo Gótico Académico")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)

        self._current_screen = None
        self._nav_buttons: dict[str, tk.Button] = {}
        self._screens: dict = {}   # inicializado lazy en run()

        self._build_header()
        self._build_layout()
        self._build_sidebar()

        DataStore.get().subscribe(self._refresh_sidebar_count)

    # ── Construcción ──────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#0D0015", height=64)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)

        tk.Label(hdr, text="✦  ORÁCULO GÓTICO ACADÉMICO  ✦",
                 font=("Palatino Linotype", 20, "bold"),
                 fg=COLOR_GOLD, bg="#0D0015").pack(side="left", padx=20, pady=10)
        tk.Label(hdr,
                 text="Sistema de Análisis Estadístico · Hipótesis B · Empleo → Rendimiento",
                 font=("Palatino Linotype", 10, "italic"),
                 fg=COLOR_GOLD_DIM, bg="#0D0015").pack(side="left", padx=4)

    def _build_layout(self):
        self._container = tk.Frame(self.root, bg=BG_MAIN)
        self._container.pack(fill="both", expand=True)
        # Sidebar
        self._sidebar = tk.Frame(self._container, bg=BG_SIDEBAR, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._sidebar.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        # Content
        self._content = tk.Frame(self._container, bg=BG_MAIN)
        self._content.pack(side="left", fill="both", expand=True)

    def _build_sidebar(self):
        tk.Label(self._sidebar, text="NAVEGACIÓN",
                 font=("Palatino Linotype", 9), fg=COLOR_BORDER, bg=BG_SIDEBAR
                 ).pack(pady=(14, 4))

        nav = [
            ("⌂  Inicio",        "home"),
            ("⊕  Datos",         "datos"),
            ("✦  La Profecía",   "profecia"),
            ("✧  El Grimorio",   "grimorio"),
            ("⚖  El Juicio Final","juicio"),
            ("☽  Los Rituales",  "rituales"),
        ]
        for label, key in nav:
            btn = tk.Button(
                self._sidebar, text=label, font=FONT_NAV,
                fg=COLOR_GOLD_DIM, bg=BG_SIDEBAR,
                activeforeground=COLOR_GOLD, activebackground=COLOR_PURPLE,
                relief="flat", anchor="w", padx=14, pady=9, bd=0, cursor="hand2",
                command=lambda k=key: self.show(k),
            )
            btn.pack(fill="x", padx=6, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLOR_PURPLE, fg=COLOR_GOLD))
            btn.bind("<Leave>", lambda e, b=btn, k2=key: b.config(
                bg=COLOR_PURPLE_LT if self._current_screen == k2 else BG_SIDEBAR,
                fg=COLOR_GOLD if self._current_screen == k2 else COLOR_GOLD_DIM))
            self._nav_buttons[key] = btn

        # Contador de almas
        spacer = tk.Frame(self._sidebar, bg=BG_SIDEBAR)
        spacer.pack(fill="both", expand=True)

        bottom = tk.Frame(self._sidebar, bg="#100020",
                          highlightbackground=COLOR_BORDER, highlightthickness=1)
        bottom.pack(fill="x", padx=8, pady=10)
        tk.Label(bottom, text="Almas analizadas",
                 font=("Palatino Linotype", 9), fg=COLOR_BORDER, bg="#100020").pack(pady=(8, 0))
        self._count_lbl = tk.Label(bottom, text="0",
                                   font=("Palatino Linotype", 28, "bold"),
                                   fg=COLOR_GOLD, bg="#100020")
        self._count_lbl.pack(pady=(0, 8))
        self._refresh_sidebar_count()

    def _refresh_sidebar_count(self):
        n = len(DataStore.get().estudiantes)
        self._count_lbl.config(text=str(n))

    # ── Pantallas ─────────────────────────────────────────────────────
    def _lazy_init_screens(self):
        from ui.screens.home_screen      import HomeScreen
        from ui.screens.data_entry       import DataEntryScreen
        from ui.screens.prophecy_screen  import ProphecyScreen
        from ui.screens.grimorio_screen  import GrimorioScreen
        from ui.screens.juicio_screen    import JuicioScreen
        from ui.screens.rituales_screen  import RitualesScreen
        self._screens = {
            "home":     HomeScreen(self),
            "datos":    DataEntryScreen(self),
            "profecia": ProphecyScreen(self),
            "grimorio": GrimorioScreen(self),
            "juicio":   JuicioScreen(self),
            "rituales": RitualesScreen(self),
        }

    def show(self, key: str):
        self._current_screen = key
        # Estilo del botón activo
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.config(bg=COLOR_PURPLE_LT, fg=COLOR_GOLD)
            else:
                btn.config(bg=BG_SIDEBAR, fg=COLOR_GOLD_DIM)
        # Limpiar contenido
        for w in self._content.winfo_children():
            w.destroy()
        # Renderizar pantalla
        self._screens[key].render(self._content)

    def refresh_current(self):
        if self._current_screen:
            self.show(self._current_screen)

    # ── Run ───────────────────────────────────────────────────────────
    def run(self):
        self._lazy_init_screens()
        self.show("home")
        self.root.mainloop()
