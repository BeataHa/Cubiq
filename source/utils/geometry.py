# -*- coding: utf-8 -*-
"""
geometry.py
----------
Pomocné funkce pro aplikaci Cubiq🧊.

Obsahuje nástroje pro:
    • kreslení čárkované čáry
"""

import math

import pygame


def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=15):
    """
    Nakreslí čárkovanou čáru mezi dvěma body.

    :param surface: pygame.Surface – plocha, na kterou se kreslí
    :param color: tuple – barva čáry (R, G, B)
    :param start_pos: tuple – počáteční bod (x, y)
    :param end_pos: tuple – koncový bod (x, y)
    :param width: int – tloušťka čáry
    :param dash_length: int – maximální délka čárky
    """

    min_space_length = 10
    space_length = max(min_space_length, dash_length // 4, 4 * width)

    # Rozdíl souřadnic
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = math.hypot(dx, dy)

    # Úprava dash_length a space_length aby přerušovaná čára vypadala hezky
    remainder = (distance + space_length) % (dash_length + space_length)
    if remainder > 0:
        count = (distance + space_length) // (dash_length + space_length)
        if count >= 1:
            increase = remainder / (4 * count + count - 1)  # zachováváme přibližný poměr 4:1 (čárky/mezera)
            dash_length += 4 * increase
            space_length += increase
        elif count == 0:
            dash_length = distance

    # Jednotkový vektor směru
    if distance == 0:
        return
    dx /= distance
    dy /= distance

    # Aktuální pozice
    x, y = x1, y1
    drawn = 0

    while drawn < distance:
        # Délka čárky (zkrátí se, pokud by přesáhla konec)
        dash_end = min(dash_length, int(distance - drawn))
        x_end = x + dx * dash_end
        y_end = y + dy * dash_end

        # Nakreslí čárku
        pygame.draw.line(surface, color, (x, y), (x_end, y_end), width)

        # Posune se na konec čárky + mezera
        x += dx * (dash_length + space_length)
        y += dy * (dash_length + space_length)
        drawn += dash_length + space_length
