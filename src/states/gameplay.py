from src.enums.colors import Colors
from src.enums.game_states import GamePlayState, GameState

import pygame
import pygame_gui

# For type hinting
from pygame.event import Event


class GameplayState:
    def __init__(self, game):
        self.game = game
        self.sub_state = GamePlayState.QUERY_INPUT

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if self.sub_state == GamePlayState.QUERY_INPUT:
                if event.key == pygame.K_ESCAPE:
                    # Clean up and return to level select
                    self.game.current_level = None
                    self.game.current_query = ""
                    self.game.query_result = None
                    self.game.error_message = None
                    self.game.success_message = None
                    if self.game.query_input:
                        self.game.query_input.kill()
                        self.game.query_input = None
                    self.game.update_state(GameState.LEVEL_SELECTOR)
                elif event.key == pygame.K_RETURN:
                    # Execute query on Enter (will transition to result state if needed)
                    self.game.execute_query()

            elif self.sub_state == GamePlayState.QUERY_RESULT:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    if self.game.success_message:
                        # Level completed, go back to level select
                        self.game.update_state(GameState.LEVEL_SELECTOR)
                    else:
                        # Try again - go back to query input
                        self.game.error_message = None
                        self.sub_state = GamePlayState.QUERY_INPUT
                        # Recreate input box if needed
                        if not self.game.query_input and self.game.current_level:
                            input_rect = pygame.Rect(
                                50, 300, self.game.screen.get_width() - 100, 200
                            )
                            self.game.query_input = pygame_gui.elements.UITextEntryLine(
                                relative_rect=pygame.Rect(
                                    input_rect.x + 20,
                                    input_rect.y + 35,
                                    input_rect.width - 40,
                                    30,
                                ),
                                manager=self.game.ui_manager,
                            )

    def render(self):
        """Render gameplay screen based on substate"""
        if self.sub_state == GamePlayState.QUERY_INPUT:
            self._render_query_input()
        elif self.sub_state == GamePlayState.QUERY_RESULT:
            self._render_result()

    def _render_query_input(self):
        """Render gameplay screen"""
        if not self.game.current_level:
            return

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
        input_box = pygame.Rect(50, 300, self.game.cfg.screen_width - 100, 200)
        pygame.draw.rect(screen, Colors.DARKER_BG.value, input_box)
        pygame.draw.rect(screen, Colors.BORDER.value, input_box, 2)

        input_label = self.game.cfg.font_small.render(
            "CYPHER QUERY:", True, Colors.ACCENT.value
        )
        screen.blit(input_label, (input_box.x + 10, input_box.y + 10))

        # UITextEntryLine is positioned and rendered by pygame_gui

        # Error/Success message
        message_y = input_box.bottom + 20
        if self.game.error_message:
            error_lines = self.game.wrap_text(
                self.game.error_message,
                self.game.cfg.font_small,
                self.game.cfg.screen_width - 100,
            )
            y_offset = message_y
            for line in error_lines:
                text = self.game.cfg.font_small.render(line, True, Colors.ERROR.value)
                screen.blit(text, (50, y_offset))
                y_offset += 25

        if self.game.success_message:
            success_lines = self.game.wrap_text(
                self.game.success_message,
                self.game.cfg.font_small,
                self.game.cfg.screen_width - 100,
            )
            y_offset = message_y
            for line in success_lines:
                text = self.game.cfg.font_small.render(line, True, Colors.SUCCESS.value)
                screen.blit(text, (50, y_offset))
                y_offset += 25

        # Query results (if available)
        if self.game.query_result is not None:
            results_y = message_y + 60
            results_label = self.game.cfg.font_small.render(
                "QUERY RESULTS:", True, Colors.ACCENT.value
            )
            screen.blit(results_label, (50, results_y))

            results_box = pygame.Rect(
                50, results_y + 25, self.game.cfg.screen_width - 100, 150
            )
            pygame.draw.rect(screen, Colors.DARKER_BG.value, results_box)
            pygame.draw.rect(screen, Colors.BORDER.value, results_box, 2)

            # Display results (limited)
            if self.game.query_result:
                result_text = str(
                    self.game.query_result[:3]
                )  # Limit to first 3 records
                if len(self.game.query_result) > 3:
                    result_text += (
                        f"\n... and {len(self.game.query_result) - 3} more records"
                    )
            else:
                result_text = "No results returned"

            result_lines = self.game.wrap_text(
                result_text, self.game.cfg.font_tiny, results_box.width - 20
            )
            y_offset = results_box.y + 10
            for line in result_lines[:6]:  # Limit display lines
                text = self.game.cfg.font_tiny.render(line, True, Colors.TEXT.value)
                screen.blit(text, (results_box.x + 10, y_offset))
                y_offset += 16

        # Instructions
        instructions = [
            "Press ENTER to execute query",
            "Press ESC to return to level select",
        ]
        y_offset = self.game.cfg.screen_height - 60
        for instruction in instructions:
            text = self.game.cfg.font_tiny.render(
                instruction, True, Colors.TEXT_DIM.value
            )
            screen.blit(text, (50, y_offset))
            y_offset += 20

    def _render_result(self):
        """Render result screen"""
        screen = self.game.screen
        if self.game.success_message:
            # Success screen
            message = self.game.cfg.font_large.render(
                self.game.success_message, True, Colors.SUCCESS.value
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
            if self.game.error_message:
                message = self.game.cfg.font_medium.render(
                    self.game.error_message, True, Colors.ERROR.value
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
