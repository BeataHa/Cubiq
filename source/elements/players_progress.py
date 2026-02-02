# -*- coding: utf-8 -*-
"""
player_progress.py
-----------------

Správa pokroku hráčů pro hru Cubiq🧊.

Třída PlayerProgress umožňuje:
    • načítat pokrok hráčů z JSON souboru,
    • ukládat jaké levely hráč dokončil,
    • přidávat nové hráče,
    • získat informace o konkrétním hráči,
    • aktualizovat dokončené levely hráče.
"""

import json
import os

from utils.fun_for_making_exe import writable_path, resource_path


class PlayerProgress:
    """
    Správa pokroku hráčů pro Cubiq.

    Umožňuje načítat a ukládat dokončené levely každého hráče
    a spravovat seznam hráčů.
    """

    def __init__(self, file_path: str = "resolved_tasks.json"):
        """
        Inicializuje správu pokroku.

        Args:
            file_path (str): cesta k JSON souboru s pokrokem hráčů.
        """
        self.file_path = file_path
        self.players: dict[str, dict] = {}
        self.load_progress()

    def load_progress(self):
        """
        Načte pokrok všech hráčů z JSON souboru.
        Pokud soubor neexistuje, vytvoří prázdný slovník.
        """
        if os.path.exists(self.file_path):
            with open(writable_path(self.file_path), "r", encoding="utf-8") as f:
                self.players = json.load(f)
        else:
            self.players = {}

    def save_progress(self):
        """
        Uloží pokrok všech hráčů do JSON souboru.
        """
        with open(writable_path(self.file_path), "w", encoding="utf-8") as f:
            json.dump(self.players, f, indent=4, ensure_ascii=False)

    def add_player(self, name: str):
        """
        Přidá hráče, pokud ještě neexistuje.

        Args:
            name (str): jméno hráče
        """
        if name not in self.players:
            self.players[name] = {"completed_levels": []}

    def get_player(self, name: str) -> dict:
        """
        Vrátí data konkrétního hráče.

        Args:
            name (str): jméno hráče

        Returns:
            dict: informace o hráči, např. {"completed_levels": [...]}
        """
        if name not in self.players:
            self.add_player(name)
        return self.players[name]

    def update_player_level(self, name: str, level: str):
        """
        Označí daný level jako dokončený pro konkrétního hráče.

        Args:
            name (str): jméno hráče
            level (str): označení levelu
        """
        if name not in self.players:
            self.add_player(name)

        if "completed_levels" not in self.players[name]:
            self.players[name]["completed_levels"] = []

        level_str = str(level)
        if level_str not in self.players[name]["completed_levels"]:
            self.players[name]["completed_levels"].append(level_str)
