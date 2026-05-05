# -*- coding: utf-8 -*-
"""Componentes reutilizables con estética gótica."""
import tkinter as tk
from config import (
    BG_MAIN, BG_CARD, BG_SECONDARY, COLOR_GOLD, COLOR_GOLD_DIM,
    COLOR_PURPLE, COLOR_PURPLE_LT, COLOR_BORDER, COLOR_RED,
    COLOR_ALTO, COLOR_MEDIO, COLOR_RIESGO,
    FONT_BODY, FONT_SMALL, FONT_TINY, FONT_SUBHEAD,
)


# ── Utilidad ──────────────────────────────────────────────────────────────────
def color_nivel(nivel: str) -> str:
    return {
        "Alto Rendimiento": COLOR_ALTO,
        "Medio": COLOR_MEDIO,
        "En Riesgo": COLOR_RIESGO,
    }.get(nivel, COLOR_GOLD_DIM)


# ── ScrollableFrame ───────────────────────────────────────────────────────────
class ScrollableFrame(tk.Frame):
    """Frame con scroll vertical gótico."""
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=kw.pop("bg", BG_MAIN), **kw)
        canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                                 bg=BG_SECONDARY, troughcolor=BG_MAIN,
                                 activebackground=COLOR_PURPLE)
        self.inner = tk.Frame(canvas, bg=BG_MAIN)
        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))


# ── GothicCard ────────────────────────────────────────────────────────────────
class GothicCard(tk.Frame):
    """Panel con fondo oscuro y borde morado."""
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG_CARD)
        kw.setdefault("padx", 14)
        kw.setdefault("pady", 12)
        kw.setdefault("relief", "flat")
        super().__init__(parent, **kw)
        self.configure(highlightbackground=COLOR_BORDER,
                       highlightthickness=1,
                       highlightcolor=COLOR_PURPLE_LT)


# ── GothicButton ──────────────────────────────────────────────────────────────
class GothicButton(tk.Button):
    def __init__(self, parent, accent=False, **kw):
        bg_n = COLOR_RED if accent else COLOR_PURPLE
        bg_h = "#A50000" if accent else COLOR_PURPLE_LT
        fg_n = "#F0C070" if accent else COLOR_GOLD
        kw.setdefault("bg", bg_n)
        kw.setdefault("fg", fg_n)
        kw.setdefault("activebackground", bg_h)
        kw.setdefault("activeforeground", COLOR_GOLD)
        kw.setdefault("relief", "flat")
        kw.setdefault("padx", 14)
        kw.setdefault("pady", 7)
        kw.setdefault("cursor", "hand2")
        kw.setdefault("font", FONT_BODY)
        kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self.bind("<Enter>", lambda e: self.config(bg=bg_h))
        self.bind("<Leave>", lambda e: self.config(bg=bg_n))


# ── SectionTitle ──────────────────────────────────────────────────────────────
class SectionTitle(tk.Label):
    def __init__(self, parent, text, **kw):
        kw.setdefault("bg", BG_MAIN)
        kw.setdefault("fg", COLOR_GOLD)
        kw.setdefault("font", FONT_SUBHEAD)
        kw.setdefault("anchor", "w")
        super().__init__(parent, text=f"✦ {text}", **kw)


# ── Separador ─────────────────────────────────────────────────────────────────
class GothicSep(tk.Canvas):
    def __init__(self, parent, width=600, **kw):
        kw.setdefault("height", 12)
        kw.setdefault("bg", BG_MAIN)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, width=width, **kw)
        self.create_line(0, 6, width, 6, fill=COLOR_BORDER, width=1, dash=(4, 4))


# ── StatCard ──────────────────────────────────────────────────────────────────
class StatCard(GothicCard):
    """Tarjeta pequeña con número grande + etiqueta."""
    def __init__(self, parent, label: str, value: str, color: str = COLOR_GOLD, **kw):
        super().__init__(parent, **kw)
        tk.Label(self, text=value, font=("Palatino Linotype", 30, "bold"),
                 fg=color, bg=BG_CARD).pack()
        tk.Label(self, text=label, font=FONT_TINY,
                 fg=COLOR_GOLD_DIM, bg=BG_CARD).pack()


