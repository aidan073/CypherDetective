# TODO: add colors here so they can be customized

import pygame
from dataclasses import dataclass


@dataclass
class GameConfig:
    fps: int = 60
    screen_width: int = 1200
    screen_height: int = 800

    def __post_init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
