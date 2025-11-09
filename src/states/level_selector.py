from src.enums.colors import Colors
from src.enums.game_states import GameState
from src.states.state_interface import StateInterface
from src.save_handler.save_system import is_level_unlocked
from src.cfg.levels_cfg import get_level, get_total_levels

import pygame

# For type hinting
from pygame.event import Event


class LevelSelectorState(StateInterface):
    def __init__(self, game):
        self.game = game

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.update_state(GameState.MENU)
            elif event.key in [
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
                pygame.K_4,
                pygame.K_5,
            ]:
                level_num = int(event.unicode)
                if is_level_unlocked(level_num):
                    self.start_level(level_num)
                    self.game.update_state(GameState.GAMEPLAY)

    def render(self):
        """Render level selection screen"""
        screen = self.game.screen
        # Title
        title = self.game.cfg.font_large.render(
            "Select Level", True, Colors.ACCENT.value
        )
        title_rect = title.get_rect(center=(self.game.cfg.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Level buttons
        total_levels = get_total_levels()

        button_width = 300
        button_height = 80
        start_x = self.game.cfg.screen_width // 2 - (button_width // 2)
        start_y = 250
        spacing = 100

        for i in range(1, total_levels + 1):
            level = get_level(i)
            y = start_y + (i - 1) * spacing

            # Check if unlocked
            unlocked = is_level_unlocked(i)

            # Button background
            color = Colors.LIGHT_BG.value if unlocked else Colors.DARKER_BG.value
            border_color = Colors.ACCENT.value if unlocked else Colors.TEXT_DIM.value

            button_rect = pygame.Rect(start_x, y, button_width, button_height)
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)

            # Level text
            if unlocked:
                level_text = self.game.cfg.font_medium.render(
                    f"Level {i}: {level.title}", True, Colors.TEXT_BRIGHT.value
                )
            else:
                level_text = self.game.cfg.font_medium.render(
                    f"Level {i}: Locked", True, Colors.TEXT_DIM.value
                )

            text_rect = level_text.get_rect(center=button_rect.center)
            screen.blit(level_text, text_rect)

            # Key hint
            if unlocked:
                key_text = self.game.cfg.font_tiny.render(
                    f"Press {i} to play", True, Colors.TEXT_DIM.value
                )
                key_rect = key_text.get_rect(
                    center=(button_rect.centerx, button_rect.centery + 30)
                )
                screen.blit(key_text, key_rect)

        # Back instruction
        back_text = self.game.cfg.font_small.render(
            "Press ESC to return to menu", True, Colors.TEXT_DIM.value
        )
        back_rect = back_text.get_rect(
            center=(self.game.cfg.screen_width // 2, self.game.cfg.screen_height - 50)
        )
        screen.blit(back_text, back_rect)

    def update(self, time_delta: float):
        """Update the state"""
        pass

    def start_level(self, level_num):
        """Start a specific level"""
        self.game.current_level = get_level(level_num)
