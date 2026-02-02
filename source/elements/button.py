# -*- coding: utf-8 -*-
"""
button.py
---------

Třída pro tvorbu a správu tlačítek v aplikaci Cubiq🧊.

Funkce třídy Button:
    • vykreslení tlačítka s textem,
    • změna barvy při najetí myší,
    • detekce kliknutí myší,
    • vertikální posun tlačítka (scroll)
    • změnu barvy tlačítka,
    • aktivace a deaktivace tlačítka,
    • vrácení šířky, výšky, dolního y, textu,
    • přenastavení souřadnic.
"""

import glob_var
import pygame

pygame.init()


class Button:
    """
    Grafické tlačítko pro uživatelské rozhraní.

    Attributes:
        rect (pygame.Rect): pozice a velikost tlačítka
        text (str): text zobrazený na tlačítku
        default_color (tuple): výchozí barva tlačítka
        hover_color (tuple): barva při najetí myší
        disabled_color (tuple): barva pro neaktivní tlačítko
        text_color (tuple): barva textu
        border_color (tuple): barva obrysu
        border_width (int): šířka obrysu
        border_radius (int): zaoblení rohů
        font (pygame.font.Font): font pro text
        clicked_inside (bool): zda bylo kliknutí iniciováno uvnitř tlačítka
        enabled (bool): zda je tlačítko aktivní
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color=(0, 0, 0), text_color=(255, 255, 255),
                 border_color=(255, 255, 255), border_width=2,
                 border_radius=12, enabled=True):
        """
        Inicializuje tlačítko.

        Args:
            x (int): levý horní roh X
            y (int): levý horní roh Y
            width (int): šířka tlačítka
            height (int): výška tlačítka
            text (str): text zobrazený na tlačítku
            color (tuple, optional): barva tlačítka
            text_color (tuple, optional): barva textu
            border_color (tuple, optional): barva obrysu
            border_width (int, optional): šířka obrysu
            border_radius (int, optional): zaoblení rohů
            enabled (bool, optional): zda je tlačítko aktivní
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.default_color = color
        self.hover_color = (50, 50, 50)
        self.disabled_color = (120, 120, 120)
        self.current_color = self.default_color
        self.text_color = text_color
        self.current_text_color = text_color
        self.border_color = border_color
        self.current_border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.font = glob_var.FONT
        self.clicked_inside = False
        self.enabled = enabled

    def __str__(self) -> str:
        """
        Vrátí textovou reprezentaci tlačítka.

        Returns:
            str: popis tlačítka a jeho pozice
        """
        return f"Tlačítko: '{self.text}' na pozici {self.rect.topleft}"

    def draw(self, screen: pygame.Surface):
        """
        Vykreslí tlačítko na obrazovku.

        Args:
            screen (pygame.Surface): surface, kam se tlačítko vykreslí
        """
        if not self.enabled:
            self.current_text_color = self.disabled_color
            self.current_border_color = self.disabled_color
            self.current_color = self.default_color
        else:
            self.current_text_color = self.text_color
            self.current_border_color = self.border_color
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.current_color = self.hover_color
            else:
                self.current_color = self.default_color

        pygame.draw.rect(screen, self.current_border_color, self.rect, border_radius=self.border_radius)
        inner_rect = self.rect.inflate(-self.border_width * 2, -self.border_width * 2)
        pygame.draw.rect(screen, self.current_color, inner_rect, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.current_text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def click(self, event: pygame.event.Event) -> bool:
        """
        Detekuje kliknutí na tlačítko.

        Args:
            event (pygame.event.Event): událost pygame

        Returns:
            bool: True, pokud je tlačítko aktivní a bylo kliknuto
        """
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked_inside = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked_inside and self.rect.collidepoint(event.pos):
                self.clicked_inside = False
                return True
            self.clicked_inside = False
        return False

    def scroll(self, dy: int):
        """
        Posune tlačítko vertikálně.

        Args:
            dy (int): posun v pixelech
        """
        self.rect.y += dy

    def change_color(self, text_color=None, border_color=None):
        """
        Změní barvu textu a obrysu tlačítka.

        Args:
            text_color (tuple, optional): nová barva textu (RGB); default je aktuální self.text_color
            border_color (tuple, optional): nová barva obrysu (RGB); default je aktuální self.border_color
        """
        if text_color is None:
            text_color = self.text_color
        if border_color is None:
            border_color = self.border_color

        self.text_color = text_color
        self.border_color = border_color

    def enable(self):
        """Aktivuje tlačítko."""
        self.enabled = True

    def disable(self):
        """Deaktivuje tlačítko."""
        self.enabled = False

    def get_text(self) -> str:
        """Vrátí text tlačítka."""
        return self.text

    def get_bottom(self) -> int:
        """Vrátí spodní y tlačítka."""
        return self.rect.bottom

    def get_height(self) -> int:
        """Vrátí výšku tlačítka."""
        return self.rect.height

    def get_width(self) -> int:
        """Vrátí šířku tlačítka."""
        return self.rect.width

    def set_x(self, x):
        """Přenastaví x souřadnici tlačítka."""
        self.rect.x = x

    def set_y(self, y):
        """Přenastaví y souřadnici tlačítka."""
        self.rect.y = y

    def change_font(self, font):
        self.font = font