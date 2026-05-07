#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════╗
║   SISTEMA DE ANÁLISIS ESTADÍSTICO ACADÉMICO         ║
║   Hipótesis B — Situación Laboral → Rendimiento     ║
║   Probabilidad y Estadística                        ║
╚══════════════════════════════════════════════════════╝
Ejecutar:  python main.py
Instalar:  pip install -r requirements.txt
"""
import sys
from pathlib import Path

# Asegura que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from data.data_store import DataStore
from data.sample_generator import generar_datos_muestra
from ui.main_window import MainWindow


def main():
    # Cargar datos de muestra al inicio
    store = DataStore.get()
    store.set_estudiantes(generar_datos_muestra())

    # Lanzar interfaz
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
