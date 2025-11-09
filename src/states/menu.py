from src.enums.colors import Colors
from src.enums.game_states import GameState
from src.states.state_interface import StateInterface

import pygame

# For type hinting
from pygame.event import Event


class MenuState(StateInterface):
    def __init__(self, game):
        self.game = game

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_p or event.key == pygame.K_RETURN:
                self.game.update_state(GameState.LEVEL_SELECTOR)

    def render(self):
        """Render main menu"""
        screen = self.game.screen
        # Title
        title = self.game.cfg.font_large.render(
            "CypherDetective", True, Colors.ACCENT.value
        )
        title_rect = title.get_rect(center=(self.game.cfg.screen_width // 2, 200))
        screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.game.cfg.font_medium.render(
            "Solve the crime with Cypher queries", True, Colors.TEXT_DIM.value
        )
        subtitle_rect = subtitle.get_rect(center=(self.game.cfg.screen_width // 2, 260))
        screen.blit(subtitle, subtitle_rect)

        # Instructions
        instructions = ["Press P or ENTER to Play", "Press ESC to Quit"]
        y_offset = 400
        for instruction in instructions:
            text = self.game.cfg.font_small.render(instruction, True, Colors.TEXT.value)
            text_rect = text.get_rect(
                center=(self.game.cfg.screen_width // 2, y_offset)
            )
            screen.blit(text, text_rect)
            y_offset += 40

        # Noir decoration - diagonal lines
        for i in range(0, self.game.cfg.screen_width, 20):
            pygame.draw.line(
                screen,
                Colors.DARKER_BG.value,
                (i, 0),
                (i + 200, self.game.cfg.screen_height),
                1,
            )

    def update(self, time_delta: float):
        """Update the state"""
        pass
