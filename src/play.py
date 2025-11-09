"""
CypherDetective - A noir-themed detective game where you solve crimes using Cypher queries
"""

from src.enums.colors import Colors
from src.enums.game_states import GameState

from src.states.menu import MenuState
from src.states.gameplay import GameplayState
from src.states.level_selector import LevelSelectorState

from src.cfg.game_cfg import GameConfig
from src.db.connect import DatabaseConnection
from src.enums.game_states import GamePlayState
from src.cfg.levels_cfg import get_level, get_total_levels
from src.save_handler.save_system import (
    load_progress,
    save_progress,
    complete_level,
    is_level_unlocked,
    get_highest_unlocked_level,
)

import sys
import pygame
import pygame_gui


# Initialize Pygame
pygame.init()


class Game:
    """Main game class"""

    def __init__(self):
        self.cfg = GameConfig()
        self.running = True
        self.state = MenuState(self)
        self.screen = pygame.display.set_mode(
            (self.cfg.screen_width, self.cfg.screen_height)
        )
        pygame.display.set_caption("CypherDetective")
        self.clock = pygame.time.Clock()

        # Database connection
        self.db = None
        self.db_error = None
        try:
            self.db = DatabaseConnection()
        except Exception as e:
            self.db_error = str(e)
            print(f"Warning: Could not connect to database: {e}")
            print("Game will run in demo mode (queries won't execute)")

        # Current level
        self.current_level = None
        self.current_query = ""
        self.query_result = None
        self.error_message = None
        self.success_message = None

        # pygame_gui setup
        self.ui_manager = pygame_gui.UIManager(
            (self.cfg.screen_width, self.cfg.screen_height)
        )
        self.query_input = None

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
            # Process pygame_gui events first
            if self.ui_manager.process_events(event):
                # Check for text entry line events
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.query_input:
                        self.execute_query()
                continue

            if event.type == pygame.QUIT:
                self.running = False
                return

            # Delegate event handling to current state
            self.state.handle_event(event)

    def update(self, time_delta):
        """Update game"""
        # Update pygame_gui
        self.ui_manager.update(time_delta)

        # Get query text from input box if it exists
        if self.query_input and isinstance(self.state, GameplayState):
            self.current_query = self.query_input.get_text()

    def start_level(self, level_num):
        """Start a specific level"""
        self.current_level = get_level(level_num)
        self.current_query = ""
        self.query_result = None
        self.error_message = None
        self.success_message = None

        # Create query input box
        if self.query_input:
            self.query_input.kill()
        input_rect = pygame.Rect(50, 300, self.cfg.screen_width - 100, 200)
        self.query_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                input_rect.x + 20, input_rect.y + 35, input_rect.width - 40, 30
            ),
            manager=self.ui_manager,
        )

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

    def execute_query(self):
        """Execute the player's Cypher query"""

        if not self.db:
            if self.db_error:
                self.error_message = f"Database not connected: {self.db_error}."
            else:
                self.error_message = "Database not connected."
            if isinstance(self.state, GameplayState):
                self.state.sub_state = GamePlayState.QUERY_RESULT
            return

        if not self.current_query.strip():
            self.error_message = "Please enter a query."
            if isinstance(self.state, GameplayState):
                self.state.sub_state = GamePlayState.QUERY_RESULT
            return

        # Validate query is read-only
        if not self.db.validate_query(self.current_query):
            self.error_message = "Error: Write operations are not allowed. Only read queries (MATCH, RETURN) are permitted."
            if isinstance(self.state, GameplayState):
                self.state.sub_state = GamePlayState.QUERY_RESULT
            return

        try:
            # Execute query
            results = self.db.execute_query(self.current_query)
            self.query_result = results

            # Validate results using level validator
            if self.current_level and self.current_level.validator:
                if self.current_level.validator(results):
                    # Level completed!
                    complete_level(self.current_level.level_num)
                    self.success_message = f"Level {self.current_level.level_num} completed! You found the clue!"
                    # Transition to result substate
                    if isinstance(self.state, GameplayState):
                        self.state.sub_state = GamePlayState.QUERY_RESULT
                else:
                    self.error_message = "Query executed successfully, but the results don't match the clue. Try again."
                    # Transition to result substate
                    if isinstance(self.state, GameplayState):
                        self.state.sub_state = GamePlayState.QUERY_RESULT
            else:
                # No validator, just show results
                self.error_message = "Query executed. Check if results match the clue."
                if isinstance(self.state, GameplayState):
                    self.state.sub_state = GamePlayState.QUERY_RESULT

        except Exception as e:
            self.error_message = f"Query error: {str(e)}"
            self.query_result = None
            if isinstance(self.state, GameplayState):
                self.state.sub_state = GamePlayState.QUERY_RESULT

    def render(self):
        """Render the current game state"""
        self.screen.fill(Colors.DARK_BG.value)

        # Delegate rendering to current state
        self.state.render()

        # Draw pygame_gui elements (if any are active)
        self.ui_manager.draw_ui(self.screen)

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
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
