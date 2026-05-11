#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

   SISTEMA DE ANALISIS ESTADISTICO ACADEMICO
   Hipotesis B — Situación Laboral → Rendimiento


Ejecutar:  python main.py
Instalar:  pip install -r requirements.txt

"""

import sys
from pathlib import Path

# Asegura que el directorio raiz esté en el path
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
