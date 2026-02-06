# Cubiq

Tento software je chráněn autorskými právy.  
Podrobné informace naleznete v souboru [LICENSE](https://github.com/BeataHa/Cubiq/blob/main/LICENSE.txt).

## Popis
Zdrojový kód a distribuční soubory aplikace **Cubiq**.

**Cubiq** je interaktivní počítačový program, který má sloužit k rozvoji prostorové představivosti.

## Složka `source/`
Obsahuje zdrojový kód aplikace, tedy Python skripty, JSON data a ikonu aplikace.  
Implementace proběhla v programovacím jazyce **Python (verze 3.13)** s využitím knihovny **Pygame (verze 2.6)**, která byla použita pro tvorbu grafického rozhraní aplikace a zpracování uživatelských vstupů.

## Složka `dist/`
Obsahuje distribuční aplikaci, tedy `main.exe` a potřebné JSON soubory.  

- Po stažení složky na počítač lze aplikaci spustit dvojklikem na soubor `main.exe`.  
- Je nutné, aby se ve stejné složce nacházely soubory `data.json` a `resolved_tasks.json`.  
- Program je určen pro operační systém **Windows** a vyžaduje minimální rozlišení obrazovky **1000 × 650 px**.  
- Pro spuštění aplikace není nutná instalace Pythonu ani knihovny Pygame.  
- Velikost aplikace: přibližně **18–19 MB**.
