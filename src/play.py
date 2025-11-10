"""
CypherDetective - A noir-themed detective game where you solve crimes using Cypher queries
"""

from src.enums.colors import Colors
from src.enums.game_states import GameState

from src.states.menu import MenuState
from src.states.gameplay import GameplayState
from src.states.level_selector import LevelSelectorState

from src.cfg.game_cfg import GameConfig
from src.db.database import DatabaseConnection
from src.save_handler.save_system import (
    load_progress,
    save_progress,
    complete_level,
    is_level_unlocked,
    get_highest_unlocked_level,
)

import os
import sys
import pygame

# import psutil

# process = psutil.Process(os.getpid())


# Initialize Pygame
pygame.init()


class GameManager:
    """Main game class"""

    def __init__(self):
        self.cfg = GameConfig()
        self.running = True
        self.screen = pygame.display.set_mode(
            (self.cfg.screen_width, self.cfg.screen_height)
        )
        self.state = MenuState(self)
        self.icon = pygame.image.load(os.path.join("src", "assets", "icon.png"))
        self.icon = pygame.transform.scale(self.icon, (64, 64))
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption("CypherDetective")
        self.clock = pygame.time.Clock()

        self.db = DatabaseConnection()
        self.current_level = None

    def run(self):
        """Main game loop"""
        while self.running:
            time_delta = self.clock.tick(self.cfg.fps) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.render()

        if self.db:
            self.db.close()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Delegate event handling to current state
            self.state.handle_event(event)

    def update(self, time_delta):
        """Update game"""
        # cpu = process.cpu_percent(interval=None)
        # mem = process.memory_info().rss / (1024**2)  # in MB
        # print(f"CPU usage: {cpu:.2f}%, Memory usage: {mem:.2f} MB")
        self.state.update(time_delta)

    def update_state(self, state: GameState):
        match state:
            case GameState.MENU:
                if not isinstance(self.state, MenuState):
                    self.state = MenuState(self)
            case GameState.LEVEL_SELECTOR:
                if not isinstance(self.state, LevelSelectorState):
                    self.state = LevelSelectorState(self)
            case GameState.GAMEPLAY:
                if not isinstance(self.state, GameplayState):
                    self.state = GameplayState(self)
            case _:
                raise ValueError(f"Invalid game state: {state}")

    def render(self):
        """Render the current game display"""
        # Delegate rendering to current state
        self.state.render()
        pygame.display.flip()

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [text]


def main():
    """Entry point"""
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
