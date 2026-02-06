# -*- coding: utf-8 -*-
"""
grid_3d.py
-----------

Nástroje pro práci s 3D mřížkou v editoru a hře Cubiq🧊.

Obsahuje funkce a třídy, které:
    • počítají rozměry a pozice 3D gridu na obrazovce,
    • generují body 3×3×3 a vykreslují mřížku s body a spojovacími čarami,
    • spravují uživatelská spojení (přidávání, mazání, slučování),
    • provádějí matematické operace v prostoru (kolinearita, vzdálenosti),
    • porovnávají uživatelské řešení se správným.
"""

import math

import glob_var
import pygame
from elements.connection import Connection3D
from elements.gridpoint import Grid3DPoint
from utils.geometry import draw_dashed_line

GRID_SIZE = 3


# ===============================
# Výpočet velikostí a pozic
# ===============================

def count_square_length() -> int:
    """
    Určí délku čtverce (grid spacing) pro 3d mřížku.
    Přizpůsobuje se rozměrům obrazovky.
    (1/5 obrazovky dole vyhrazena na text k úloze)

    Returns:
        int: délka jednoho čtverce mřížky
    """
    if (glob_var.SCREEN_WIDTH // 9) > (((4 * glob_var.SCREEN_HEIGHT) // 5) // 5):
        return ((4 * glob_var.SCREEN_HEIGHT) // 5) // 5
    return glob_var.SCREEN_WIDTH // 9


def count_length_of_shift_to_3d(square_length: int) -> float:
    """
    Vrátí velikost posunu mezi jednotlivými 3d vrstvami.
    Jedná se o volné rovnoběžné promítání (kolmice → 45°, 1/2 délky).

    Args:
        square_length (int): délka jedné strany čtverce

    Returns:
        float: posun mezi vrstvami 3d mřížky
    """
    return (square_length / math.sqrt(2)) / 2


def find_left_upper_corner(square_length: int, length_of_shift_to_3d: float) -> list[float]:
    """
    Vypočítá levý horní roh krychlové mřížky (3×3×3),
    aby byla umístěna v pravé části obrazovky.
    (1/5 obrazovky dole vyhrazena na text k úloze)

    Args:
        square_length (int): délka jedné strany čtverce
        length_of_shift_to_3d (float): posun mezi jednotlivými vrstvami

    Returns:
        list[float]: souřadnice levého horního rohu mřížky [x, y]
    """
    right_centre = [(glob_var.SCREEN_WIDTH * 3) // 4,
                    ((4 * glob_var.SCREEN_HEIGHT) // 5) // 2]
    c = [right_centre[0] - (square_length + length_of_shift_to_3d),
         right_centre[1] - (square_length - length_of_shift_to_3d)]
    return c


def find_left_upper_corner_in_middle_of_screen_width(square_length: int, length_of_shift_to_3d: float) -> list[float]:
    centre = [glob_var.SCREEN_WIDTH // 2, 3*glob_var.SCREEN_HEIGHT // 7]
    c = [centre[0] - (square_length + length_of_shift_to_3d),
         centre[1] - (square_length - length_of_shift_to_3d)]
    return c


# ===============================
# Práce s body a mřížkou
# ===============================

def create_3d_points(in_middle=False) -> list:
    """
    Vytvoří 3d mřížku 3×3×3 bodů.
    Vrací seznam objektů GridPoint se souřadnicemi (x, y)
    a indexy (col, row, lay).

        :param in_middle:    jestli to vykreslit uprostřed (pro tutoriál)
    Args:
        start (list[float]): levý horní roh mřížky [x, y]
        square_length (int): délka jedné strany čtverce
        length_of_shift_to_3d (float): posun mezi vrstvami

    Returns:
        list[GridPoint]: seznam všech bodů 3d mřížky


    """
    square_length = count_square_length()
    length_of_shift_to_3d = count_length_of_shift_to_3d(square_length)

    if not in_middle:
        start = find_left_upper_corner(square_length, length_of_shift_to_3d)
    else:
        start = find_left_upper_corner_in_middle_of_screen_width(square_length, length_of_shift_to_3d)

    cols = rows = layers = GRID_SIZE
    points = []

    for lay in range(layers):
        actual_start = [
            start[0] + (length_of_shift_to_3d * lay),
            start[1] - (length_of_shift_to_3d * lay)
        ]
        for row in range(rows):
            for col in range(cols):
                x = actual_start[0] + col * square_length
                y = actual_start[1] + row * square_length
                point = Grid3DPoint(x, y, col, row, lay)
                points.append(point)

    return points


def draw_3d_grid(screen: "pygame.Surface", points: list,
                 mouse_pos: tuple[int, int] = None, gridpoints_enabled=True) -> None:
    """
    Vykreslí 3d mřížku (spojení + body).

    Args:
        screen (pygame.Surface): plocha pro vykreslení
        points (list): seznam bodů mřížky (GridPoint)
        mouse_pos (tuple[int, int]): aktuální pozice kurzoru myši
        gridpoints_enabled (bool): zapínání/vypínání interaktivity bodů
    """
    cols = rows = layers = GRID_SIZE
    line_color = (50, 50, 50)
    line_width = int(glob_var.LINE_GRID_WIDTH)

    def index(c, r, l):
        return c + r * cols + l * rows * cols

    for point in points:
        if not gridpoints_enabled:
            point.disable()
        c, r, l = point.col, point.row, point.lay

        if c < cols - 1:
            right = points[index(c + 1, r, l)]
            pygame.draw.line(screen, line_color, (point.x, point.y), (right.x, right.y), line_width)

        if r < rows - 1:
            below = points[index(c, r + 1, l)]
            pygame.draw.line(screen, line_color, (point.x, point.y), (below.x, below.y), line_width)

        if l < layers - 1:
            back = points[index(c, r, l + 1)]
            pygame.draw.line(screen, line_color, (point.x, point.y), (back.x, back.y), line_width)

    for point in points:
        point.draw(screen, mouse_pos)


# ===============================
# Spojení mezi body
# ===============================


def draw_connections(connections: list["Connection3D"], screen: "pygame.Surface",
                     line_color: tuple[int, int, int] = (255, 255, 255),
                     line_width=glob_var.LINE_WIDTH) -> None:
    """
    Vykreslí zadaná spojení mezi body.
    Podporuje čárkované čáry podle atributu conn.dashed.

    Args:
        connections (list["Connection3D"]): seznam úseček
        screen (pygame.Surface): plocha pro vykreslení
        line_color (tuple[int, int, int], optional): barva čáry RGB
        line_width (optional): tloušťka čáry
    """
    radius = int(line_width * 2)
    line_width = int(line_width)
    for conn in connections:
        x1, y1 = conn.point_a.x, conn.point_a.y
        x2, y2 = conn.point_b.x, conn.point_b.y

        if (x1, y1) == (x2, y2):
            pygame.draw.circle(screen, line_color, (x1, y1), radius)
        else:
            if getattr(conn, "dashed", False):
                # čárkovaná čára
                draw_dashed_line(screen, line_color, (x1, y1), (x2, y2), width=int(line_width//2))
            else:
                pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), line_width)

