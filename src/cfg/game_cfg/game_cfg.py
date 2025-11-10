# TODO: add colors here so they can be customized

import pygame
from dataclasses import dataclass


@dataclass
class GameConfig:
    fps: int = 60
    screen_width: int = 1200
    screen_height: int = 800

    def __post_init__(self):
        self.font_large = pygame.font.SysFont("Times New Roman", 32)
        self.font_medium = pygame.font.SysFont("Times New Roman", 24)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_tiny = pygame.font.SysFont("Arial", 16)
