# -*- coding: utf-8 -*-
"""
edit_question_screen.py
--------------------------------------

Prvotní stránka editoru Cubiq🧊 pro zadání ID příkladu s tlačítkem Button.

Obsahuje třídu EditQuestionScreen, která:
    • zobrazuje InputBox pro zadání ID příkladu s textovým popiskem,
    • umožňuje zadání pouze validního ID (formát x.y a kontrola existujících levelů),
    • aktivuje tlačítko Načíst/Vytvořit pouze pro validní ID,
    • detekuje stisky Enter a Escape, Backspace a běžné psaní,
    • blikající kurzor a návrat zadaného textu uživatelem.
"""

import pygame
import glob_var
from elements.input_box import InputBox
from elements.button import Button


class EditQuestionScreen:
    """
    Prvotní stránka editoru pro zadání ID příkladu s tlačítkem Button.

    Attributes:
        input_box (InputBox): pole pro zadání ID
        btn_load (Button): tlačítko Načíst/Vytvořit
        running (bool): zda je stránka aktivní
        enter_pressed (bool): zda uživatel stiskl Enter nebo tlačítko
        result_text (str): text zadaný uživatelem
        clock (pygame.time.Clock): časovač pro blikání kurzoru
    """

    def __init__(self):
        """Inicializuje editor, vytvoří input box a tlačítko uprostřed obrazovky."""
        self.running = True
        self.enter_pressed = False
        self.result_text = ""

        # Rozměry input boxu
        box_width = 100
        box_height = (2 / 3) * glob_var.BTN_HEIGHT
        box_x = glob_var.SCREEN_WIDTH // 2 - box_width // 2
        box_y = glob_var.SCREEN_HEIGHT // 2 - box_height // 2
        self.input_box = InputBox(box_x, box_y, box_width, box_height, max_length=5)

        # Tlačítko Načíst/Vytvořit
        btn_width = 250
        btn_height = glob_var.BTN_HEIGHT
        btn_x = glob_var.SCREEN_WIDTH // 2 - btn_width // 2
        btn_y = box_y + box_height + 30
        self.btn_load = Button(btn_x, btn_y, btn_width, btn_height, "Načíst/Vytvořit")

        # časovač pro blikání kurzoru v InputBoxu
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(120)  # ms od posledního frame

    def is_valid_id(self, text: str, level_data) -> bool:
        """Validuje, zda text má formát x.y a existuje kapitola s x-1."""
        if text.count('.') != 1:
            return False

        x_str, y_str = text.split('.')

        # základní validace
        if (
                not x_str.isdigit()
                or not y_str.isdigit()
                or x_str.startswith("0")
                or y_str.startswith("0")
        ):
            return False

        all_levels = level_data.get_all_levels()
        if text in all_levels:
            return True

        x = int(x_str)
        prev_x = x - 1

        # existuje alespoň jeden level s x-1 ?
        return any(level.startswith(f"{prev_x}.") for level in all_levels)

    def handle_events(self, events, level_data) -> tuple[str, bool]:
        """
        Zpracuje události pygame.

        • Escape → ukončí editor
        • Enter / klik na tlačítko → uloží text (pokud je validní)
        • psaní / backspace → řeší input_box

        Returns:
            tuple[str, bool]: text zadaný uživatelem a zda byl stisknut Escape
        """
        escape_pressed = False
        self.result_text = ""
        self.enter_pressed = False

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                escape_pressed = True

            # input box (Enter, psaní, backspace)
            elif self.input_box.handle_event(event):
                if self.is_valid_id(self.input_box.get_text(), level_data):
                    self.enter_pressed = True
                    self.result_text = self.input_box.get_text()

            # tlačítko Načíst / Vytvořit
            if self.btn_load.click(event):
                if self.is_valid_id(self.input_box.get_text(), level_data):
                    self.enter_pressed = True
                    self.result_text = self.input_box.get_text()

        return self.result_text, escape_pressed

    def draw(self, screen: pygame.Surface, level_data):
        """
        Spustí hlavní smyčku editoru.

        Args:
            screen (pygame.Surface): surface, kam se vykresluje

        """
        self.input_box.update(self.dt)

        # --- vykreslení ---
        screen.fill((0, 0, 0))  # pozadí černé
        self.input_box.draw_label(screen, text="Zadejte ID příkladu ve formátu x.y")
        self.input_box.draw(screen)

        # Aktivace tlačítka jen pro validní ID
        if self.is_valid_id(self.input_box.get_text(), level_data):
            self.btn_load.enable()
        else:
            self.btn_load.disable()
        self.btn_load.draw(screen)

