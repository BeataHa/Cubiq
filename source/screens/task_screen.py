# -*- coding: utf-8 -*-
"""
task_screen.py
--------------

Obrazovka řešení úlohy (Task) ve hře Cubiq🧊.

Obsahuje třídu TaskScreen, která:
    • zobrazuje 2D pohledy (půdorys, nárys, bokorys) a 3D mřížku,
    • umožňuje uživateli spojovat body v prostoru a kontroluje řešení,
    • vykresluje text úlohy a navigační tlačítka,
    • zpracovává události myši a klávesnice.
"""

import pygame

import glob_var
from elements.button import Button
from elements.connection import Connection2D, Connection3D
from elements.task_data import TaskData
from grids import grid_2d, grid_3d
from utils import grid_fun
from utils.UI import MouseClickHandler
from elements.pop_up_window import PopUpWindow


class TaskScreen:
    """
    Obrazovka řešení úkolu (Task) ve hře Cubiq.
    """

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

        # týká se při úlohách z 3d do 2d
        self.active_grid = None  # None = žádný aktivní, "p"/"n"/"b" = aktivní grid

        self.current_task = None  # bude obsahovat instanci TaskData
        self.just_resolved = False  # pamatuje si, zda byla úloha vyřešená v self.draw_buttons

        # tlačítka pro posun mezi úlohami, x a y se dopočítají
        width = height = glob_var.BTN_HEIGHT
        self.btn_prev = Button(0, 0, width, height, "<")
        self.btn_next = Button(0, 0, width, height, ">")
        self.margin_x_button = glob_var.BTN_HEIGHT

        # tlačítka pro vrácení domů "⌂"
        self.btn_home = Button(0, 0, width, height, "⌂")

        # tlačítko Vyčistit na smazání všech uživatelských úseček
        clean_width = width * 2
        self.btn_clean = Button(0, 0, clean_width, height, "Vyčistit")

        # y souřadnice čáry
        self.line_y = (4 * glob_var.SCREEN_HEIGHT) // 5

        # řeší dvojklik
        self.mouse_click_handler = MouseClickHandler(double_click_interval=400)

        # pro 3D -> 2D
        self.user_pudorys_connections = []
        self.user_narys_connections = []
        self.user_bokorys_connections = []

        # Připravit seznam povrchů pro řádky textu (aby se to nepočítalo každý frame)
        self.task_text_surfaces = []
        self.task_text_positions = []

        # vyskakovací okénka  půdorys, nárys, bokorys
        pop_btn_width = pop_btn_height = glob_var.BTN_HEIGHT // 2.5
        color = (150, 150, 150)
        self.pop_btn_n = Button(0, 0, pop_btn_width, pop_btn_height, "?", text_color=color,
                                border_color=color, border_width=1)
        self.pop_btn_p = Button(0, 0, pop_btn_width, pop_btn_height, "?", text_color=color,
                                border_color=color, border_width=1)
        self.pop_btn_b = Button(0, 0, pop_btn_width, pop_btn_height, "?", text_color=color,
                                border_color=color, border_width=1)

        self.pop_up_n = PopUpWindow(0, 0)
        self.pop_up_p = PopUpWindow(0, 0)
        self.pop_up_b = PopUpWindow(0, 0)

        # nápověda kreslení do sítí
        self.pop_btn_draw = Button(0, 0, width, height, "?")

        self.pop_up_draw = PopUpWindow(0, 0)

        # správa načtení výsledku když admin
        self.loaded = False

    # ------------------------
    # Reset úlohy
    # ------------------------
    def _clear_all_points(self):
        self.points.clear()
        self.p_points.clear()
        self.n_points.clear()
        self.b_points.clear()

    def _clear_all_user_connections(self):
        self.user_connections.clear()
        self.user_pudorys_connections.clear()
        self.user_narys_connections.clear()
        self.user_bokorys_connections.clear()

    def reset_task(self):
        """Vymaže data aktuální úlohy před načtením nové."""
        self._clear_all_points()
        self.current_task = None
        self.just_resolved = False
        self._clear_all_user_connections()
        # správa načtení výsledku když admin
        self.loaded = False
        # zavření vyskakovacích oken
        self.pop_up_n.hide()
        self.pop_up_p.hide()
        self.pop_up_b.hide()
        self.pop_up_draw.hide()
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

            if a_match is not None and b_match is not None:
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

            if a_match is not None and b_match is not None:
                mapped.append(Connection3D(a_match, b_match, dashed))

        return mapped

    # ======================================================
    # Pomocné metody pro handle_events
    # ======================================================

    def _handle_2d_to_3d_mouse_down(self, mouse_pos, event):
        clicked_any = False
        for point in self.points:
            new_conn, clicked = point.click(self.points, mouse_pos, event, self.user_connections)
            if new_conn:
                self.user_connections.append(new_conn)
                self.user_connections = grid_fun.merge_if_double_connections_3d(self.user_connections)
            if clicked:
                clicked_any = True
                break

        if not clicked_any:
            for point in self.points:
                point.selected = False

            click_type = self.mouse_click_handler.check_click(event)
            if click_type == "double":
                grid_fun.delete_connection(self.user_connections, mouse_pos)

    def _handle_3d_to_2d_mouse_down(self, mouse_pos, event):
        clicked_any = False
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

        if not clicked_any:
            self.active_grid = None
            for points_list, _, _ in grids:
                for p in points_list:
                    p.selected = False

            click_type = self.mouse_click_handler.check_click(event)
            if click_type == "double":
                for conns in (
                        self.user_pudorys_connections,
                        self.user_narys_connections,
                        self.user_bokorys_connections
                ):
                    grid_fun.delete_connection(conns, mouse_pos)

    def _handle_buttons_down(self, task, event, mouse_pos=None):
        new_task_id = ""
        escape_pressed = False

        clicked_prev = self.btn_prev.click(event)
        clicked_next = self.btn_next.click(event)
        clicked_home = self.btn_home.click(event)
        clicked_clean = self.btn_clean.click(event)
        clicked_pop_n = self.pop_btn_n.click(event)
        clicked_pop_p = self.pop_btn_p.click(event)
        clicked_pop_b = self.pop_btn_b.click(event)
        clicked_pop_draw = self.pop_btn_draw.click(event)

        if clicked_pop_n:
            self.pop_up_n.set_xy(mouse_pos[0], mouse_pos[1])
            self.pop_up_n.show()
        elif clicked_pop_p:
            self.pop_up_p.set_xy(mouse_pos[0], mouse_pos[1])
            self.pop_up_p.show()
        elif clicked_pop_b:
            self.pop_up_b.set_xy(mouse_pos[0], mouse_pos[1])
            self.pop_up_b.show()
        elif clicked_pop_draw:
            self.pop_up_draw.set_xy(glob_var.SCREEN_WIDTH // 2, int(glob_var.BTN_HEIGHT * 1.5))
            self.pop_up_draw.show()

        if clicked_clean:
            self._clear_all_user_connections()

        if clicked_home:
            escape_pressed = True

        elif clicked_prev or (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT):
            chapter, sub = task.task_id.split(".")
            sub = int(sub)
            if sub > 1:
                new_task_id = f"{chapter}.{sub - 1}"

        elif clicked_next or (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT):
            if self.btn_next.enabled:
                chapter, sub = task.task_id.split(".")
                current_chapter = None
                for chap in self.level_data.get_chapters():
                    if any(level.startswith(chapter + ".") for level in chap["levels"]):
                        current_chapter = chap
                        break
                if current_chapter:
                    levels = current_chapter["levels"]
                    current_index = levels.index(task.task_id)
                    if current_index < len(levels) - 1:
                        new_task_id = levels[current_index + 1]
                    else:
                        escape_pressed = True
        else:
            new_task_id = ""
        return new_task_id, escape_pressed

    # ============================================
    # Události myši a klávesnice
    # ============================================
    def handle_events(self, events):
        """
        Zpracuje všechny události: klávesy, kliknutí myší.

        Args:
            events (list): seznam událostí z pygame.event.get()

        Returns:
            tuple(bool, str): (escape_pressed, new_task_id)
            new_task_id = "" pokud zůstávám na stejné úloze
        """
        escape_pressed = False
        new_task_id = ""

        task = self.current_task
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # -----------------------------
            # ESC
            # -----------------------------
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._clear_all_user_connections()
                escape_pressed = True

            # -----------------------------
            # Šipky dopředu a dozadu – posouvání úlohy dpředu nebo dozadu
            # -----------------------------
            # šipka doleva → stejné jako klik na < tlačítko
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                new_task_id, _ = self._handle_buttons_down(self.current_task, event)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                new_task_id, escape_pressed = self._handle_buttons_down(self.current_task, event)

            # -----------------------------
            # Levé tlačítko DOWN – body a nastavení tlačítek
            # -----------------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # tlačítka – jen nastaví clicked_inside
                self.btn_prev.click(event)
                self.btn_next.click(event)
                self.btn_home.click(event)
                self.btn_clean.click(event)
                self.pop_btn_n.click(event)
                self.pop_btn_p.click(event)
                self.pop_btn_b.click(event)
                self.pop_btn_draw.click(event)

                self.pop_up_n.handle_event(event)
                self.pop_up_p.handle_event(event)
                self.pop_up_b.handle_event(event)
                self.pop_up_draw.handle_event(event)

                if (task.task_type == "2D_to_3D") or (
                        (task.task_type == "tutorial") and (
                        task.task_id in ("0.5", "0.6", "0.9", "0.7", "0.8", "0.10"))):
                    self._handle_2d_to_3d_mouse_down(mouse_pos, event)

                elif task.task_type == "3D_to_2D":
                    self._handle_3d_to_2d_mouse_down(mouse_pos, event)

            # -----------------------------
            # Levé tlačítko UP – tlačítka
            # -----------------------------
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_task_id, escape_pressed = self._handle_buttons_down(task, event, mouse_pos)
                self.pop_up_n.handle_event(event)
                self.pop_up_p.handle_event(event)
                self.pop_up_b.handle_event(event)
                self.pop_up_draw.handle_event(event)

            # -----------------------------
            # Pravé tlačítko – přepínání dashed
            # -----------------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if task.task_type == "2D_to_3D" or (
                        (task.task_type == "tutorial") and (
                        task.task_id in ("0.5", "0.6", "0.9", "0.7", "0.8", "0.10"))):
                    grid_fun.change_dashed_of_connection(self.user_connections, mouse_pos)
                    self.user_connections = grid_fun.merge_if_double_connections_3d(self.user_connections)
                elif task.task_type == "3D_to_2D":
                    for conns in (
                            self.user_pudorys_connections,
                            self.user_narys_connections,
                            self.user_bokorys_connections
                    ):
                        grid_fun.change_dashed_of_connection(conns, mouse_pos)
                        grid_fun.merge_if_double_connections_2d(conns)

        return escape_pressed, new_task_id

    # ======================================================
    # Pomocné metody pro draw
    # ======================================================

    def draw_buttons(self, screen, current_task, was_resolved=False, is_currently_resolved=False):
        """Vykreslí tlačítka < a > vedle textu, fixně vycentrovaná mezi čárou a spodním okrajem okna."""
        margin_x = self.margin_x_button
        line_y = (4 * glob_var.SCREEN_HEIGHT) // 5  # Y souřadnice čáry
        bottom_y = glob_var.SCREEN_HEIGHT

        # vertikální střed mezi čárou a spodním okrajem
        center_y = line_y + (bottom_y - line_y) // 2

        # nastavení pozice tlačítek
        self.btn_prev.set_x(margin_x)
        self.btn_prev.set_y(center_y - self.btn_prev.get_height() // 2)

        self.btn_next.set_x(glob_var.SCREEN_WIDTH - margin_x - self.btn_prev.get_width())
        self.btn_next.set_y(center_y - self.btn_next.get_height() // 2)

        # pokud byla úloha již vyřešená anebo je aktuálně vyřešená, umožni zmáčknutí tlačítka
        if was_resolved or is_currently_resolved or self.just_resolved:
            self.btn_next.enable()

            # pokud je aktuálně vyřešená, změň barvu tlačítka ">" na zlatou
            if is_currently_resolved or self.just_resolved:
                self.btn_next.change_color(text_color=(255, 215, 0), border_color=(255, 215, 0))  # zlatá

            else:
                self.btn_next.change_color(text_color=(255, 255, 255), border_color=(255, 255, 255))  # bílá

        else:
            # úloha ještě není vyřešená → tlačítko neaktivní
            self.btn_next.disable()

        # vykreslení tlačítek
        if current_task.sub_id > 1:
            self.btn_prev.draw(screen)
        self.btn_next.draw(screen)

    def draw_home_button(self, screen):
        x_offset = glob_var.BTN_HEIGHT
        y_offset = (1 / 2) * glob_var.BTN_HEIGHT
        x = glob_var.SCREEN_WIDTH - self.btn_home.get_width() - x_offset
        y = y_offset

        self.btn_home.change_font(pygame.font.SysFont("Segoe UI Symbol", glob_var.FONT_SIZE))

        self.btn_home.set_x(x)
        self.btn_home.set_y(y)
        self.btn_home.draw(screen)

    def draw_clean_button(self, screen, task):
        y_offset = (1 / 2) * glob_var.BTN_HEIGHT + glob_var.BTN_HEIGHT
        y = self.line_y - y_offset
        if (task.task_type == "2D_to_3D") or (task.task_id in ("0.5", "0.6", "0.9")):
            x = int(glob_var.SCREEN_WIDTH - self.btn_clean.get_width() - glob_var.BTN_HEIGHT)
        elif task.task_type == "3D_to_2D":
            x = glob_var.BTN_HEIGHT
        else:
            x = -1000

        self.btn_clean.set_x(x)
        self.btn_clean.set_y(y)
        self.btn_clean.draw(screen)

    def draw_pop_up_buttons(self, screen, p_pos, n_pos, b_pos, l_square_length):
        def shift_to_pop_x(left_grid_corner):
            x, y = left_grid_corner
            pop_x = x + 1.9 * l_square_length
            pop_y = y + 2.5 * l_square_length
            return pop_x, pop_y

        # vypočítat nové pozice tlačítek
        n_x, n_y = shift_to_pop_x(n_pos)
        p_x, p_y = shift_to_pop_x(p_pos)
        b_x, b_y = shift_to_pop_x(b_pos)

        # nastavit pozice
        self.pop_btn_n.set_x(n_x)
        self.pop_btn_n.set_y(n_y)

        self.pop_btn_p.set_x(p_x)
        self.pop_btn_p.set_y(p_y)

        self.pop_btn_b.set_x(b_x)
        self.pop_btn_b.set_y(b_y)

        # nastavit menší font
        self.pop_btn_n.change_font(glob_var.POP_UP_FONT)
        self.pop_btn_p.change_font(glob_var.POP_UP_FONT)
        self.pop_btn_b.change_font(glob_var.POP_UP_FONT)

        # vykreslit
        self.pop_btn_n.draw(screen)
        self.pop_btn_p.draw(screen)
        self.pop_btn_b.draw(screen)

    def draw_pop_up_draw_button(self, screen):
        # vypočítat nové pozice tlačítek
        x = int(glob_var.SCREEN_WIDTH - glob_var.BTN_HEIGHT * 3.5)
        y = glob_var.BTN_HEIGHT // 2

        # nastavit pozice
        self.pop_btn_draw.set_x(x)
        self.pop_btn_draw.set_y(y)

        # vykreslit
        self.pop_btn_draw.draw(screen)

    def draw_pop_up_windows(self, screen, task):
        if task.task_id in ("0.1", "0.2", "0.3", "0.4"):
            return

        self.pop_up_n.set_text("Nárys – pohled zepředu.\nHlavní pohled pravoúhlého promítání.")
        self.pop_up_p.set_text("Půdorys – pohled shora.")
        self.pop_up_b.set_text(
            "Levý bokorys – pohled zprava.")

        self.pop_up_n.draw(screen)
        self.pop_up_p.draw(screen)
        self.pop_up_b.draw(screen)

    def draw_pop_up_draw_window(self, screen, task):
        if task.task_id in ("0.1", "0.2", "0.3", "0.4"):
            return

        self.pop_up_draw.set_text(
            "Plná úsečka... levé tlačítko myši.\nČárkovaná úsečka... levé tlačítko myši + Ctrl.\nMazání úsečky... levý dvojklik.\nPřepínání čárkovaná/plná... pravé tlačítko myši.\nKreslení bodu... levé tlačítko myši + Shift.\nMazání bodu... levé tlačítko myši + Shift.")
        self.pop_up_draw.draw(screen)

    def _draw_id(self, screen, task, was_resolved=False, is_currently_resolved=False):
        """
        Vykreslí ID aktuální úlohy nahoře uprostřed obrazovky s čitelným pozadím.
        Zlatě se vybarví pouze ID úlohy.
        """
        if task is None:
            return

        # Texty
        if task.task_type == "tutorial":
            prefix = "Tutoriál: "
        else:
            prefix = "Úloha: "

        task_id_text = str(task.task_id)

        # Barva ID
        if (was_resolved or is_currently_resolved or self.just_resolved) and (
                not task.task_id in ("0.1", "0.2", "0.3", "0.4")):
            id_color = (255, 215, 0)  # zlatá
        else:
            id_color = (255, 255, 255)

        prefix_color = (255, 255, 255)

        # Render jednotlivých částí
        prefix_surf = glob_var.FONT.render(prefix, True, prefix_color)
        id_surf = glob_var.FONT.render(task_id_text, True, id_color)

        total_width = prefix_surf.get_width() + id_surf.get_width()

        # Pozice – nahoře uprostřed
        x = (glob_var.SCREEN_WIDTH - total_width) // 2
        y = glob_var.BTN_HEIGHT // 2

        # Pozadí
        padding = 8
        bg_rect = pygame.Rect(
            x - padding,
            y - padding,
            total_width + 2 * padding,
            max(prefix_surf.get_height(), id_surf.get_height()) + 2 * padding
        )
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=5)

        # Vykreslení textů
        screen.blit(prefix_surf, (x, y))
        screen.blit(id_surf, (x + prefix_surf.get_width(), y))

    def _draw_arrow(self, screen, task):
        if not task:
            return

        y = (5 / 7) * glob_var.SCREEN_HEIGHT // 2

        color = (150, 150, 150)
        if not (task.task_id in ("0.1", "0.2", "0.3", "0.4")):
            if task.task_type == "3D_to_2D":
                surf = glob_var.FONT.render("<--", True, color)
            else:
                surf = glob_var.FONT.render("-->", True, color)
            x = ((glob_var.SCREEN_WIDTH - surf.get_width()) // 2)
            screen.blit(surf, (x, y))

    def prepare_task_text(self, text):
        """Vykreslí text zadání úlohy vycentrovaný mezi čárou a spodním okrajem okna a odsazený od tlačítek < a >."""
        font = glob_var.FONT
        color = (230, 230, 230)

        # margin_x = šířka tlačítek + x_offset talčítka + rezerva
        margin_x = self.btn_prev.get_width() + self.margin_x_button + 40
        line_y = (4 * glob_var.SCREEN_HEIGHT) // 5  # Y souřadnice čáry
        bottom_y = glob_var.SCREEN_HEIGHT  # dolní okraj
        max_width = glob_var.SCREEN_WIDTH - 2 * margin_x
        line_spacing = 5  # mezera mezi řádky
        padding_top = 8  # mezera od čáry nad textem

        available_height = bottom_y - line_y - padding_top

        font_size = font.get_height()
        min_font_size = 16

        # Zmenšování fontu, pokud text přeteče
        while font_size >= min_font_size:
            font = pygame.font.SysFont("Gabriola", font_size)

            words = text.split(" ")
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())

            total_text_height = (
                    sum(font.size(line)[1] for line in lines)
                    + line_spacing * (len(lines) - 1)
            )

            if total_text_height <= available_height:
                break

            font_size -= 1

        # Vertikální pozice
        top_y = line_y + padding_top + (available_height - total_text_height) // 2

        # Připravit seznam povrchů
        self.task_text_surfaces = []
        self.task_text_positions = []

        y = top_y
        for line in lines:
            surf = font.render(line, True, color)
            x = margin_x + (max_width - surf.get_width()) // 2
            self.task_text_surfaces.append(surf)
            self.task_text_positions.append((x, y))
            y += surf.get_height() + line_spacing

    def draw_task_text(self, screen):
        """Vykreslí předem připravené povrchy textu."""
        for surf, pos in zip(self.task_text_surfaces, self.task_text_positions):
            screen.blit(surf, pos)

    def _ensure_task_loaded(self, task_id):
        """Načte TaskData pouze při změně úlohy, NERESERTUJE uživatelská spojení."""
        if self.current_task is None or self.current_task.task_id != str(task_id):
            # Vytvoření nové úlohy
            self.current_task = TaskData(task_id)

            # Zde se připraví text – počítá se jen jednou
            if self.current_task.text.strip():
                self.prepare_task_text(self.current_task.text)

            # body 2D/3D se inicializují až pokud ještě nejsou
            self._ensure_grids_initialized(task_id)

            # --- Tutorial: předvyplněné user_connections ---
            if self.current_task.task_type == "tutorial":
                tutorial_connections = {
                    "0.7": [(self.points[6], self.points[8])],  # přední dolní hrana
                    "0.8": [(self.points[24], self.points[26])],  # zadní dolní hrana
                    "0.10": [(self.points[13], self.points[13])],
                    # případně další tutorialy s vlastním nastavením
                }
                # pokud má tutorial definované spojení
                if self.current_task.task_id in tutorial_connections:
                    self.user_connections = [
                        Connection3D(a, b, dashed=False) for a, b in tutorial_connections[self.current_task.task_id]
                    ]

    def _ensure_grids_initialized(self, task_id):
        """Inicializuje 3D a 2D gridy pouze jednou."""
        if not self.points:
            if task_id == "0.1":
                self.points = grid_3d.create_3d_points(in_middle=True)
            else:
                self.points = grid_3d.create_3d_points()

        if not self.p_points:
            self.p_points, self.n_points, self.b_points = grid_2d.create_all_2d_points()

    def _draw_2d_grids(self, screen, task, mouse_pos, player_name):
        """Vykreslí všechny 2D pohledy (půdorys, nárys, bokorys)."""
        green = glob_var.GREEN
        blue = glob_var.BLUE
        red = glob_var.RED
        p_color = n_color = b_color = (255, 255, 255)

        l_square_length = grid_2d.count_square_length()
        p_pos, n_pos, b_pos = grid_2d.find_left_upper_corners(l_square_length)

        if task.task_type != "tutorial":
            self.draw_pop_up_buttons(screen, p_pos, n_pos, b_pos, l_square_length)

        # Napárování spojů z TaskData → reálné body
        p_conns = self._map_connections_to_points_2d(task.pudorys_connections, self.p_points)
        n_conns = self._map_connections_to_points_2d(task.narys_connections, self.n_points)
        b_conns = self._map_connections_to_points_2d(task.bokorys_connections, self.b_points)

        if task.task_id == "0.2":
            n_color = green
        elif task.task_id == "0.3":
            p_color = blue
        elif task.task_id == "0.4":
            b_color = red

        grids = [
            ("Půdorys", p_pos, self.p_points, p_conns, "p", p_color),
            ("Nárys", n_pos, self.n_points, n_conns, "n", n_color),
            ("Bokorys", b_pos, self.b_points, b_conns, "b", b_color),
        ]

        for title, pos, points, conns, grid_key, color in grids:
            if task.task_type == "2D_to_3D" or (
                    (task.task_type == "tutorial") and (
                    task.task_id in ("0.5", "0.6", "0.9", "0.7", "0.8", "0.10", "0.2", "0.3", "0.4"))):
                grid_2d.draw_task(screen, pos, l_square_length, title, conns, points,
                                  mouse_pos=None, gridpoints_enabled=False, connections_color=color,
                                  connections_width=glob_var.LINE_WIDTH)
            else:  # 3D_to_2D
                grid_2d.draw_task(screen, pos, l_square_length, title, [], points, mouse_pos=mouse_pos,
                                  gridpoints_enabled=(self.active_grid in (None, grid_key)),
                                  connections_width=glob_var.LINE_WIDTH)

        if (task.task_type == "3D_to_2D") and (player_name == "admin") and (self.loaded == False):
            self.user_pudorys_connections = p_conns
            self.user_narys_connections = n_conns
            self.user_bokorys_connections = b_conns
            self.loaded = True


    def _draw_3d_part(self, screen, task, mouse_pos, player_name):
        """Vykreslí 3D mřížku a případně i řešení."""

        show_active_grid = (
                task.task_type == "2D_to_3D" or
                (task.task_type == "tutorial" and task.task_id in ("0.5", "0.6", "0.9", "0.7", "0.8", "0.10"))
        )

        conns = self._map_connections_to_points_3d(task.connections_3d, self.points)

        if show_active_grid:
            grid_3d.draw_3d_grid(screen, self.points, mouse_pos)
            if (player_name == "admin") and (self.loaded == False):
                self.user_connections = conns
                self.loaded = True
        else:
            grid_3d.draw_3d_grid(screen, self.points, gridpoints_enabled=False)
            grid_3d.draw_connections(conns, screen, line_width=glob_var.LINE_WIDTH)

        # barevné zvýraznění řešení
        color_map = {
            "0.2": glob_var.GREEN,
            "0.3": glob_var.BLUE,
            "0.4": glob_var.RED,
        }

        if task.task_id in color_map and task.unpacked_data3d[1] and len(task.unpacked_data3d[1]) > 1:
            conns = self._map_connections_to_points_3d(task.unpacked_data3d[1], self.points)
            grid_3d.draw_connections(conns, screen, line_color=color_map[task.task_id], line_width=glob_var.LINE_WIDTH)

    def _draw_separator_and_text(self, screen):
        """Vykreslí oddělovací čáru a předpočítaný text zadání."""
        y = self.line_y
        pygame.draw.line(screen, (100, 100, 100), (0, y), (glob_var.SCREEN_WIDTH, y), 2)

        if self.task_text_surfaces:
            self.draw_task_text(screen)

    def _check_and_draw_solution(self, screen, task):
        """
        Zkontroluje řešení, nastaví styl a vykreslí uživatelská spojení.

        Returns:
            bool: True pokud je řešení správné
        """
        resolved = False
        color = (255, 255, 255)
        width = int(glob_var.LINE_WIDTH)

        if (task.task_type == "tutorial") and (task.task_id in ("0.1", "0.2", "0.3", "0.4")):
            resolved = True

        if task.task_type == "2D_to_3D" or (
                (task.task_type == "tutorial") and (task.task_id in ("0.5", "0.6", "0.9", "0.7", "0.8", "0.10"))):
            if grid_fun.check_3d_solution(self.user_connections, task.unpacked_data3d):
                resolved = True

            if resolved:
                color = (255, 215, 0)
                self.just_resolved = True
                width = int(glob_var.LINE_SOLUTION_WIDTH)
            grid_3d.draw_connections(self.user_connections, screen, color, width)

        elif task.task_type == "3D_to_2D":
            pudorys_ok = grid_fun.check_2d_solution(self.user_pudorys_connections, task.pudorys_connections)
            narys_ok = grid_fun.check_2d_solution(self.user_narys_connections, task.narys_connections)
            bokorys_ok = grid_fun.check_2d_solution(self.user_bokorys_connections, task.bokorys_connections)

            resolved = pudorys_ok and narys_ok and bokorys_ok

            if resolved:
                color = (255, 215, 0)
                self.just_resolved = True
                width = int(glob_var.LINE_SOLUTION_WIDTH)

            grid_2d.draw_lines_from_connections(screen, self.user_pudorys_connections, color, width)
            grid_2d.draw_lines_from_connections(screen, self.user_narys_connections, color, width)
            grid_2d.draw_lines_from_connections(screen, self.user_bokorys_connections, color, width)

        return resolved

    # ------------------------
    # Vykreslení úlohy
    # ------------------------
    def draw(self, screen, task_id, was_resolved=False, player_name=""):
        """
        Vykreslí úkol na obrazovku.

        Returns:
            bool: True pokud je úkol vyřešen během tohoto vykreslení
        """
        self._ensure_task_loaded(task_id)

        task = self.current_task
        screen.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()

        if not (task.task_type == "tutorial" and task.task_id == "0.1"):
            self._draw_2d_grids(screen, task, mouse_pos, player_name)
        self._draw_3d_part(screen, task, mouse_pos, player_name)
        self._draw_separator_and_text(screen)

        resolved = self._check_and_draw_solution(screen, task)

        self.draw_buttons(
            screen,
            task,
            was_resolved=was_resolved,
            is_currently_resolved=resolved
        )
        self.draw_home_button(screen)
        if task_id not in ("0.1", "0.2", "0.3", "0.4"):
            self.draw_pop_up_draw_button(screen)
            if task_id not in ("0.7", "0.8", "0.10"):
                self.draw_clean_button(screen, task)
        self._draw_id(screen, task, was_resolved, resolved)
        self._draw_arrow(screen, task)

        self.draw_pop_up_windows(screen, task)
        self.draw_pop_up_draw_window(screen, task)

        return resolved

