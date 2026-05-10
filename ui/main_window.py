# -*- coding: utf-8 -*-
"""Ventana principal con barra lateral de navegación — tema monocromático."""
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from config import (
    BG_MAIN, BG_SIDEBAR, COLOR_GOLD, COLOR_GOLD_DIM, COLOR_BORDER, COLOR_BORDER_LT,
    COLOR_PURPLE, COLOR_PURPLE_LT,
    FONT_BODY, FONT_SMALL, FONT_NAV, FONT_TINY,
    WIN_W, WIN_H, SIDEBAR_W, MPL_STYLE,
)
from data.data_store import DataStore

plt.rcParams.update(MPL_STYLE)

_HDR_BG      = "#050505"
_SIDEBAR_BTM = "#111111"
_ACTIVE_BG   = "#252525"


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Estadístico Académico")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)

        self._current_screen = None
        self._nav_buttons: dict[str, tk.Button] = {}
        self._screens: dict = {}

        self._build_header()
        self._build_layout()
        self._build_sidebar()

        DataStore.get().subscribe(self._refresh_sidebar_count)

    # Construcción
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=_HDR_BG, height=58)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)

        # Barra izquierda blanca (acento visual)
        tk.Frame(hdr, bg=COLOR_GOLD, width=4).pack(side="left", fill="y")

        tk.Label(hdr, text="SISTEMA DE ANÁLISIS ESTADÍSTICO ACADÉMICO",
                 font=("Palatino Linotype", 16, "bold"),
                 fg="#FFFFFF", bg=_HDR_BG).pack(side="left", padx=16, pady=10)

        tk.Label(hdr,
                 text="Hipótesis B · Situación Laboral → Rendimiento Académico · α = 0.05",
                 font=("Palatino Linotype", 10, "italic"),
                 fg=COLOR_GOLD_DIM, bg=_HDR_BG).pack(side="left", padx=4)

        # Indicador de versión
        tk.Label(hdr, text="v2.0", font=("Palatino Linotype", 9),
                 fg=COLOR_BORDER_LT, bg=_HDR_BG).pack(side="right", padx=14)

    def _build_layout(self):
        self._container = tk.Frame(self.root, bg=BG_MAIN)
        self._container.pack(fill="both", expand=True)
        self._sidebar = tk.Frame(self._container, bg=BG_SIDEBAR, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._sidebar.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        self._content = tk.Frame(self._container, bg=BG_MAIN)
        self._content.pack(side="left", fill="both", expand=True)

    def _build_sidebar(self):
        # Encabezado del sidebar
        tk.Label(self._sidebar, text="NAVEGACIÓN",
                 font=("Palatino Linotype", 8, "bold"),
                 fg=COLOR_BORDER_LT, bg=BG_SIDEBAR,
                 ).pack(pady=(16, 6))

        nav = [
            ("⌂  Inicio",              "home"),
            ("⊕  Datos",               "datos"),
            ("✦  La Profecía",         "profecia"),
            ("✧  El Grimorio",         "grimorio"),
            ("∑  Grimorio Avanzado",   "grimorio_avanzado"),
            ("⚖  El Juicio Final",     "juicio"),
            ("☽  Los Rituales",        "rituales"),
            ("?  Guía de Uso",         "guia"),
            ("☆  Créditos",            "creditos"),
        ]
        for label, key in nav:
            btn = tk.Button(
                self._sidebar, text=label, font=FONT_NAV,
                fg=COLOR_GOLD_DIM, bg=BG_SIDEBAR,
                activeforeground=COLOR_GOLD, activebackground=_ACTIVE_BG,
                relief="flat", anchor="w", padx=14, pady=9, bd=0, cursor="hand2",
                command=lambda k=key: self.show(k),
            )
            btn.pack(fill="x", padx=6, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=_ACTIVE_BG, fg=COLOR_GOLD))
            btn.bind("<Leave>", lambda e, b=btn, k2=key: b.config(
                bg=_ACTIVE_BG if self._current_screen == k2 else BG_SIDEBAR,
                fg=COLOR_GOLD if self._current_screen == k2 else COLOR_GOLD_DIM))
            self._nav_buttons[key] = btn

        # Separador
        tk.Frame(self._sidebar, bg=COLOR_BORDER, height=1).pack(
            fill="x", padx=10, pady=(10, 0))

        # Panel contador inferior
        spacer = tk.Frame(self._sidebar, bg=BG_SIDEBAR)
        spacer.pack(fill="both", expand=True)

        bottom = tk.Frame(self._sidebar, bg=_SIDEBAR_BTM,
                          highlightbackground=COLOR_BORDER, highlightthickness=1)
        bottom.pack(fill="x", padx=8, pady=10)
        tk.Label(bottom, text="ALMAS REGISTRADAS",
                 font=("Palatino Linotype", 8, "bold"),
                 fg=COLOR_BORDER_LT, bg=_SIDEBAR_BTM).pack(pady=(10, 0))
        self._count_lbl = tk.Label(bottom, text="0",
                                   font=("Palatino Linotype", 34, "bold"),
                                   fg=COLOR_GOLD, bg=_SIDEBAR_BTM)
        self._count_lbl.pack(pady=(0, 10))
        self._refresh_sidebar_count()

    def _refresh_sidebar_count(self):
        n = len(DataStore.get().estudiantes)
        self._count_lbl.config(text=str(n))

    # Pantallas
    def _lazy_init_screens(self):
        from ui.screens.home_screen              import HomeScreen
        from ui.screens.data_entry               import DataEntryScreen
        from ui.screens.prophecy_screen          import ProphecyScreen
        from ui.screens.grimorio_screen          import GrimorioScreen
        from ui.screens.grimorio_avanzado_screen import GrimorioAvanzadoScreen
        from ui.screens.juicio_screen            import JuicioScreen
        from ui.screens.rituales_screen          import RitualesScreen
        from ui.screens.guia_screen              import GuiaScreen
        from ui.screens.creditos_screen          import CreditosScreen
        self._screens = {
            "home":              HomeScreen(self),
            "datos":             DataEntryScreen(self),
            "profecia":          ProphecyScreen(self),
            "grimorio":          GrimorioScreen(self),
            "grimorio_avanzado": GrimorioAvanzadoScreen(self),
            "juicio":            JuicioScreen(self),
            "rituales":          RitualesScreen(self),
            "guia":              GuiaScreen(self),
            "creditos":          CreditosScreen(self),
        }

    def show(self, key: str):
        self._current_screen = key
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.config(bg=_ACTIVE_BG, fg=COLOR_GOLD)
            else:
                btn.config(bg=BG_SIDEBAR, fg=COLOR_GOLD_DIM)
        for w in self._content.winfo_children():
            w.destroy()
        self._screens[key].render(self._content)

    def refresh_current(self):
        if self._current_screen:
            self.show(self._current_screen)

    # Run
    def run(self):
        self._lazy_init_screens()
        self.show("home")
        self.root.mainloop()
