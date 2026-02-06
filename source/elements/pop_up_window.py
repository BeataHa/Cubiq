# -*- coding: utf-8 -*-
"""
pop_up_window.py
----------------

Třída pro interaktivní vyskakovací okno (PopUp) v aplikaci Cubiq🧊.

Obsahuje:
    • zobrazení textu s automatickým zalomením a paddingem,
    • dynamické přizpůsobení velikosti okna dle obsahu,
    • tlačítko OK pro zavření okna,
    • metody pro nastavení textu a pozice okna,
    • vykreslování pozadí, okraje, textu a tlačítka,
    • zpracování kliknutí na tlačítko.
"""

import pygame
import glob_var
from elements.button import Button


class PopUpWindow:
    def __init__(
            self,
            x: int,
            y: int,
            text: str = ""
    ):
        # výchozí padding a barvy z glob_var
        self.padding = glob_var.POP_UP_FONT_SIZE // 3
        self.line_spacing = glob_var.POP_UP_FONT_SIZE // 5

        # font
        self.font_name = glob_var.FONT_NAME
        self.base_font_size = glob_var.POP_UP_FONT_SIZE
        self.font = pygame.font.SysFont(self.font_name, self.base_font_size)

        # pozadí a barvy
        self.bg_color = (15, 15, 15)
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)

        # text a vykreslené řádky
        self.text = text
        self._rendered_lines = []

        # tlačítko OK
        self.ok_button = Button(0, 0, glob_var.BTN_HEIGHT, glob_var.BTN_HEIGHT // 2, "OK",
                                border_radius=5)

        # inicializace pozice
        self.rect = pygame.Rect(x, y, 0, 0)
        self.visible = False

        self._update_text()
        self._update_ok_position()

    # -----------------------------------------------------
    def set_text(self, text: str):
        self.text = text
        self._update_text()

    def set_xy(self, x: int, y: int):
        self.rect.topleft = (x, y)
        self._update_ok_position()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    # -----------------------------------------------------
    def _update_text(self):
        """Zalomí text a upraví velikost okna podle obsahu, nepřekrývá tlačítko OK."""
        max_line_width = 0
        self._rendered_lines.clear()

        # zalomení textu
        for paragraph in self.text.split("\n"):
            words = paragraph.split(" ")
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                line_width, _ = self.font.size(test_line)
                if line_width <= glob_var.SCREEN_WIDTH // 2:
                    line = test_line
                else:
                    rendered = self.font.render(line, True, self.text_color)
                    self._rendered_lines.append(rendered)
                    max_line_width = max(max_line_width, rendered.get_width())
                    line = word
            if line:
                rendered = self.font.render(line, True, self.text_color)
                self._rendered_lines.append(rendered)
                max_line_width = max(max_line_width, rendered.get_width())

        # nastavíme velikost okna podle textu + padding + tlačítko OK
        total_height = len(self._rendered_lines) * (self.font.get_height() + self.line_spacing) \
                       + 2 * self.padding + self.ok_button.get_height() + self.line_spacing
        total_width = max_line_width + 2 * self.padding

        self.rect.width = total_width
        self.rect.height = total_height

        # tlačítko OK
        self.ok_button.change_font(self.font)
        self._update_ok_position()

    # -----------------------------------------------------
    def _update_ok_position(self):
        """Nastaví tlačítko OK dole uprostřed okna."""
        # horizontálně vycentrovat
        self.ok_button.set_x(self.rect.x + (self.rect.width - self.ok_button.get_width()) // 2)

        # svisle odspodu
        self.ok_button.set_y(self.rect.y + self.rect.height - self.padding - self.ok_button.get_height())

    # -----------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        # pozadí
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)

        # text
        y_offset = self.rect.y + self.padding
        for line_surf in self._rendered_lines:
            surface.blit(line_surf, (self.rect.x + self.padding, y_offset))
            y_offset += line_surf.get_height() + self.line_spacing

        # tlačítko OK
        self.ok_button.draw(surface)

    # -----------------------------------------------------
    def handle_event(self, event):
        if not self.visible:
            return
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (
                event.type == pygame.MOUSEBUTTONUP and event.button == 1):
            if self.ok_button.click(event):
                self.hide()

