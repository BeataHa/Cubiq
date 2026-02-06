# -*- coding: utf-8 -*-
"""
data_creating_fun.py
-------------------
Pomocné funkce pro aplikaci Cubiq🧊.

Obsahuje nástroje pro:
    • vytvoření, úpravu a mazání úloh v JSON souborech
"""

import json
import os

from utils.fun_for_making_exe import resource_path, writable_path


def create_empty_task(task_id: str, filepath="data.json"):
    """
    Vytvoří novou prázdnou úlohu v JSON souboru se zadaným task_id.

    Args:
        task_id (str): ID úlohy ve formátu "x.x", např. "1.5"
        filepath (str): cesta k JSON souboru
    """
    # Načti existující data, pokud existují
    if os.path.exists(filepath):
        with open(writable_path(filepath), "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    # Nová úloha s minimální strukturou
    all_data[task_id] = {
        "text": "text k úloze",
        "task_type": "3D_to_2D",
        "pudorys": [],
        "narys": [],
        "bokorys": [],
        "data3d": [[]]
    }

    # Ulož zpět do JSON
    with open(writable_path(filepath), "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"Úloha '{task_id}' byla vytvořena v {filepath}.")


def make_data_connections_for_json(connections):
    return [conn.make_data_connection_for_json() for conn in connections]


def save_task_to_json(
        task_id: str,
        text: str,
        task_type: str,
        p_connections: list,
        n_connections: list,
        b_connections: list,
        d_connections: list[list],
        filepath="data.json"
):
    # Načtení existujících dat
    if os.path.exists(filepath):
        with open(writable_path(filepath), "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    # Převod dat
    pudorys = make_data_connections_for_json(p_connections)
    narys = make_data_connections_for_json(n_connections)
    bokorys = make_data_connections_for_json(b_connections)

    # 3D data – list listů
    data3d = [
        make_data_connections_for_json(group)
        for group in d_connections
    ]

    # Uložení úlohy
    all_data[task_id] = {
        "text": text,
        "task_type": task_type,
        "pudorys": pudorys,
        "narys": narys,
        "bokorys": bokorys,
        "data3d": data3d
    }

    # Zápis do souboru
    with open(writable_path(filepath), "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"Úloha '{task_id}' byla uložena do {filepath}.")


def delete_from_json(task_id, filepath="data.json"):
    """
    Smaže všechny data úlohy s daným task_id z JSON souboru.
    task_id musí být string!
    """

    # Načti existující data
    with open(writable_path(filepath), "r", encoding="utf-8") as f:
        data = json.load(f)

    # Zkontroluj, jestli task_id existuje
    if task_id in data:
        del data[task_id]
        print(f"Úloha {task_id} byla smazána.")
    else:
        print(f"Úloha {task_id} nebyla nalezena.")

    # Ulož zpět
    with open(writable_path(filepath), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

