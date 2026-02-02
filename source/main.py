# -*- coding: utf-8 -*-  (české znaky)
"""
Cubiq🧊 – hlavní aplikační modul
---------------------------------
Soubor: main.py
Autor: Beáta Havelková
Datum poslední úpravy:  2025-10-19

Popis:
    Tento modul obsahuje hlavní třídu `App`, která zajišťuje:
        • Inicializaci Pygame a herního okna
        • Inicializace pomocných tříd a tříd obrazovek
        • Správu obrazovek (Start, Levels, Task)
        • Načítání a ukládání pokroku hráče
        • Řízení hlavního herního cyklu
"""

import sys

import glob_var
import pygame
from elements.level_data import LevelData
from elements.players_progress import PlayerProgress
from screens.edit_question_screen import EditQuestionScreen
from screens.levels_screen import LevelsScreen
from screens.start_screen import StartScreen
from screens.task_screen import TaskScreen
from screens.edit_screen import EditScreen
from utils.data_creating_fun import create_empty_task
from utils.initiating_length import initiate_length


class App:
    """Hlavní třída hry Cubiq – zajišťuje běh aplikace a přepínání obrazovek."""

    def __init__(self):
        """Inicializace Pygame, obrazovek a základního stavu hry."""
        # ----------------------------
        # Inicializace Pygame
        # ----------------------------
        pygame.init()

        info = pygame.display.Info()
        initiate_length(info)

        self.screen = pygame.display.set_mode((glob_var.SCREEN_WIDTH, glob_var.SCREEN_HEIGHT))
        pygame.display.set_caption("Cubiq🧊")
        self.clock = pygame.time.Clock()

        # ----------------------------
        # Inicializace pomocných tříd
        # ----------------------------
        self.player_progress = PlayerProgress()
        self.level_data = LevelData()

        # ----------------------------
        # Vytvoření instancí obrazovek
        # ----------------------------
        self.start_screen = StartScreen(self.player_progress)
        self.levels_screen = LevelsScreen(self.player_progress, self.level_data)
        self.task_screen = TaskScreen(self.level_data)
        self.edit_question_screen = EditQuestionScreen()
        self.edit_screen = EditScreen(self.level_data)

        # ----------------------------
        # Proměnné pro řízení hry
        # ----------------------------
        self.current_screen = "start"
        self.selected_level = None
        self.player_name = None
        self.running = True

    def _update_data(self):
        self.level_data.update()
        self.levels_screen = LevelsScreen(self.player_progress, self.level_data)
        self.task_screen = TaskScreen(self.level_data)

    def run(self):
        """Spustí hlavní herní smyčku - zajišťuje přepínání obrazovek."""
        while self.running:
            events = pygame.event.get()

            # ------------------------
            # Globální události (ukončení)
            # ------------------------
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # ------------------------
            # OBRAZOVKA: START
            # ------------------------
            if self.current_screen == "start":
                start_clicked, player_name = self.start_screen.handle_events(events)
                self.start_screen.update()
                self.start_screen.draw(self.screen)

                if start_clicked:
                    self.player_name = player_name
                    if self.player_name == "admin":
                        for level in self.level_data.get_all_levels():
                            self.player_progress.update_player_level(self.player_name, level)
                            self.player_progress.save_progress()
                    self.player_progress.add_player(self.player_name)
                    self.current_screen = "levels"

            # ------------------------
            # OBRAZOVKA: LEVELS
            # ------------------------
            elif self.current_screen == "levels":
                level_clicked = self.levels_screen.handle_events(events, self.player_name)
                self.levels_screen.draw(self.screen, self.player_name)

                if level_clicked is not None:
                    if level_clicked == "+":
                        self.current_screen = "edit_question"
                    else:
                        self.selected_level = level_clicked
                        self.task_screen.reset_task()
                        self.current_screen = "task"

            # ------------------------
            # OBRAZOVKA: TASK
            # ------------------------
            elif self.current_screen == "task":
                escape_pressed, new_task_id = self.task_screen.handle_events(events)

                # Přepnutí na novou úlohu
                if new_task_id != "":
                    self.selected_level = new_task_id
                    self.task_screen.reset_task()

                # Kontrola, zda level už byl vyřešen
                player_data = self.player_progress.get_player(self.player_name)
                was_resolved = str(self.selected_level) in map(str, player_data["completed_levels"])

                # Vykreslení úlohy
                resolved = self.task_screen.draw(
                    self.screen,
                    self.selected_level,
                    was_resolved=was_resolved,
                    player_name=self.player_name
                )

                # Uložení pokroku po dokončení
                if resolved:
                    self.player_progress.update_player_level(self.player_name, self.selected_level)
                    self.player_progress.save_progress()

                # Návrat na obrazovku LEVELS
                if escape_pressed:
                    self.selected_level = None
                    self.player_progress.load_progress()
                    self.levels_screen.update_buttons(self.player_name)
                    self.current_screen = "levels"

            # ------------------------
            # OBRAZOVKA: EDIT QUESTION
            # ------------------------
            elif self.current_screen == "edit_question":
                self.edit_question_screen.draw(self.screen, self.level_data)
                new_level_id, escape_pressed = self.edit_question_screen.handle_events(events, self.level_data)
                # Pokud stiskl Escape → návrat na Levels
                if escape_pressed:
                    self.current_screen = "levels"
                # Pokud uživatel něco zadal (neprázdný text)
                if new_level_id:
                    if new_level_id not in self.level_data.get_all_levels():
                        create_empty_task(new_level_id)
                        self._update_data()
                        if self.player_name == "admin":
                            self.player_progress.update_player_level(self.player_name, new_level_id)
                            self.player_progress.save_progress()
                    self.selected_level = new_level_id
                    self.current_screen = "edit"

            # ------------------------
            # OBRAZOVKA: EDIT QUESTION
            # ------------------------
            elif self.current_screen == "edit":
                self.edit_screen.draw(self.screen, self.selected_level)
                escape_pressed = self.edit_screen.handle_events(events)
                if escape_pressed:
                    self._update_data()
                    self.current_screen = "edit_question"

            # ------------------------
            # Aktualizace obrazovky
            # ------------------------
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# ======================================================================
# Spouštěcí sekce
# ======================================================================
if __name__ == "__main__":
    App().run()
