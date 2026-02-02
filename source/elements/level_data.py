# -*- coding: utf-8 -*-
"""
level_data.py
-------------

Správa dat o levelech pro Cubiq🧊.

Třída LevelData umožňuje:
    • načítat úlohy z JSON souboru,
    • seskupovat levely podle kapitol,
    • poskytovat seznam všech levelů nebo seznam kapitol s názvy a levely.

"""

import json
from utils.fun_for_making_exe import resource_path, writable_path


class LevelData:
    """
    Správa dat o levely pro Cubiq.

    Načítá úlohy z JSON a poskytuje seznam kapitol a levelů.
    """

    def __init__(self, data_file: str = "data.json", chapter_titles: list[str] = None):
        """
        Inicializace LevelData.

        Args:
            data_file (str): cesta k JSON souboru s daty o levelech
            chapter_titles (list[str], optional): seznam názvů kapitol;
                                                default ["Tutoriál", "Úsečky", "Rovinné útvary", "Tělesa"]

        Attributes:
            chapters (list[dict]): seznam kapitol, každá jako {"title": ..., "levels": [...]}
        """
        self.data_file = data_file
        self.chapter_titles = chapter_titles or ["Tutoriál", "Úsečky", "Mnohoúhelníky", "Mnohostěny"]
        self.chapters = []  # seznam slovníků: {"title": ..., "levels": [...]}

        self._load_data()

    def update(self):
        self._load_data()

    def _load_data(self):
        """
        Načte JSON a připraví seznam kapitol s levely.

        Postup:
            - seskupí levely podle kapitoly,
            - seřadí je uvnitř kapitoly podle čísla,
            - vytvoří seznam kapitol s názvem a seznamem levelů.
        """
        with open(writable_path(self.data_file), "r", encoding="utf-8") as f:
            data = json.load(f)

        # ignoruj metadata
        if "_meta" in data:
            self.meta = data["_meta"]
            del data["_meta"]
        else:
            self.meta = {"version": "unknown"}

        # dočasně seskupíme levely podle kapitoly (0,1,2,...)
        chapter_levels = {}
        for key in data.keys():
            chapter_index = key.split(".")[0]
            chapter_levels.setdefault(chapter_index, []).append(key)

        # seřadíme levely uvnitř kapitoly
        for chapter_index in chapter_levels:
            chapter_levels[chapter_index].sort(key=lambda s: tuple(int(x) for x in s.split('.')))

        # vytvoříme seznam kapitol s názvem a seznamem levelů
        max_chapters = max(len(chapter_levels), len(self.chapter_titles))
        self.chapters = []
        for i in range(max_chapters):
            title = self.chapter_titles[i] if i < len(self.chapter_titles) else f"Kapitola {i}"
            levels = chapter_levels.get(str(i), [])
            self.chapters.append({
                "title": title,
                "levels": levels
            })

    def get_all_levels(self) -> list[str]:
        """
        Vrátí seznam všech levelů ve formě ['0.1', '0.2', ...].

        Returns:
            list[str]: všechny levely ve všech kapitolách
        """
        levels = []
        for chapter in self.chapters:
            levels.extend(chapter["levels"])
        return levels

    def get_chapters(self) -> list[dict]:
        """
        Vrátí seznam kapitol s názvy a levely.

        Returns:
            list[dict]: každá kapitola jako {"title": ..., "levels": [...]}
        """
        return self.chapters

    def get_version(self) -> str:
        return self.meta.get("version", "unknown")

