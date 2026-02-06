# -*- coding: utf-8 -*-
"""
UI.py
---------------------
Pomocné funkce pro aplikaci Cubiq🧊.

Obsahuje nástroje pro:
    • detekci jednokliku a dvojkliku myší v Pygame
"""

import pygame


class MouseClickHandler:
    def __init__(self, double_click_interval=400):
        """
        double_click_interval: maximální interval mezi kliky pro dvojklik (ms)
        """
        self.double_click_interval = double_click_interval
        self.last_click_time = 0

    def check_click(self, event):
        """
        Zavolej při každém eventu pygame.
        Vrací:
            'single' - jedno kliknutí
            'double' - dvojklik
            None - žádná akce
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_click_time <= self.double_click_interval:
                self.last_click_time = 0  # reset po dvojkliku
                return 'double'
            else:
                self.last_click_time = current_time
                return 'single'
        return None

