# -*- coding: utf-8 -*-
"""
grid_2d.py
-----------

Nástroje pro vykreslování 2D gridů v editoru a hře Cubiq🧊.

Obsahuje funkce, které:
    • počítají velikosti čtverců a pozice gridů na obrazovce,
    • generují 3×3 body pro půdorys, nárys a bokorys,
    • vykreslují mřížku s body a spojovacími čarami,
    • přidávají popisky pod jednotlivé 2D gridy,
    • vykreslují úsečky podle seznamu Connection2D,
    • podporují interaktivní 2D grid pro editor úloh.
"""


import math

import glob_var
import pygame
from elements.connection import Connection2D
from elements.gridpoint import Grid2DPoint
from utils.geometry import draw_dashed_line


def count_square_length() -> int:
    """
    Vrátí velikost čtverce pro 2D grid podle velikosti obrazovky. (1/5 obrazovky dole vyhrazena na text k úloze)

    Grid je určený pro levou polovinu obrazovky.
    """
    if (glob_var.SCREEN_WIDTH // 14) > (((4 * glob_var.SCREEN_HEIGHT) // 5) // 9):
        return ((4 * glob_var.SCREEN_HEIGHT) // 5) // 9
    return glob_var.SCREEN_WIDTH // 14


def find_left_upper_corners(square_length: int, centre_x: int = None, centre_y: int = None):
    """
    Vypočítá levé horní rohy pro půdorys, nárys a bokorys.
    (1/5 obrazovky dole vyhrazena na text k úloze)

    Args:
        square_length (int): délka jedné strany čtverce
        centre_x (int, optional): středová X souřadnice gridu; default je 1/4 šířky obrazovky
        centre_y (int, optional): středová Y souřadnice gridu; default je polovina 1/5 výšky obrazovky

    Returns:
        tuple: (p, n, b) – souřadnice levých horních rohů (půdorysu, nárysu, bokorysu)
    """
    if centre_x is None:
        # původně
        centre_x = glob_var.SCREEN_WIDTH // 4
        # centre_x = glob_var.SCREEN_WIDTH // 5
    if centre_y is None:
        centre_y = int(((4 * glob_var.SCREEN_HEIGHT) / 5) // 2)  # (1/5 obrazovky dole vyhrazena na text k úloze)

    # původně
    # p = [centre_x - int(2.5 * square_length), centre_y - int(3.5 * square_length)]
    # n = [centre_x - int(2.5 * square_length), centre_y + int(0.5 * square_length)]
    # b = [centre_x + int(0.5 * square_length), centre_y + int(0.5 * square_length)]

    p = [centre_x + int(0.5 * square_length), centre_y + int(0.5 * square_length)]
    n = [centre_x + int(0.5 * square_length), centre_y - int(3.5 * square_length)]
    b = [centre_x - int(2.5 * square_length), centre_y - int(3.5 * square_length)]

    return p, n, b


def create_2d_points(start: list[int], square_length: int) -> list[Grid2DPoint]:
    """
    Vytvoří 3×3 body gridu pro 2D mřížku.

    Args:
        start (list[int]): levý horní roh gridu [x, y]
        square_length (int): velikost jedné strany čtverce

    Returns:
        list[Grid2DPoint]: seznam všech bodů gridu
    """
    points = []
    for row in range(3):
        for col in range(3):
            x = start[0] + col * square_length
            y = start[1] + row * square_length
            points.append(Grid2DPoint(x, y, col, row))
    return points


def create_all_2d_points():
    """
        Vytvoří všechny 3 3×3 body gridu pro 2D mřížku.
        Returns:
        3x list[Grid2DPoint]: seznam všech bodů gridu půdorysu, nárysu a bokorysu
    """

    l_square_length = count_square_length()
    p, n, b = find_left_upper_corners(l_square_length)

    p_points = create_2d_points(p, l_square_length)
    n_points = create_2d_points(n, l_square_length)
    b_points = create_2d_points(b, l_square_length)

    return p_points, n_points, b_points


def draw_2d_grid(screen: pygame.Surface, points: list[Grid2DPoint], mouse_pos=None, gridpoints_enabled=True):
    """
    Vykreslí 3x3 grid s body a čarami.

    Args:
        screen: pygame surface, kam se kreslí
        points (list): seznam bodů mřížky (GridPoint)
        mouse_pos (tuple[int, int]): aktuální pozice kurzoru myši
        gridpoints_enabled (bool): zapínání/vypínání interaktivnosti
    """
    rows = cols = 3
    line_color = (50, 50, 50)
    line_width = int(glob_var.LINE_GRID_WIDTH)

    def index(c, r):
        return c + r * cols

    for point in points:
        point.enable() if gridpoints_enabled else point.disable()
        c, r = point.col, point.row

        if c < cols - 1:
            right = points[index(c + 1, r)]
            pygame.draw.line(screen, line_color, (point.x, point.y), (right.x, right.y), line_width)

        if r < rows - 1:
            below = points[index(c, r + 1)]
            pygame.draw.line(screen, line_color, (point.x, point.y), (below.x, below.y), line_width)

    for point in points:
        point.draw(screen, mouse_pos)


def draw_grid_label(screen: pygame.Surface, start: list[int], square_length: int,
                    label: str, offset_y: int = None, color=(100, 100, 100)):
    """
    Vykreslí textový popisek pod 2D gridem.

    Args:
        screen: pygame surface
        start: levý horní roh gridu
        square_length: velikost čtverce
        label: text popisku
        offset_y: posun od gridu dolů
        color: barva textu
    """
    font = glob_var.FONT
    if offset_y is None:
        offset_y = square_length // 2
    text_surface = font.render(label, True, color)
    x = start[0] + 1 * square_length - text_surface.get_width() // 2
    y = start[1] + 2 * square_length + offset_y
    screen.blit(text_surface, (x, y))


def draw_lines_from_connections(screen: pygame.Surface, connections: list[Connection2D],
                                connections_color=(255, 255, 255), connections_width=glob_var.LINE_WIDTH):
    """
    Vykreslí úsečky mezi body gridu podle seznamu Connection2D.
    Pokud jsou oba body totožné, vykreslí se bod.
    """
    radius = int(connections_width * 2)
    line_width = int(connections_width)
    for conn in connections:
        a = conn.point_a
        b = conn.point_b
        x1, y1 = a.x, a.y
        x2, y2 = b.x, b.y

        if (x1, y1) == (x2, y2):
            pygame.draw.circle(screen, connections_color, (x1, y1), radius)
        else:
            if getattr(conn, "dashed", False):
                # čárkovaná čára
                draw_dashed_line(screen, connections_color, (x1, y1), (x2, y2), width=int(line_width//2))
            else:
                # plná čára
                pygame.draw.line(screen, connections_color, (x1, y1), (x2, y2), line_width)


def draw_task(screen: pygame.Surface, position: list[int], square_length: int,
              label: str, connections: list[Connection2D], points: list[Grid2DPoint], mouse_pos=None,
              gridpoints_enabled=True, connections_color=(255, 255, 255), connections_width=glob_var.LINE_WIDTH):
    """
    Vykreslí kompletní 2D úlohu: grid, popisek a úsečky(/body).

    Args:
        screen: pygame surface
        position: levý horní roh gridu
        square_length: velikost čtverce
        label: název gridu (např. "Půdorys")
        connections: seznam dvojic bodů, které určují úsečky
        points (list): seznam bodů mřížky (GridPoint)
        mouse_pos (tuple[int, int]): aktuální pozice kurzoru myši
        gridpoints_enabled (bool): zapínání/vypínání interaktivnosti
        connections_color: barva spojení (mění se když řešení)
        connections_width: šířka spojení (mění se když řešení)
    """

    draw_2d_grid(screen, points, mouse_pos, gridpoints_enabled)
    draw_grid_label(screen, position, square_length, label)
    draw_lines_from_connections(screen, connections, connections_color, connections_width)

