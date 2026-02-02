# -*- coding: utf-8 -*-
"""
global_variables.py
-------------------
Globální proměnné pro hru Cubiq🧊

Slouží k uchování základních konstant (velikost okna, font apod.),
které jsou sdílené napříč moduly aplikace.
"""

import pygame

pygame.init()

# Velikost hlavního okna (1000 * 650)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# Výchozí font písma, vhodné pro českou diakritiku
FONT_NAME = "Gabriola"
FONT_SIZE = 35

FONT = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

POP_UP_FONT_SIZE = int(FONT_SIZE//2)
POP_UP_FONT = pygame.font.SysFont(FONT_NAME, POP_UP_FONT_SIZE)

# výchozí x a y odsazení především tlačítek od okraje obrazovky
X_OFFSET = 50
Y_OFFSET = 50

# výška tlačítek
BTN_HEIGHT = 60

# šířka čar
LINE_GRID_WIDTH = 2
LINE_WIDTH = 3
LINE_SOLUTION_WIDTH = 4
RADIUS = LINE_WIDTH

# barvy
GREEN = (0, 255, 120)
BLUE = (0, 170, 255)
RED = (255, 60, 60)
