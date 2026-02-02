# -*- coding: utf-8 -*-
"""
start_screen.py
---------------

Startovací obrazovka hry Cubiq🧊

Obsahuje:
    • InputBox pro zadání jména hráče
    • Tlačítko Start pro potvrzení jména
    • Zpracování událostí myši a klávesnice
    • Vykreslování startovací obrazovky.
"""

import glob_var
import pygame
from elements.button import Button
from elements.input_box import InputBox


class StartScreen:
    """
    Obrazovka startu hry Cubiq.

    Obsahuje tlačítko Start a InputBox pro zadání jména hráče.
    """

    def __init__(self, player_progress):
        """
        Inicializuje startovací tlačítko a nastaví prázdný řetězec pro jméno hráče.

        Args:
            player_progress: instance třídy správy hráčů a jejich pokroku
        """
        # správa hráčů a jejich pokroku
        self.player_progress = player_progress

        # tlačítko Start
        start_button_width = 200
        start_button_height = glob_var.BTN_HEIGHT
        x_start_button = (glob_var.SCREEN_WIDTH - start_button_width) // 2
        y_start_button = ((glob_var.SCREEN_HEIGHT - start_button_height) // 2) + (glob_var.SCREEN_HEIGHT // 4)
        self.start_button = Button(x_start_button, y_start_button,
                                   start_button_width, start_button_height, "Přihlásit se")

        # input box pro jméno hráče
        input_width = 400
        input_height = (2/3)*glob_var.BTN_HEIGHT
        x_input = (glob_var.SCREEN_WIDTH - input_width) // 2
        y_input = (glob_var.SCREEN_HEIGHT // 2) - input_height
        self.input_box = InputBox(x_input, y_input, input_width, input_height)

        # jméno hráče, bude zadáno přes InputBox
        self.player_name = ""

        # časovač pro blikání kurzoru v InputBoxu
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(120)  # ms od posledního frame

    # ============================================
    # Události myši a klávesnice
    # ============================================
    def handle_events(self, events):
        """
        Zpracuje všechny události myši a klávesnice.

        Args:
            events (list): seznam událostí z pygame.event.get()

        Returns:
            tuple (clicked, player_name):
                clicked (bool): zda se kliklo na tlačítko Start a nebo enter při zadávání uživatelského jména
                player_name (str): jméno z InputBoxu
        """
        start_clicked = False
        for event in events:
            # zpracování kláves v InputBoxu, vrátí True pokud byl stisknut Enter
            enter_pressed = self.input_box.handle_event(event)

            # kliknutí na tlačítko Start
            if self.start_button.click(event) or enter_pressed:
                self.player_name = self.input_box.get_text().strip()
                if self.player_name:
                    # přidání nového hráče nebo načtení existujícího
                    self.player_progress.add_player(self.player_name)
                start_clicked = True

        return start_clicked, self.player_name

    # ------------------------
    # updata InputBoxu
    # ------------------------
    def update(self):
        """Aktualizace InputBoxu a tlačítka Start."""
        self.input_box.update(self.dt)

        # tlačítko se aktivuje jen pokud je v input boxu alespoň jeden znak
        player_name = self.input_box.get_text().strip()
        if player_name:
            self.start_button.enable()
        else:
            self.start_button.disable()

    # ------------------------
    # Vykreslení "startovací" obrazovky
    # ------------------------
    def draw(self, screen):
        """
        Vykreslí startovací obrazovku.
        """
        screen.fill((0, 0, 0))

        # input box
        self.input_box.update(self.dt)
        self.input_box.draw(screen)
        self.input_box.draw_label(screen, "Zadejte své uživatelské jméno")

        # tlačítko
        self.start_button.draw(screen)