# ── TablaSimple ───────────────────────────────────────────────────────────────
class TablaSimple(tk.Frame):
    """Tabla minimalista (lista de (clave, valor))."""
    def __init__(self, parent, filas: list[tuple[str, str]], **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)
        for i, (k, v) in enumerate(filas):
            bg = BG_CARD if i % 2 == 0 else "#160028"
            tk.Label(self, text=k, font=FONT_SMALL, fg=COLOR_GOLD_DIM, bg=bg,
                     anchor="w", padx=8, pady=4).grid(row=i, column=0, sticky="ew")
            tk.Label(self, text=v, font=FONT_SMALL, fg=COLOR_GOLD, bg=bg,
                     anchor="e", padx=8, pady=4).grid(row=i, column=1, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


# ── Ornamento ─────────────────────────────────────────────────────────────────
def ornamento(parent, bg=BG_MAIN) -> tk.Label:
    return tk.Label(parent, text="✦ ✧ ✦ ✧ ✦", font=("Palatino Linotype", 11),
                    fg=COLOR_BORDER, bg=bg)


# ── Medidor circular (canvas) ─────────────────────────────────────────────────
class Medidor(tk.Canvas):
    """Arco circular que muestra una calificación sobre 10."""
    SIZE = 220

    def __init__(self, parent, **kw):
        kw.setdefault("width", self.SIZE)
        kw.setdefault("height", self.SIZE)
        kw.setdefault("bg", BG_MAIN)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, **kw)
        self._draw(0)

    def set_value(self, value: float):
        self.delete("all")
        self._draw(value)

    def _draw(self, value: float):
        s = self.SIZE
        pad = 18
        # Fondo del círculo
        self.create_oval(pad, pad, s - pad, s - pad,
                         outline=COLOR_BORDER, width=3, fill=BG_CARD)
        # Arco de progreso (270° = full)
        extent = (value / 10.0) * 270
        if extent > 0:
            color = (COLOR_ALTO if value >= 8.5 else
                     COLOR_MEDIO if value >= 7.0 else COLOR_RIESGO)
            self.create_arc(pad + 6, pad + 6, s - pad - 6, s - pad - 6,
                            start=135, extent=extent,
                            outline=color, width=10, style="arc")
        # Número central
        self.create_text(s // 2, s // 2 - 10,
                         text=f"{value:.1f}",
                         fill=COLOR_GOLD, font=("Palatino Linotype", 40, "bold"))
        self.create_text(s // 2, s // 2 + 26,
                         text="/10", fill=COLOR_GOLD_DIM,
                         font=("Palatino Linotype", 13))


# ── Barra de probabilidad ─────────────────────────────────────────────────────
class BarraProbabilidad(tk.Canvas):
    H = 28

    def __init__(self, parent, label_ap="Aprobar", label_rep="Reprobar", **kw):
        kw.setdefault("height", self.H + 24)
        kw.setdefault("bg", BG_MAIN)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, **kw)
        self._la = label_ap
        self._lr = label_rep
        self.set_value(0.5)

    def set_value(self, prob_ap: float):
        self.delete("all")
        w = self.winfo_reqwidth() or 400
        pct_ap = max(0.0, min(1.0, prob_ap))
        pct_re = 1 - pct_ap
        w_ap = int(w * pct_ap)
        w_re = w - w_ap
        # Barra aprobar
        if w_ap > 0:
            self.create_rectangle(0, 0, w_ap, self.H, fill=COLOR_ALTO, outline="")
        # Barra reprobar
        if w_re > 0:
            self.create_rectangle(w_ap, 0, w, self.H, fill=COLOR_RIESGO, outline="")
        # Etiquetas
        self.create_text(4, self.H + 12, anchor="w",
                         text=f"{self._la}: {pct_ap*100:.1f}%",
                         fill=COLOR_ALTO, font=FONT_TINY)
        self.create_text(w - 4, self.H + 12, anchor="e",
                         text=f"{self._lr}: {pct_re*100:.1f}%",
                         fill=COLOR_RIESGO, font=FONT_TINY)
