# -*- coding: utf-8 -*-
"""
initiating_length.py
-------------------
Iniciace globálních proměnných pro hru Cubiq🧊

Slouží k definování základních konstant (velikost okna, font apod.),
které jsou sdílené napříč moduly aplikace.
"""

import glob_var
import pygame


def initiate_length(info):
    glob_var.SCREEN_WIDTH = info.current_w * 0.92 if (info.current_w * 0.8 > 1000) else 1000  # min velikost obrazovky
    glob_var.SCREEN_HEIGHT = info.current_h * 0.92 if (info.current_h * 0.8 > 650) else 650

    glob_var.X_OFFSET = glob_var.Y_OFFSET = 45 + glob_var.SCREEN_WIDTH // 200
    glob_var.BTN_HEIGHT = 40 + glob_var.SCREEN_WIDTH // 60

    glob_var.FONT_SIZE = int(25 + glob_var.SCREEN_HEIGHT // 60)

    glob_var.FONT = pygame.font.SysFont(
        glob_var.FONT_NAME,
        int(glob_var.FONT_SIZE)
    )

    glob_var.POP_UP_FONT_SIZE = int(glob_var.FONT_SIZE//1.5)
    glob_var.POP_UP_FONT = pygame.font.SysFont(
        glob_var.FONT_NAME,
        glob_var.POP_UP_FONT_SIZE
    )

    glob_var.LINE_WIDTH = int(3 + glob_var.SCREEN_HEIGHT // 1000)
    glob_var.LINE_GRID_WIDTH = int((2/3)*glob_var.LINE_WIDTH)
    glob_var.LINE_SOLUTION_WIDTH = int((3/2)*glob_var.LINE_WIDTH)
    glob_var.RADIUS = int(glob_var.LINE_WIDTH)


