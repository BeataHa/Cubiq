# Cubiq🧊 – Zdrojové kódy

Zdrojový kód aplikace Cubiq🧊, obsahuje Python skripty, JSON data a ikonu aplikace.

**Technologie:**
- Python 3.13
- Pygame 2.6 (grafické rozhraní a zpracování uživatelských vstupů)

## Struktura složky `source/`

- **elements/** – objekty, které se používají napříč aplikací: tlačítka, popup okna, body mřížky, spojení, vstupní pole a správu úrovní.
- **grids/** – funkce pro vykreslování a práci s 2D a 3D mřížkami.
- **screens/** – jednotlivé obrazovky aplikace (start, úlohy, editace, seznam úrovní).
- **utils/** – různé podpůrné moduly: matematika, geometrie, pomocné funkce pro UI a vytváření spustitelného souboru.
- **data.json** – obsahuje všechna zadání a řešení úloh.
- **glob_var.py** – globální nastavení, velikosti, barvy a konstanty.
- **icon.ico** – ikona aplikace
- **main.py** – vstupní bod aplikace.
- **resolved_tasks.json** – ukládá dokončené a vyřešené úlohy uživatele.

## Hlavní principy

- 2D a 3D gridy s interaktivními body a spojeními  
- Data uložená v JSON souborech
- Vykreslení a ovládání přes Pygame  

## Spuštění

```bash
python main.py
