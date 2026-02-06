# -*- coding: utf-8 -*-
"""
fun_for_making_exe.py
---------------------
Pomocné funkce pro aplikaci Cubiq🧊.

Obsahuje nástroje pro:
    • získání cest k souborům při běhu v Pythonu i z .exe
    • určení cesty pro zápis souborů
"""

import os, sys

def resource_path(relative_path):
    """Najde soubory správně, i když je kód zabalen do .exe."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

import os, sys

def writable_path(relative_path):
    """Vrací cestu, kam lze zapisovat soubory."""
    if hasattr(sys, "_MEIPASS"):
        # Pokud běží z PyInstaller .exe, použij složku se spuštěným exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Pokud běží v PyCharm / Pythonu
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


