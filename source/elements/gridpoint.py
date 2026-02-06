# -*- coding: utf-8 -*-
"""
gridpoint.py
------------
Třídy pro reprezentaci bodů v mřížkách 2D a 3D v aplikaci Cubiq🧊.

Obsahuje:
    • GridPoint – obecná třída se společným chováním pro všechny typy gridů,
        zahrnuje výběr myší, kreslení bodu, tvorbu spojení a reset stavu,
    • Grid2DPoint – specializace pro 2D grid (půdorys, nárys, bokorys),
    • Grid3DPoint – specializace pro 3D grid (sloupec, řádek, vrstva),
    • metody pro interaktivní klikání, kreslení a zvýraznění bodů.
"""

import math

import pygame
import glob_var
from elements.connection import Connection2D
from elements.connection import Connection3D
from utils.geometry import draw_dashed_line

pygame.init()


class GridPoint:
    """
    Obecná třída pro bod v mřížce (použitelná pro 2D i 3D grid).

    Sdílí základní chování:
        • výběr myší,
        • kreslení bodu a zvýraznění,
        • tvorbu spojení (Connection),
        • reset stavu výběru.
    """

    def __init__(self, x: float, y: float,
                 radius=glob_var.RADIUS, hover_radius=(glob_var.LINE_WIDTH * 5),
                 highlighted_radius=(glob_var.LINE_WIDTH * 1.5),
                 color=(100, 100, 100), hover_color=(255, 255, 255), enabled=True):
        """
        Inicializuje základní vlastnosti bodu.

        Args:
            x (float): X souřadnice bodu
            y (float): Y souřadnice bodu
            radius (int, optional): poloměr bodu
            hover_radius (int, optional): poloměr pro detekci myši
            highlighted_radius (int, optional): poloměr zvýraznění
            color (tuple, optional): barva bodu (RGB)
            hover_color (tuple, optional): barva bodu při najetí myší (RGB)
        """
        self.x = x
        self.y = y
        self.radius = int(radius)
        self.hover_radius = int(hover_radius)
        self.highlighted_radius = int(highlighted_radius)
        self.color = color
        self.hover_color = hover_color
        self.selected = False
        self.enabled = enabled  # zapínání/vypínání

    # -------------------------
    # Společné metody
    # -------------------------

    def is_mouse_near(self, mouse_pos: tuple[float, float]) -> bool:
        """Zjistí, zda je kurzor myši v dosahu bodu."""
        mouse_x, mouse_y = mouse_pos
        distance = math.sqrt((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2)
        return distance <= self.hover_radius

    def click(self, points: list, mouse_pos: tuple[float, float], event: pygame.event.Event, connections: list) \
            -> tuple["Connection | None", bool]:
        """
        Zpracuje kliknutí na bod a případně vytvoří spojení s jiným bodem.
        Použije správnou třídu Connection podle typu bodu.
        Přidá logiku pro dashed čáry při stisknutém Ctrl.
        Přidá logiku pro kreslení bodu pomocí shiftu.
        """

        new_connection = None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_mouse_near(mouse_pos):

                # --- SHIFT = nakresli bod (nulová čára) ---
                # SHIFT = nakresli / smaž bod
                shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                if shift_pressed:
                    # hledáme, jestli bod už existuje
                    existing_conn = next(
                        (c for c in connections if c.point_a == self and c.point_b == self), None
                    )
                    if existing_conn:
                        # pokud existuje, smaž ho
                        connections.remove(existing_conn)
                        # zruš výběr všech bodů
                        for p in points:
                            p.selected = False
                        return None, True
                    else:
                        # pokud neexistuje, nakresli bod
                        if isinstance(self, Grid2DPoint):
                            new_connection = Connection2D(self, self, dashed=False)
                        else:
                            new_connection = Connection3D(self, self, dashed=False)

                        # zruš výběr všech bodů
                        for p in points:
                            p.selected = False
                        return new_connection, True

                # --- běžná logika klikání ---
                if self.selected:
                    self.selected = False
                    return None, True

                selected_points = [p for p in points if p.selected]

                if len(selected_points) == 1 and selected_points[0] != self:
                    other = selected_points[0]

                    # Ctrl → dashed
                    ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
                    dashed = bool(ctrl_pressed)

                    # najdi existující spojení
                    existing_conn = None
                    for conn in connections:
                        if conn.connects(self, other):
                            existing_conn = conn
                            break

                    if existing_conn:
                        if existing_conn.dashed != dashed:
                            connections.remove(existing_conn)
                            if isinstance(self, Grid2DPoint):
                                new_connection = Connection2D(other, self, dashed=dashed)
                            else:
                                new_connection = Connection3D(other, self, dashed=dashed)
                    else:
                        if isinstance(self, Grid2DPoint):
                            new_connection = Connection2D(other, self, dashed=dashed)
                        else:
                            new_connection = Connection3D(other, self, dashed=dashed)

                    for p in points:
                        p.selected = False

                else:
                    for p in points:
                        p.selected = False
                    self.selected = True

                return new_connection, True

        return None, False

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[float, float]):
        """
        Vykreslí bod a případně čáru k myši, pokud je vybrán.
        Pokud je při tom stisknutý Ctrl, čára se kreslí čárkovaně.
        """
        self.radius = int(glob_var.RADIUS)
        self.hover_radius = int(glob_var.LINE_WIDTH * 5)
        self.highlighted_radius = int(glob_var.LINE_WIDTH * 1.5)

        line_width = int(glob_var.LINE_WIDTH)
        line_color = (255, 255, 255)

        if not self.enabled:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        else:
            if self.selected:
                # zjisti, jestli je Ctrl stisknuté
                ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

                if ctrl_pressed:
                    # čárkovaná čára – rozdělíme ji na segmenty
                    draw_dashed_line(screen, line_color, (self.x, self.y), mouse_pos, int(line_width // 2))
                else:
                    # klasická plná čára
                    pygame.draw.line(screen, line_color, (self.x, self.y), mouse_pos, line_width)

            elif self.is_mouse_near(mouse_pos):
                pygame.draw.circle(screen, self.hover_color, (self.x, self.y), self.highlighted_radius)
            else:
                pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def reset(self):
        """Resetuje stav výběru bodu."""
        self.selected = False

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True


class Grid3DPoint(GridPoint):
    """
    Reprezentuje bod v 3D mřížce.
    """

    def __init__(self, x: float, y: float, col: int, row: int, lay: int,
                 radius=glob_var.RADIUS, hover_radius=(glob_var.LINE_WIDTH * 5),
                 highlighted_radius=(glob_var.LINE_WIDTH * 1.5),
                 color=(100, 100, 100), hover_color=(255, 255, 255), enabled=True):
        """
        Inicializuje bod v 3D mřížce.

        Args:
            x (float): X souřadnice bodu
            y (float): Y souřadnice bodu
            col (int): sloupec v mřížce
            row (int): řádek v mřížce
            lay (int): vrstva v mřížce
        """
        super().__init__(x, y, radius, hover_radius, highlighted_radius, color, hover_color, enabled=True)
        self.col = col
        self.row = row
        self.lay = lay


class Grid2DPoint(GridPoint):
    """Reprezentuje bod v 2D mřížce (půdorys, nárys, bokorys)."""

    def __init__(self, x: float, y: float, col: int, row: int,
                 radius=glob_var.RADIUS, hover_radius=(glob_var.LINE_WIDTH * 5),
                 highlighted_radius=(glob_var.LINE_WIDTH * 1.5),
                 color=(100, 100, 100), hover_color=(255, 255, 255), enabled=True):
        """
        Inicializuje bod v 2D mřížce.

        Args:
            x (float): X souřadnice bodu
            y (float): Y souřadnice bodu
            col (int): sloupec v mřížce
            row (int): řádek v mřížce
        """
        super().__init__(x, y, radius, hover_radius, highlighted_radius, color, hover_color, enabled=True)
        self.col = col
        self.row = row

