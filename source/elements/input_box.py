# -*- coding: utf-8 -*-
"""
inpu_tbox.py
-----------

Třída pro zadávání textu uživatelem v aplikaci Cubiq🧊.

Obsahuje:
    • textové pole s pevnou velikostí,
    • detekci stisku kláves (včetně Enter a Backspace),
    • omezení délky vstupu,
    • blikající kurzor,
    • vykreslení textu, obdélníku a kurzoru,
    • volitelný popisek nad polem.
"""

import glob_var
import pygame

pygame.init()


class InputBox:
    """
    Reprezentuje zadávací textové pole.

    Attributes:
        rect (pygame.Rect): obdélník pole
        y (int): vertikální pozice pole
        width (int): šířka pole
        color (pygame.Color): barva textu a obrysu
        text (str): aktuální obsah pole
        font (pygame.font.Font): font textu
        txt_surface (pygame.Surface): vykreslený text
        active (bool): zda je pole aktivní
        cursor_visible (bool): viditelnost kurzoru
        cursor_timer (float): časovač blikání kurzoru
        cursor_interval (int): interval blikání kurzoru (ms)
        max_length (int): maximální délka textu
    """

    def __init__(self, x: int, y: int, w: int, h: int, text: str = '', active=True, max_length=30,
                 max_length_per_row=30):
        """
        Inicializuje zadávací pole.

        Args:
            x (int): X souřadnice levého horního rohu
            y (int): Y souřadnice levého horního rohu
            w (int): šířka pole
            h (int): výška pole
            text (str, optional): počáteční text
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.y = y
        self.width = w
        self.color = pygame.Color('white')
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = active
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500
        self.max_length = max_length
        self.mas_length_per_row = max_length_per_row

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Zpracuje klávesové události (Enter, Backspace, znaky).

        Args:
            event (pygame.event.Event): událost pygame

        Returns:
            bool: True, pokud uživatel stiskl Enter a text není prázdný
        """

        enter_pressed = False
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.text) > 0:
                    enter_pressed = True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, self.color)
        return enter_pressed

    def update(self, dt: float):
        """
        Aktualizuje stav kurzoru (blikání).

        Args:
            dt (float): čas od poslední aktualizace (ms)
        """
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def draw(self, screen: pygame.Surface):
        """
        Vykreslí text do InputBoxu.
        Pokud text přesáhne výšku boxu, automaticky zmenší font,
        aby se celý text vešel.
        """
        x_offset = 7
        y_offset = 5
        line_spacing = 2

        max_width = self.rect.width - 2 * x_offset
        max_height = self.rect.height - 2 * y_offset

        font_size = 36
        min_font_size = 14

        # -----------------------------
        # hledání vhodné velikosti fontu
        # -----------------------------
        while font_size >= min_font_size:
            font = pygame.font.Font(None, font_size)

            lines = []
            current_line = ""

            # ruční zalamování – BEZ strip()
            for char in self.text:
                test_line = current_line + char
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char

            if current_line or not lines:
                lines.append(current_line)

            total_height = (
                    len(lines) * font.get_height()
                    + (len(lines) - 1) * line_spacing
            )

            if total_height <= max_height:
                break

            font_size -= 1

        # -----------------------------
        # vertikální vycentrování
        # -----------------------------
        start_y = self.rect.y + (self.rect.height - total_height) // 2

        # -----------------------------
        # vykreslení textu
        # -----------------------------
        y = start_y
        for line in lines:
            surface = font.render(line, True, self.color)
            screen.blit(surface, (self.rect.x + x_offset, y))
            y += font.get_height() + line_spacing

        # -----------------------------
        # obrys InputBoxu
        # -----------------------------
        pygame.draw.rect(screen, self.color, self.rect, 2)

        # -----------------------------
        # kurzor – NEIGNORUJE MEZERY
        # -----------------------------
        if self.cursor_visible and self.active:
            last_line = lines[-1]

            cursor_x = (
                    self.rect.x
                    + x_offset
                    + font.size(last_line)[0]  # ← mezery započítány
            )

            cursor_y = (
                    start_y
                    + (len(lines) - 1) * (font.get_height() + line_spacing)
            )

            cursor_h = font.get_height()

            pygame.draw.line(
                screen,
                self.color,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + cursor_h),
                2
            )

    def draw_label(self, screen: pygame.Surface, text=""):
        """
        Vykreslí nadpis/popis textového pole.

        Args:
            screen (pygame.Surface): surface, kam se kreslí
        """
        label_offset = glob_var.BTN_HEIGHT
        font = glob_var.FONT
        title_surface = font.render(text, True, (255, 255, 255))
        screen.blit(title_surface,
                    (glob_var.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, self.y - label_offset))

    def get_text(self) -> str:
        """ Vrátí aktuální obsah pole. """
        return self.text

    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
