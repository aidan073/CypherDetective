from src.enums.colors import Colors
from src.enums.game_states import GameState
from src.levels import get_level, get_total_levels
from src.states.state_interface import StateInterface
from src.save_handler.save_system import is_level_unlocked, save_progress

import pygame

# For type hinting
from pygame.event import Event


class LevelSelectorState(StateInterface):
    def __init__(self, game):
        self.game = game
        self.reset_progress_rect = None
        self.showing_confirmation = False
        self.confirmation_result = None
        self._yes_button_rect = None
        self._no_button_rect = None

    def handle_event(self, event: Event):
        if self.showing_confirmation:
            # Handle confirmation dialog events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicking Yes or No buttons
                    if self._yes_button_rect and self._yes_button_rect.collidepoint(
                        mouse_pos
                    ):
                        self.showing_confirmation = False
                        self.confirmation_result = True
                    elif self._no_button_rect and self._no_button_rect.collidepoint(
                        mouse_pos
                    ):
                        self.showing_confirmation = False
                        self.confirmation_result = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.showing_confirmation = False
                    self.confirmation_result = False
            return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.reset_progress_rect and self.reset_progress_rect.collidepoint(
                    mouse_pos
                ):
                    self.showing_confirmation = True
                    self.confirmation_result = None
                    return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.update_state(GameState.MENU)
            elif event.key in [
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
                pygame.K_4,
                pygame.K_5,
                pygame.K_6,
                pygame.K_7,
                pygame.K_8,
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

        # Level buttons - two columns of 4 levels each
        total_levels = get_total_levels()

        button_width = 300
        button_height = 80
        spacing = 100

        # Center the gap between columns on the screen
        gap_width = 200
        center_x = self.game.cfg.screen_width // 2

        # Left column: levels 1-4
        left_column_x = center_x - button_width - gap_width // 2
        # Right column: levels 5-8
        right_column_x = center_x + gap_width // 2

        start_y = 200

        for i in range(1, total_levels + 1):
            level = get_level(i)

            # Determine column and position
            if i <= 4:
                # Left column (levels 1-4)
                x = left_column_x
                y = start_y + (i - 1) * spacing
            else:
                # Right column (levels 5-8)
                x = right_column_x
                y = start_y + (i - 5) * spacing

            # Check if unlocked
            unlocked = is_level_unlocked(i)

            # Button background
            color = Colors.LIGHT_BG.value if unlocked else Colors.DARKER_BG.value
            border_color = Colors.ACCENT.value if unlocked else Colors.TEXT_DIM.value

            button_rect = pygame.Rect(x, y, button_width, button_height)
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
                    center=(button_rect.centerx, button_rect.centery + 25)
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

        # Reset progress button
        reset_text = self.game.cfg.font_small.render(
            "Reset progress", True, Colors.ERROR.value
        )
        reset_rect = reset_text.get_rect(
            center=(self.game.cfg.screen_width - 100, self.game.cfg.screen_height - 50)
        )
        reset_rect.inflate_ip(20, 20)
        self.reset_progress_rect = reset_rect
        pygame.draw.rect(screen, Colors.ERROR.value, reset_rect, 2)

        text_pos = reset_text.get_rect(center=reset_rect.center)
        screen.blit(reset_text, text_pos)

        # Render confirmation dialog if showing
        if self.showing_confirmation:
            self._render_confirmation_dialog(screen)

    def update(self, time_delta: float):
        """Update the state"""
        # Check if confirmation dialog was answered
        if self.confirmation_result is not None:
            if self.confirmation_result:
                # User confirmed - reset progress
                save_progress({})
            self.confirmation_result = None

    def _render_confirmation_dialog(self, screen: pygame.Surface):
        """Render a confirmation dialog overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface(
            (self.game.cfg.screen_width, self.game.cfg.screen_height)
        )
        overlay.set_alpha(200)
        overlay.fill(Colors.DARKER_BG.value)
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width = 500
        dialog_height = 200
        dialog_x = (self.game.cfg.screen_width - dialog_width) // 2
        dialog_y = (self.game.cfg.screen_height - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        # Draw dialog background
        pygame.draw.rect(screen, Colors.DARK_BG.value, dialog_rect)
        pygame.draw.rect(screen, Colors.BORDER.value, dialog_rect, 3)

        # Title
        title_text = self.game.cfg.font_medium.render(
            "Reset Progress?", True, Colors.ERROR.value
        )
        title_rect = title_text.get_rect(
            center=(dialog_rect.centerx, dialog_rect.y + 40)
        )
        screen.blit(title_text, title_rect)

        # Message
        message_text = self.game.cfg.font_small.render(
            "Are you sure you want to reset all progress?",
            True,
            Colors.TEXT.value,
        )
        message_rect = message_text.get_rect(
            center=(dialog_rect.centerx, dialog_rect.y + 80)
        )
        screen.blit(message_text, message_rect)

        sub_message_text = self.game.cfg.font_tiny.render(
            "This action cannot be undone.",
            True,
            Colors.TEXT_DIM.value,
        )
        sub_message_rect = sub_message_text.get_rect(
            center=(dialog_rect.centerx, dialog_rect.y + 110)
        )
        screen.blit(sub_message_text, sub_message_rect)

        # Yes button
        yes_button_width = 120
        yes_button_height = 40
        yes_button_x = dialog_rect.centerx - yes_button_width - 20
        yes_button_y = dialog_rect.bottom - yes_button_height - 30
        self._yes_button_rect = pygame.Rect(
            yes_button_x, yes_button_y, yes_button_width, yes_button_height
        )
        pygame.draw.rect(screen, Colors.ERROR.value, self._yes_button_rect)
        pygame.draw.rect(screen, Colors.TEXT_BRIGHT.value, self._yes_button_rect, 2)
        yes_text = self.game.cfg.font_small.render(
            "Yes", True, Colors.TEXT_BRIGHT.value
        )
        yes_text_rect = yes_text.get_rect(center=self._yes_button_rect.center)
        screen.blit(yes_text, yes_text_rect)

        # No button
        no_button_width = 120
        no_button_height = 40
        no_button_x = dialog_rect.centerx + 20
        no_button_y = dialog_rect.bottom - no_button_height - 30
        self._no_button_rect = pygame.Rect(
            no_button_x, no_button_y, no_button_width, no_button_height
        )
        pygame.draw.rect(screen, Colors.LIGHT_BG.value, self._no_button_rect)
        pygame.draw.rect(screen, Colors.BORDER.value, self._no_button_rect, 2)
        no_text = self.game.cfg.font_small.render("No", True, Colors.TEXT.value)
        no_text_rect = no_text.get_rect(center=self._no_button_rect.center)
        screen.blit(no_text, no_text_rect)

        # Instructions
        instruction_text = self.game.cfg.font_tiny.render(
            "Press ESC to cancel", True, Colors.TEXT_DIM.value
        )
        instruction_rect = instruction_text.get_rect(
            center=(dialog_rect.centerx, dialog_rect.bottom - 15)
        )
        screen.blit(instruction_text, instruction_rect)

    def start_level(self, level_num):
        """Start a specific level"""
        self.game.current_level = get_level(level_num)
