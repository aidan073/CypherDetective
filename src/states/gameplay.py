from src.enums.colors import Colors
from src.states.state_interface import StateInterface
from src.enums.game_states import GamePlayState, GameState
from src.ui.gameplay_ui import create_graph_visualization, GraphVisualization

import pygame
import pygame_gui

# For type hinting
from typing import Optional
from pygame.event import Event


class GameplayState(StateInterface):
    def __init__(self, game):
        self.game = game
        self.pygame_gui_manager = pygame_gui.UIManager(
            (self.game.cfg.screen_width, self.game.cfg.screen_height)
        )
        self.sub_state = GamePlayState.QUERY_INPUT

        # pygame_gui elements
        self.query_input = None
        self.submit_button = None

        # messages
        self.error_message = None
        self.success_message = None

        # query result
        self.query_result = None

        # graph visualization
        self.graph_visualization: Optional[GraphVisualization] = None

    def handle_event(self, event: Event):
        # Process pygame_gui events first
        self.pygame_gui_manager.process_events(event)

        # Pass events to graph visualization
        if self.graph_visualization:
            self.graph_visualization.handle_event(event)

        # Handle submit button click
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == "#submit_button":
                self.game.db.execute_user_query(self)
                return

        if event.type == pygame.KEYDOWN:
            if self.sub_state == GamePlayState.QUERY_INPUT:
                if event.key == pygame.K_ESCAPE:
                    self.clean_up()
                    self.game.current_level = None
                    self.game.update_state(GameState.LEVEL_SELECTOR)

            elif self.sub_state == GamePlayState.QUERY_RESULT:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    if self.success_message:
                        # Level completed, go back to level select
                        self.clean_up()
                        self.game.current_level = None
                        self.game.update_state(GameState.LEVEL_SELECTOR)
                    else:
                        # Try again - go back to query input
                        self.query_result = None
                        self.error_message = None
                        self.sub_state = GamePlayState.QUERY_INPUT

    def render(self):
        """Render gameplay screen based on substate"""
        if self.sub_state == GamePlayState.QUERY_INPUT:
            self._render_query_input()
        elif self.sub_state == GamePlayState.QUERY_RESULT:
            self._render_query_result()

    def update(self, time_delta: float):
        """Update the state"""
        self.pygame_gui_manager.update(time_delta)

    def clean_up(self):
        """Clean up the state"""
        if self.graph_visualization:
            self.graph_visualization.clean_up()
            self.graph_visualization = None

    def _render_query_input(self):
        """Render substate QUERY_INPUT screen"""
        screen = self.game.screen

        # Level title
        title = self.game.cfg.font_medium.render(
            f"Level {self.game.current_level.level_num}: {self.game.current_level.title}",
            True,
            Colors.ACCENT.value,
        )
        title_rect = title.get_rect(center=(self.game.cfg.screen_width // 2, 50))
        screen.blit(title, title_rect)

        # Lead/Clue box
        clue_box = pygame.Rect(50, 100, self.game.cfg.screen_width - 100, 120)
        pygame.draw.rect(screen, Colors.DARKER_BG.value, clue_box)
        pygame.draw.rect(screen, Colors.BORDER.value, clue_box, 2)

        # Clue text
        clue_label = self.game.cfg.font_small.render("LEAD:", True, Colors.ACCENT.value)
        screen.blit(clue_label, (clue_box.x + 10, clue_box.y + 10))

        # Wrap clue text
        clue_lines = self.game.wrap_text(
            self.game.current_level.lead, self.game.cfg.font_small, clue_box.width - 20
        )
        y_offset = clue_box.y + 35
        for line in clue_lines:
            text = self.game.cfg.font_small.render(line, True, Colors.TEXT.value)
            screen.blit(text, (clue_box.x + 10, y_offset))
            y_offset += 25

        # Hint (if available)
        if self.game.current_level.hint:
            hint_y = clue_box.bottom + 10
            hint_label = self.game.cfg.font_tiny.render(
                "HINT:", True, Colors.TEXT_DIM.value
            )
            screen.blit(hint_label, (50, hint_y))
            hint_lines = self.game.wrap_text(
                self.game.current_level.hint,
                self.game.cfg.font_tiny,
                self.game.cfg.screen_width - 100,
            )
            y_offset = hint_y + 20
            for line in hint_lines:
                text = self.game.cfg.font_tiny.render(line, True, Colors.TEXT_DIM.value)
                screen.blit(text, (50, y_offset))
                y_offset += 18

        # Query input box background
        input_box = pygame.Rect(50, 305, self.game.cfg.screen_width - 100, 250)
        pygame.draw.rect(screen, Colors.DARKER_BG.value, input_box)
        pygame.draw.rect(screen, Colors.BORDER.value, input_box, 2)

        input_label = self.game.cfg.font_small.render(
            "CYPHER QUERY:", True, Colors.ACCENT.value
        )
        screen.blit(input_label, (input_box.x + 10, input_box.y + 10))

        # Create query input and submit button pygame_gui elements
        if not self.query_input:
            input_rect = pygame.Rect(50, 300, self.game.cfg.screen_width - 100, 250)
            button_width = 120
            button_height = 40
            button_padding = 10

            # Input box takes most space, leaving room for label and button at bottom
            input_box_height = input_rect.height - 35 - button_height - button_padding
            input_box_y = input_rect.y + 35

            # Button positioned at bottom left, aligned with query_input box left edge
            # query_input box starts at input_rect.x + 20, so align button to that
            button_x = input_rect.x + 20
            # Move button down a bit more (reduce padding from 10 to 5)
            button_y = input_rect.bottom - button_height - 5

            self.query_input = pygame_gui.elements.UITextEntryBox(
                relative_rect=pygame.Rect(
                    input_rect.x + 20,
                    input_box_y,
                    input_rect.width - 40,
                    input_box_height,
                ),
                manager=self.pygame_gui_manager,
                object_id="#query_input",
            )

            self.submit_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    button_x,
                    button_y,
                    button_width,
                    button_height,
                ),
                text="Submit Query",
                manager=self.pygame_gui_manager,
                object_id="#submit_button",
            )

        # Initialize and render graph visualization
        if not self.graph_visualization and self.game.current_level:
            self.graph_visualization = create_graph_visualization(self)
        elif self.graph_visualization and self.game.current_level:
            # Reload graph if level changed
            if (
                self.graph_visualization.current_level
                != self.game.current_level.level_num
            ):
                self.graph_visualization.load_graph_for_level(
                    self.game.current_level.level_num
                )
            # Render graph
            self.graph_visualization.render(screen)

        self.pygame_gui_manager.draw_ui(screen)

        # Instructions
        instructions = [
            "Click 'Submit Query' button to execute",
            "Press ESC to return to level select",
        ]
        y_offset = self.game.cfg.screen_height - 60
        for instruction in instructions:
            text = self.game.cfg.font_tiny.render(
                instruction, True, Colors.TEXT_DIM.value
            )
            screen.blit(text, (50, y_offset))
            y_offset += 20

    def _render_query_result(self):
        """Render substate QUERY_RESULT screen"""
        screen = self.game.screen
        if self.success_message:
            # Success screen
            message = self.game.cfg.font_large.render(
                self.success_message, True, Colors.SUCCESS.value
            )
            message_rect = message.get_rect(
                center=(
                    self.game.cfg.screen_width // 2,
                    self.game.cfg.screen_height // 2 - 50,
                )
            )
            screen.blit(message, message_rect)

            next_text = self.game.cfg.font_medium.render(
                "Press ENTER to continue", True, Colors.TEXT.value
            )
            next_rect = next_text.get_rect(
                center=(
                    self.game.cfg.screen_width // 2,
                    self.game.cfg.screen_height // 2 + 50,
                )
            )
            screen.blit(next_text, next_rect)
        else:
            # Error screen
            if self.error_message:
                message = self.game.cfg.font_medium.render(
                    self.error_message, True, Colors.ERROR.value
                )
                message_rect = message.get_rect(
                    center=(
                        self.game.cfg.screen_width // 2,
                        self.game.cfg.screen_height // 2,
                    )
                )
                screen.blit(message, message_rect)

            retry_text = self.game.cfg.font_small.render(
                "Press ENTER to try again", True, Colors.TEXT.value
            )
            retry_rect = retry_text.get_rect(
                center=(
                    self.game.cfg.screen_width // 2,
                    self.game.cfg.screen_height // 2 + 100,
                )
            )
            screen.blit(retry_text, retry_rect)
