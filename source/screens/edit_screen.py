# -*- coding: utf-8 -*-
"""
edit_screen.py
---------------

Editorová obrazovka úlohy (Edit) pro hru Cubiq🧊.

Obsahuje třídu EditScreen, která:
    • umožňuje vytvářet a upravovat 2D pohledy (půdorys, nárys, bokorys) a 3D mřížku,
    • poskytuje tlačítka pro ukládání, mazání, vyčištění a přepínání 2D/3D,
    • spravuje InputBox pro zadání textu úlohy,
    • mapuje spojení mezi body na skutečné GridPoint objekty,
    • zpracovává události myši a klávesnice (levé/pravé tlačítko, ESC, Enter),
    • vykresluje celé prostředí úlohy s oddělovací čárou, ID úlohy a navigačními prvky.
"""

import sys

import glob_var
import pygame
from elements.button import Button
from elements.connection import Connection2D, Connection3D
from elements.task_data import TaskData
from elements.input_box import InputBox
from grids import grid_2d, grid_3d
from utils import grid_fun, grid_math
from utils.UI import MouseClickHandler
from utils.data_creating_fun import save_task_to_json, delete_from_json


class EditScreen:
    """Jednoduchá obrazovka úlohy pro editor."""

    def __init__(self, level_data):
        """
        Inicializuje seznam bodů a spojení.
        """

        # správa kapitol a levlů
        self.level_data = level_data
        self.levels = self.level_data.get_all_levels()

        # pro 3D
        self.points = []
        self.user_connections = []

        # pro 2D
        self.p_points = []
        self.n_points = []
        self.b_points = []

        # zabránění kreslení čáry do více gridů najednou
        self.active_grid = None  # None = žádný aktivní, "p"/"n"/"b"/"c" = aktivní grid (c jako cube)

        self.current_task = None  # bude obsahovat instanci TaskData

        # tlačítka pro ukládání a mazání, x a y se dopočítají
        width = height = glob_var.BTN_HEIGHT
        width_del_and_sav = width * 2
        self.btn_delete = Button(0, 0, width_del_and_sav, height, "Smazat")
        self.btn_save = Button(0, 0, width_del_and_sav, height, "Uložit")
        self.margin_x_button = glob_var.X_OFFSET

        # tlačítko pro přepínání mezi 2d_to_3d a 3d_to_2d
        self.btn_change = Button(0, 0, width, (5 / 6) * height, "<--")

        # tlačítko Vyčistit na smazání všech uživatelských úseček
        clean_width = width * 2
        self.btn_clean = Button(0, 0, clean_width, height, "Vyčistit")

        # Y souřadnice čáry
        self.line_y = (4 * glob_var.SCREEN_HEIGHT) // 5

        # řeší dvojklik
        self.mouse_click_handler = MouseClickHandler(double_click_interval=400)

        # pro 3D -> 2D
        self.user_pudorys_connections = []
        self.user_narys_connections = []
        self.user_bokorys_connections = []

        # časovač pro blikání kurzoru v InputBoxu
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(120)  # ms od posledního frame

    # ------------------------
    # "namapování" bodů na skutečné GridPoint objekty
    # ------------------------

    def _map_connections_to_points_2d(self, connections_2d, points_2d):
        """
        Nahradí body v Connection2D (které mají jen col,row) skutečnými Grid2DPointy z 2D gridu.

        Args:
            connections (list[Connection2D]): spoje z TaskData (indexové)
            points_2d (list[Grid2DPoint]): body vytvořené v create_2d_points()

        Returns:
            list[Connection2D]: spoje s reálnými Grid2DPointy (s x,y)
        """
        mapped = []

        for conn in connections_2d:
            a, b = conn.point_a, conn.point_b
            dashed = conn.dashed
            a_match = next((p for p in points_2d if p.col == a.col and p.row == a.row), None)
            b_match = next((p for p in points_2d if p.col == b.col and p.row == b.row), None)

            if a_match or b_match:
                mapped.append(Connection2D(a_match, b_match, dashed))

        return mapped

    def _map_connections_to_points_3d(self, connections_3d, points_3d):
        """
        Nahradí body v Connection3D (které mají jen col,row,lay) skutečnými Grid3DPointy z 3D gridu.

        Args:
            connections (list[Connection3D]): spoje z TaskData (indexové)
            points_3d (list[Grid3DPoint]): body vytvořené v create_3d_points()

        Returns:
            list[Connection3D]: spoje s reálnými Grid3DPointy (s x,y,z)
        """
        mapped = []

        for conn in connections_3d:
            a, b = conn.point_a, conn.point_b
            dashed = conn.dashed
            a_match = next((p for p in points_3d if p.col == a.col and p.row == a.row and p.lay == a.lay), None)
            b_match = next((p for p in points_3d if p.col == b.col and p.row == b.row and p.lay == b.lay), None)

            if a_match or b_match:
                mapped.append(Connection3D(a_match, b_match, dashed))

        return mapped

    def _ensure_grids_initialized(self):
        """Inicializuje 3D a 2D gridy pouze jednou."""
        if not self.points:
            self.points = grid_3d.create_3d_points()

        if not self.p_points:
            self.p_points, self.n_points, self.b_points = grid_2d.create_all_2d_points()

    # ------------------------
    # Načtení úlohy
    # ------------------------
    def load_task(self, task_id):
        self.current_task = TaskData(task_id)
        if self.current_task.task_type == "2D_to_3D":
            self.btn_change.text = "-->"
        elif self.current_task.task_type == "3D_to_2D":
            self.btn_change.text = "<--"

        self._ensure_grids_initialized()

        # map connections → reálné body s x,y,z
        self.user_connections = self._map_connections_to_points_3d(self.current_task.connections_3d, self.points)
        self.user_pudorys_connections = self._map_connections_to_points_2d(self.current_task.pudorys_connections,
                                                                           self.p_points)
        self.user_narys_connections = self._map_connections_to_points_2d(self.current_task.narys_connections,
                                                                         self.n_points)
        self.user_bokorys_connections = self._map_connections_to_points_2d(self.current_task.bokorys_connections,
                                                                           self.b_points)

    # ------------------------
    # Reset úlohy
    # ------------------------
    def _clear_all_user_connections(self):
        self.user_connections.clear()
        self.user_pudorys_connections.clear()
        self.user_narys_connections.clear()
        self.user_bokorys_connections.clear()

    def reset_task(self):
        """Vymaže data aktuální úlohy před načtením nové."""
        self.points.clear()
        self.current_task = None
        if hasattr(self, 'task_input_box'):
            del self.task_input_box
        self._clear_all_user_connections()

    # ======================================================
    # Pomocné metody pro handle_events
    # ======================================================

    def _handle_mouse_down_for_grids(self, mouse_pos, event):
        """
        Jediná funkce pro levé tlačítko DOWN – 3D i 2D.
        Zakazuje kreslení do více gridů najednou.
        """
        clicked_any = False

        # --- 3D body ---
        if self.active_grid is None or self.active_grid == "c":
            for point in self.points:
                new_conn, clicked = point.click(self.points, mouse_pos, event, self.user_connections)
                if clicked:
                    self.active_grid = "c"
                if new_conn:
                    self.active_grid = None  # po vytvoření spojení můžeme uvolnit aktivní grid
                    self.user_connections.append(new_conn)
                    self.user_connections = grid_fun.merge_if_double_connections_3d(self.user_connections)
                if clicked:
                    clicked_any = True
                    break

        # --- 2D body ---
        if not clicked_any:
            grids = [
                (self.p_points, self.user_pudorys_connections, "p"),
                (self.n_points, self.user_narys_connections, "n"),
                (self.b_points, self.user_bokorys_connections, "b"),
            ]

            for points_list, user_conns, grid_key in grids:
                if self.active_grid is None or self.active_grid == grid_key:
                    for point in points_list:
                        new_conn, clicked = point.click(points_list, mouse_pos, event, user_conns)
                        if clicked:
                            self.active_grid = grid_key
                        if new_conn:
                            self.active_grid = None
                            user_conns.append(new_conn)
                            grid_fun.merge_if_double_connections_2d(user_conns)
                        if clicked:
                            clicked_any = True
                            break
                if clicked_any:
                    break

        # --- žádný bod nekliknut → reset selection ---
        if not clicked_any:
            self.active_grid = None
            for p in self.points:
                p.selected = False
            for points_list, _, _ in grids:
                for p in points_list:
                    p.selected = False

            # --- dvojklik: smaže spojení všude ---
            click_type = self.mouse_click_handler.check_click(event)
            if click_type == "double":
                grid_fun.delete_connection(self.user_connections, mouse_pos)
                for conns in (
                        self.user_pudorys_connections, self.user_narys_connections, self.user_bokorys_connections):
                    grid_fun.delete_connection(conns, mouse_pos)

    def _save_task(self, task):
        task_id = task.task_id

        text = self.task_input_box.get_text()

        if str(task.task_id).startswith("0."):
            task_type = "tutorial"
        else:
            if self.btn_change.text == "<--":
                task_type = "3D_to_2D"
            else:
                task_type = "2D_to_3D"

        p_connections = self.user_pudorys_connections
        n_connections = self.user_narys_connections
        b_connections = self.user_bokorys_connections
        d_connections = [self.user_connections]

        save_task_to_json(task_id, text, task_type, p_connections, n_connections, b_connections, d_connections)

    def _handle_buttons_down(self, task, event) -> bool:
        clicked_delete = self.btn_delete.click(event)
        clicked_save = self.btn_save.click(event)
        clicked_change = self.btn_change.click(event)
        clicked_clean = self.btn_clean.click(event)
        escape_pressed = False

        if clicked_clean:
            self._clear_all_user_connections()

        if clicked_delete:
            print("smazání příkladu")
            delete_from_json(task.task_id)
            escape_pressed = True

        elif clicked_save:
            print("uložení příkladu")
            self._save_task(task)
            escape_pressed = True

        elif clicked_change:
            print("změna typu tasku")
            if self.btn_change.text == "<--":
                self.btn_change.text = "-->"
            elif self.btn_change.text == "-->":
                self.btn_change.text = "<--"

        return escape_pressed

    # ============================================
    # Události myši a klávesnice
    # ============================================
    def handle_events(self, events):
        """
        Zpracuje všechny události: klávesy, kliknutí myší.

        Args:
            events (list): seznam událostí z pygame.event.get()

        Returns:
            tuple: escape_pressed
        """
        escape_pressed = False

        task = self.current_task
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # -----------------------------
            # ESC
            # -----------------------------
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._clear_all_user_connections()
                escape_pressed = True
                self.reset_task()

            # -----------------------------
            # INPUT BOX
            # -----------------------------
            # --- kliknutí do InputBoxu nebo mimo něj ---
            if hasattr(self, 'task_input_box'):
                self.task_input_box.handle_mouse_event(event)

            # --- zpracování kláves jen pokud je aktivní ---
            if hasattr(self, 'task_input_box') and self.task_input_box.active:
                enter_pressed = self.task_input_box.handle_event(event)
                if enter_pressed:
                    print("Uživatel stiskl Enter, text:", self.task_input_box.get_text())

            # -----------------------------
            # Levé tlačítko DOWN – body a nastavení tlačítek
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # tlačítka – jen nastaví clicked_inside
                self.btn_delete.click(event)
                self.btn_save.click(event)
                self.btn_change.click(event)
                self.btn_clean.click(event)

                self._handle_mouse_down_for_grids(mouse_pos, event)

            # -----------------------------
            # Levé tlačítko UP – tlačítka
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                escape_pressed = self._handle_buttons_down(task, event)
                if escape_pressed:
                    self.reset_task()

            # -----------------------------
            # Pravé tlačítko – přepínání dashed
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                grid_fun.change_dashed_of_connection(self.user_connections, mouse_pos)
                self.user_connections = grid_fun.merge_if_double_connections_3d(self.user_connections)
                for conns in (
                        self.user_pudorys_connections,
                        self.user_narys_connections,
                        self.user_bokorys_connections
                ):
                    grid_fun.change_dashed_of_connection(conns, mouse_pos)
                    grid_fun.merge_if_double_connections_2d(conns)

        return escape_pressed

    # ======================================================
    # Pomocné metody pro draw
    # ======================================================

    def draw_buttons(self, screen, current_task):
        """Vykreslí tlačítka < a > vedle textu, fixně vycentrovaná mezi čárou a spodním okrajem okna."""
        margin_x = self.margin_x_button
        line_y = self.line_y
        bottom_y = glob_var.SCREEN_HEIGHT

        # vertikální střed mezi čárou a spodním okrajem
        center_y = line_y + (bottom_y - line_y) // 2

        # nastavení pozice tlačítek
        self.btn_delete.set_x(margin_x)
        self.btn_delete.set_y(center_y - self.btn_delete.get_height() // 2)

        self.btn_save.set_x(glob_var.SCREEN_WIDTH - margin_x - self.btn_delete.get_width())
        self.btn_save.set_y(center_y - self.btn_save.get_height() // 2)

        self.btn_save.enable()
        self.btn_delete.draw(screen)
        self.btn_save.draw(screen)

    def draw_clean_button(self, screen):
        x_spacing = 20

        y_offset = (1 / 4) * glob_var.BTN_HEIGHT + glob_var.BTN_HEIGHT
        y = self.line_y - y_offset

        x = int(glob_var.SCREEN_WIDTH//2 - self.btn_clean.get_width()//2) + x_spacing

        self.btn_clean.set_x(x)
        self.btn_clean.set_y(y)
        self.btn_clean.draw(screen)

    def draw_task_text(self, screen, text):
        """
        Vykreslí text zadání úlohy vycentrovaný mezi čárou a spodním okrajem okna
        a odsazený od tlačítek Smazat a Uložit, pomocí jednoho InputBoxu.
        """
        margin_x = self.btn_delete.get_width() + self.margin_x_button + 40
        line_y = (4 * glob_var.SCREEN_HEIGHT) // 5
        bottom_y = glob_var.SCREEN_HEIGHT
        max_width = glob_var.SCREEN_WIDTH - 2 * margin_x

        # výška InputBoxu = 90% prostoru mezi čárou a spodním okrajem
        box_height = (bottom_y - line_y) * 0.9

        # vertikálně vycentrovaný y
        box_y = line_y + ((bottom_y - line_y) - box_height) // 2

        # maximální počet znaků
        max_length = 200

        # vytvoření InputBoxu
        if not hasattr(self, 'task_input_box'):
            self.task_input_box = InputBox(
                x=margin_x,
                y=box_y,
                w=max_width,
                h=box_height,
                text=text,
                max_length=max_length
            )
            self.task_input_box.active = False

        if hasattr(self, 'task_input_box'):
            self.dt = self.clock.tick(120)  # aktualizace času pro kurzor
            self.task_input_box.update(self.dt)
            self.task_input_box.draw(screen)

    def _ensure_task_loaded(self, task_id):
        """Načte TaskData pouze při změně úlohy, NERESERTUJE uživatelská spojení."""
        if self.current_task is None or self.current_task.task_id != str(task_id):
            self.load_task(task_id)

    def _draw_2d_grids(self, screen, task, mouse_pos):
        """Vykreslí všechny 2D pohledy (půdorys, nárys, bokorys)."""
        l_square_length = grid_2d.count_square_length()
        p_pos, n_pos, b_pos = grid_2d.find_left_upper_corners(l_square_length)

        # Napárování spojů z TaskData → reálné body
        p_conns = self._map_connections_to_points_2d(self.user_pudorys_connections, self.p_points)
        n_conns = self._map_connections_to_points_2d(self.user_narys_connections, self.n_points)
        b_conns = self._map_connections_to_points_2d(self.user_bokorys_connections, self.b_points)

        grids = [
            ("Půdorys", p_pos, self.p_points, p_conns, "p"),
            ("Nárys", n_pos, self.n_points, n_conns, "n"),
            ("Bokorys", b_pos, self.b_points, b_conns, "b"),
        ]

        for title, pos, points, conns, grid_key in grids:
            grid_2d.draw_task(screen, pos, l_square_length, title, conns, points, mouse_pos=mouse_pos,
                              gridpoints_enabled=(self.active_grid in (None, grid_key)), connections_width=glob_var.LINE_WIDTH)

    def _draw_3d_part(self, screen, task, mouse_pos):
        """Vykreslí 3D mřížku a případně i řešení."""
        grid_3d.draw_3d_grid(screen, self.points, mouse_pos)
        grid_3d.draw_connections(self.user_connections, screen, line_width=glob_var.LINE_WIDTH)

    def _draw_separator_and_text(self, screen, task):
        """Vykreslí oddělovací čáru a text zadání."""
        y = (4 * glob_var.SCREEN_HEIGHT) // 5
        pygame.draw.line(screen, (100, 100, 100), (0, y), (glob_var.SCREEN_WIDTH, y), 2)

        if task.text.strip():
            self.draw_task_text(screen, task.text)

    def _draw_id(self, screen, task):
        """
        Vykreslí ID aktuální úlohy nahoře uprostřed obrazovky s čitelným pozadím.

        Args:
            screen (pygame.Surface): surface, kam se kreslí
            task (TaskData): aktuální úloha
        """
        x_spacing = 20

        if task is None:
            return

        # Text
        text = f"Úloha ID: {task.task_id}"
        text_surface = glob_var.FONT.render(text, True, (255, 255, 255))  # bílá barva

        # Pozice - nahoře uprostřed
        x = ((glob_var.SCREEN_WIDTH - text_surface.get_width()) // 2) + x_spacing
        y = (1 / 5) * glob_var.Y_OFFSET
        # Černé pozadí pro lepší čitelnost
        padding = 4
        bg_rect = pygame.Rect(
            x - padding,
            y - padding,
            text_surface.get_width() + 2 * padding,
            text_surface.get_height() + 2 * padding
        )
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=5)

        # Vykreslení textu
        screen.blit(text_surface, (x, y))

    def _draw_top_controls(self, screen, task):
        if not task:
            return

        y = (1 / 2) * glob_var.Y_OFFSET + (1 / 5) * glob_var.Y_OFFSET + glob_var.FONT_SIZE  # vertikální pozice nahoře
        is_tutorial = str(task.task_id).startswith("0.")

        white = (255, 255, 255)
        spacing = glob_var.X_OFFSET // 2  # mezera mezi textem a tlačítkem
        x_spacing = 20

        if is_tutorial:
            # tutorial text doprostřed
            surf = glob_var.FONT.render("Tutorial", True, white)
            x = ((glob_var.SCREEN_WIDTH - surf.get_width()) // 2) + x_spacing
            screen.blit(surf, (x, y))
        else:
            # levý a pravý text
            left_surf = glob_var.FONT.render("2D", True, white)
            right_surf = glob_var.FONT.render("3D", True, white)

            # tlačítko doprostřed
            self.btn_change.set_x(((glob_var.SCREEN_WIDTH - self.btn_change.get_width()) // 2) + x_spacing)
            self.btn_change.set_y(y)
            self.btn_change.draw(screen)

            # pozice levého a pravého textu
            left_x = self.btn_change.rect.x - spacing - left_surf.get_width()
            right_x = self.btn_change.rect.x + self.btn_change.get_width() + spacing

            screen.blit(left_surf, (left_x, y))
            screen.blit(right_surf, (right_x, y))

    # ------------------------
    # Vykreslení úlohy
    # ------------------------
    def draw(self, screen, task_id):
        """
        Vykreslí úkol na obrazovku.
        """
        self._ensure_task_loaded(task_id)

        task = self.current_task
        screen.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # Tlačítko ">" mezi "2D" a "3D" nebo "Tutorial"
        self._draw_top_controls(screen, task)

        # ID úlohy nahoře uprostřed
        self._draw_id(screen, task)

        self._draw_2d_grids(screen, task, mouse_pos)
        self._draw_3d_part(screen, task, mouse_pos)
        self._draw_separator_and_text(screen, task)

        self.draw_buttons(screen, task)
        self.draw_clean_button(screen)

