# Cubiq
Zdrojový kód a distribuční soubory aplikace Cubiq.

Cubiq je interaktivní počítačový program, který má sloužit k rozvoji prostorové představivosti.

Složka source/ obsahuje zdrojový kód aplikace, tedy Python skripty, JSON data a ikonu aplikace.
  Implementace proběhla v programovacím jazyce Python  (verze 3.13) s využitím knihovny Pygame  (verze 2.6), která byla použita pro tvorbu grafického rozhraní aplikace a zpracování uživatelských vstupů.

Složka dis/ obsahuje distribuční aplíček aplikace, tedy main.exe a potřebné JSON soubory.
  Po stažení složky na počítač lze aplikaci spustit dvojklikem na soubor main.exe. Je přitom nutné, aby se ve stejné složce nacházely i soubory data.json a resolved_tasks.json.
  Program je určen pro operační systém Windows a vyžaduje minimální rozlišení obrazovky 1000 × 650 pixelů. Pro spuštění aplikace není nutná instalace Pythonu ani knihovny Pygame. Velikost aplikace se pohybuje mezi 18–19 MB.
