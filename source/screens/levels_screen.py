# -*- coding: utf-8 -*-
"""
levels_screen.py
----------------

Obrazovka výběru jednotlivých levelů pro hru Cubiq🧊.

Třída LevelsScreen umožňuje:
    • vytvořit tlačítka pro jednotlivé levely,
    • nastavit jejich stav (aktivní / neaktivní) podle pokroku hráče,
    • zpracovávat události myši a kolečka (scrollování),
    • vykreslit obrazovku s názvy kapitol a tlačítky.
"""

import glob_var
import pygame
from elements.button import Button


class LevelsScreen:
    """
    Obrazovka výběru úrovní pro hru Cubiq.

    Tato třída spravuje:
        - seznam tlačítek pro jednotlivé levely
        - stav tlačítek (dostupné / dokončené / uzamčené)
        - scrollování a kliknutí
        - vykreslení obrazovky s nadpisy kapitol a tlačítky
    """

    def __init__(self, player_progress, level_data):
        """
        Inicializuje obrazovku úrovní.

        Args:
            player_progress: instance PlayerProgress pro kontrolu pokroku hráče
            level_data: instance LevelData obsahující seznam kapitol a levelů
        """
        # Správa hráčů a jejich pokroku
        self.player_progress = player_progress

        # Načtení dat o kapitolách a levelech
        self.level_data = level_data
        self.chapters: list[dict] = self.level_data.get_chapters()

        self.x_offset = glob_var.X_OFFSET
        self.button_height = glob_var.BTN_HEIGHT * 1.05

        # Seznam tlačítek a stav inicializace
        self.buttons: list[Button] = []
        self.initialized: bool = False

        # Posun obrazovky (scroll)
        self.scroll_y: int = 0
        self.max_scroll: int = 0

        # seznam startovacích pozic kapitol
        self.chapter_positions: list[tuple[int, int]] = []

        # Horní bar
        self.top_bar_height = 130
        btn_add_width = btn_add_height = self.button_height
        self.btn_add = Button(glob_var.SCREEN_WIDTH - btn_add_width - self.x_offset,
                              (self.top_bar_height - btn_add_height) // 2,
                              btn_add_width, btn_add_height, "+")

    # ------------------------
    # "namapování" levlů na skutečné Buttons objekty
    # ------------------------
    def update_buttons(self, player_name: str):
        """
        Aktualizuje stav tlačítek podle dokončených levelů a aktuální dostupnosti.

        Args:
            player_name: jméno hráče, jehož pokrok se kontroluje
        """
        player_data = self.player_progress.get_player(player_name)
        completed_levels: list[str] = player_data.get("completed_levels", [])

        # první nevyřešené levely v každé kapitole
        current_levels: list[str] = []
        for chapter in self.chapters:
            for level in chapter["levels"]:
                if level not in completed_levels:
                    current_levels.append(level)
                    break

        # aktualizace tlačítek
        for button in self.buttons:
            if button.get_text() in completed_levels:
                button.enable()
                button.change_color(text_color=(255, 215, 0), border_color=(255, 215, 0))
            elif button.get_text() in current_levels:
                button.enable()
            else:
                button.disable()

    def initialize_buttons(self, player_name: str):
        """
        Vytvoří tlačítka pro všechny levely a určí jejich počáteční pozice.
        Odstraní btn_add pokud player_name není "admin".

        Args:
            player_name: jméno přihlášeného hráče (pro určení dostupných levelů)
        """
        if player_name != "admin":
            self.btn_add.disable()

        self.buttons.clear()

        # Rozměry tlačítek a vzdálenosti
        button_width = button_height = self.button_height
        spacing_x = 30
        spacing_y = 30
        chapter_spacing = 90
        min_x_offset = self.x_offset
        start_y = self.top_bar_height + chapter_spacing

        # maximální počet tlačítek v řádku
        max_per_row = (glob_var.SCREEN_WIDTH - 2 * min_x_offset + spacing_x) // (button_width + spacing_x)
        x_offset = (glob_var.SCREEN_WIDTH - (max_per_row * (button_width + spacing_x) - spacing_x)) / 2

        for chapter_index, chapter in enumerate(self.chapters):
            chapter_start_y = start_y
            self.chapter_positions.append((chapter_index, chapter_start_y))

            levels = chapter["levels"]
            level_count = len(levels)

            for row_start in range(0, level_count, int(max_per_row)):
                row_level_count = min(max_per_row, level_count - row_start)
                row_index = row_start // max_per_row
                y = chapter_start_y + row_index * (button_height + spacing_y)

                for i in range(int(row_level_count)):
                    x = x_offset + i * (button_width + spacing_x)
                    label = levels[row_start + i]
                    self.buttons.append(Button(x, y, button_width, button_height, label))

            # posun start_y na další kapitolu
            start_y = y + button_height + chapter_spacing

        self.initialized = True

        # maximální posun = celková výška obsahu - výška obrazovky
        total_height = max(button.get_bottom() for button in self.buttons) + 50
        visible_height = glob_var.SCREEN_HEIGHT - self.top_bar_height
        self.max_scroll = max(0, total_height - visible_height)

        # inicializace stavu tlačítek podle pokroku hráče
        self.update_buttons(player_name)

    # ============================================
    # Události myši a klávesnice
    # ============================================
    def handle_events(self, events: list, player_name: str) -> str | None:
        """
        Zpracuje kliknutí uživatele a scrollování.

        Args:
            events: seznam událostí z pygame.event.get()
            player_name: jméno přihlášeného hráče

        Returns:
            str | None: označení vybraného levelu ("0.1", "1.3" ...) nebo None nebo "+" (pravé horní tlačítko)
        """
        if not self.initialized:
            self.initialize_buttons(player_name)

        selected_level: str | None = None
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and event.button == 1:
                if self.btn_add.click(event):
                    return "+"
                for button in self.buttons:
                    if button.click(event):
                        selected_level = button.get_text()
                        break

            elif event.type == pygame.MOUSEWHEEL:
                mouse_y = pygame.mouse.get_pos()[1]

                # scroll jen pokud je kurzor pod horním bannerem
                if mouse_y > self.top_bar_height:
                    dy = event.y * 30
                    new_scroll = self.scroll_y + dy
                    new_scroll = max(min(new_scroll, 0), -self.max_scroll)

                    delta = new_scroll - self.scroll_y
                    self.scroll_y = new_scroll

                    for button in self.buttons:
                        button.scroll(delta)

        return selected_level

    # ------------------------
    # Vykreslení celé obrazovky
    # ------------------------
    def draw(self, screen: pygame.Surface, player_name: str):
        """
        Vykreslí obrazovku výběru levelů s nadpisy kapitol a tlačítky.

        Args:
            screen: pygame.Surface, na který se kreslí
            player_name: jméno hráče (pro případný nadpis)
        """
        screen.fill((0, 0, 0))

        # --- vykreslení nadpisů kapitol pod horním barem ---
        chapter_font = glob_var.FONT
        for idx, start_y in self.chapter_positions:
            chapter = self.chapters[idx]
            title_surface = chapter_font.render(chapter["title"], True, (255, 255, 255))
            screen.blit(title_surface, (self.x_offset, start_y - self.button_height + 10 + self.scroll_y))

        # --- vykreslení tlačítek ---
        for button in self.buttons:
            button.draw(screen)

        # --- horní bar ---
        bar_color = (0, 0, 0)  # tmavě šedá / černá
        pygame.draw.rect(screen, bar_color, pygame.Rect(0, 0, glob_var.SCREEN_WIDTH, self.top_bar_height))
        # spodní oddělovací čára
        pygame.draw.line(screen, (255, 255, 255), (0, self.top_bar_height),
                         (glob_var.SCREEN_WIDTH, self.top_bar_height), 2)

        # jméno uživatele vlevo
        font = glob_var.FONT

        label = font.render("Jste přihlášený jako:", True, (180, 180, 180))
        name = font.render(player_name, True, (255, 255, 255))
        screen.blit(label, (self.x_offset, (self.top_bar_height - name.get_height()) // 2))
        screen.blit(name, (self.x_offset + label.get_width() + 10, (self.top_bar_height - name.get_height()) // 2))

        # tlačítko "+" vpravo
        if player_name == "admin":
            self.btn_add.draw(screen)
