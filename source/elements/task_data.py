# -*- coding: utf-8 -*-
"""
task_data.py
------------

Správa a rozbalení dat jedné úlohy v aplikaci Cubiq🧊.

Třída TaskData poskytuje:
    • načtení úlohy z JSON souboru podle task_id,
    • 2D reprezentace (půdorys, nárys, bokorys) s Connection2D objekty,
    • 3D řešení s rozbalením indexů na Grid3DPoint a Connection3D,
    • přístup k textu úlohy a sub_id (druhá část task_id),
    • podporu pro různé typy úloh: "2D_to_3D", "3D_to_2D", "tutorial".
"""

import json
from utils.fun_for_making_exe import resource_path, writable_path

from elements.connection import Connection2D, Connection3D
from elements.gridpoint import Grid2DPoint, Grid3DPoint


class TaskData:
    """
    Reprezentuje data jednoho úkolu pro Cubiq.

    Načítá konkrétní úlohu z JSON souboru a rozbalí její řešení
    z indexů na 3D souřadnice.

    Args:
        task_id (str | int): identifikátor úlohy (např. "1.4")
        filepath (str, optional): cesta k JSON souboru s úlohami; default "data.json"

    Attributes:
        data (dict): načtená data úlohy z JSON, obsahuje:
            - text (str): text zadání úlohy
            - pudorys (list[list[int]]): 2D body půdorysu
            - narys (list[list[int]]): 2D body nárysu
            - bokorys (list[list[int]]): 2D body bokorysu
            - data3d (list[list[list[int]]]): 3D spojení jako indexy
            - unpacked_data3d (list[list[tuple[int,int,int]]]): rozbalená 3D řešení

    Properties:
        pudorys -> list[list[int]]: data půdorysu úlohy
        narys -> list[list[int]]: data nárysu úlohy
        bokorys -> list[list[int]]: data bokorysu úlohy
        data3d -> list[list[list[int]]]: původní indexové 3D "řešení"
        unpacked_data3d -> list[list[tuple[int,int,int]]]: rozbalená 3D řešení
        text -> str: text zadání úlohy
        sub_id -> int: druhá část task_id jako celé číslo (např. "1.4" → 4)
    """

    def __init__(self, task_id, filepath="data.json"):
        self.filepath = filepath
        self.task_id = str(task_id)
        self.data = self._load_json()
        self._unpack_data3d()
        self._unpack_2d_connections()

    def _load_json(self) -> dict:
        """Načte JSON a vrátí data pro dané task_id."""
        with open(writable_path(self.filepath), "r", encoding="utf-8") as f:
            all_data = json.load(f)

        self.meta = all_data.get("_meta", {"version": "unknown"})

        if self.task_id not in all_data:
            raise KeyError(f"Úloha '{self.task_id}' nebyla nalezena v {self.filepath}.")

        return all_data[self.task_id]

    def _unpack_data3d(self):
        """Rozbalí 3D "řešení" z JSON, včetně volitelného parametru dashed."""
        unpacked = []
        for sol in self.data.get("data3d", []):
            conn_list = []
            for conn_data in sol:
                a_coords = conn_data[0]
                b_coords = conn_data[1]
                if len(conn_data) == 3 and conn_data[2] == 1:
                    # třetí prvek je dashed
                    dashed = True
                else:
                    dashed = False
                # vytvoření Grid3DPoint
                a = Grid3DPoint(0, 0, *a_coords)
                b = Grid3DPoint(0, 0, *b_coords)
                conn_list.append(Connection3D(a, b, dashed=dashed))

            unpacked.append(conn_list)
        self.data["unpacked_data3d"] = unpacked
        self.data["connections_3d"] = unpacked[0]

    def _unpack_2d_connections(self):
        """
        Převádí pudorys, narys a bokorys na seznam Connection2D objektů.
        JSON formát: [[ [col,row], [col,row], dashed ]]
        """
        for plane in ["pudorys", "narys", "bokorys"]:
            connections_raw = self.data.get(plane, [])
            conn_list = []
            for pair in connections_raw:
                if len(pair) >= 2:
                    (a_col, a_row), (b_col, b_row) = pair[:2]
                    if len(pair) > 2 and pair[2] == 1:
                        dashed = True
                    else:
                        dashed = False
                    a = Grid2DPoint(None, None, a_col, a_row)
                    b = Grid2DPoint(None, None, b_col, b_row)
                    conn_list.append(Connection2D(a, b, dashed=dashed))
            self.data[f"{plane}_connections"] = conn_list

    @property
    def task_type(self):
        """
        vrací: "2D_to_3D" nebo "3D_to_2D" nebo "tutorial"
        """
        return self.data.get("task_type", "")

    @property
    def pudorys_connections(self):
        return self.data.get("pudorys_connections", [])

    @property
    def narys_connections(self):
        return self.data.get("narys_connections", [])

    @property
    def bokorys_connections(self):
        return self.data.get("bokorys_connections", [])

    @property
    def data3d(self):
        return self.data.get("data3d", [])

    @property
    def unpacked_data3d(self):
        return self.data.get("unpacked_data3d", [])

    @property
    def connections_3d(self):
        return self.data.get("connections_3d", [])

    @property
    def text(self):
        return self.data.get("text", "")

    @property
    def sub_id(self):
        """
        Vrací druhou část task_id jako celé číslo.

        Např.:
            task_id = "1.4"  → vrátí 4
            task_id = "1.14" → vrátí 14

        Returns:
            int: druhá část task_id za tečkou
        """
        return int(str(self.task_id).split(".")[1])

