from src.enums.colors import Colors
from src.enums.game_states import GameState
from src.states.state_interface import StateInterface

import os
import json
import math
import pygame
import pygame_gui

# For type hinting
from pygame.event import Event


class MenuState(StateInterface):
    def __init__(self, game):
        self.game = game
        self.time_accumulator = 0.0
        self.flicker_timer = 0.0
        self.shake_timer = 0.0
        self.background_image = pygame.image.load(
            os.path.join("src", "assets", "menu_bg.png")
        ).convert()  # TODO: Look into convert, without it the cpu usage is much higher

        # Initialize pygame_gui manager
        self.pygame_gui_manager = pygame_gui.UIManager(
            (self.game.cfg.screen_width, self.game.cfg.screen_height)
        )

        # Load and scale button image
        button_image_raw = pygame.image.load(
            os.path.join("src", "assets", "case_details_button.jpg")
        ).convert_alpha()
        button_scale = 0.15  # Scale to 15% of original size
        original_size = button_image_raw.get_size()
        new_size = (
            int(original_size[0] * button_scale),
            int(original_size[1] * button_scale),
        )
        self.button_image = pygame.transform.scale(button_image_raw, new_size)
        self.pygame_gui_manager.get_theme().load_theme(
            os.path.join("src", "ui", "theme_cfgs", "menu_themes.json")
        )

        # UI elements (created in render)
        self.case_button = None
        self.case_panel = None

    def handle_event(self, event: Event):
        # Process pygame_gui events first
        self.pygame_gui_manager.process_events(event)

        # Handle button press
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == "#case_details_button":
                if self.case_panel:
                    self.case_panel.kill()
                    self.case_panel = None
                else:
                    self._create_case_panel()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_RETURN:
                self.game.update_state(GameState.LEVEL_SELECTOR)

    def render(self):
        """Render main menu with noir effects"""
        screen = self.game.screen

        # Calculate flicker effect using sine waves for smooth variation
        # Multiple sine waves at different frequencies create more natural flicker
        flicker_intensity = 0.12  # How much brightness can vary (12%)
        flicker1 = math.sin(self.flicker_timer) * 0.5
        flicker2 = math.sin(self.flicker_timer * 1.7) * 0.3
        flicker3 = math.sin(self.flicker_timer * 2.3) * 0.2
        flicker_value = 1.0 + (flicker1 + flicker2 + flicker3) * flicker_intensity
        flicker_value = max(
            0.88, min(1.12, flicker_value)
        )  # Clamp between 88% and 112%

        # Calculate shake effect using sine waves for smooth movement
        shake_intensity = 1.5  # Maximum pixels of shake
        shake_x = math.sin(self.shake_timer * 0.8) * shake_intensity
        shake_y = math.cos(self.shake_timer * 1.1) * shake_intensity

        # Apply flicker to accent color
        base_accent = Colors.ACCENT.value
        flickered_accent = tuple(int(c * flicker_value) for c in base_accent)
        flickered_accent = tuple(min(255, max(0, c)) for c in flickered_accent)

        # Blit background image first
        screen.blit(self.background_image, (0, 0))

        # Calculate text box bounds to contain all menu text
        # Title is at y=200, subtitle at y=260, instructions start at y=400 and go to y=440
        text_box_width = self.game.cfg.screen_width * 0.4
        text_box_x = self.game.cfg.screen_width * 0.5 - text_box_width / 2
        text_box_top = self.game.cfg.screen_height * 0.15  # Above title
        text_box_bottom = self.game.cfg.screen_height * 0.65  # Below last instruction
        text_box_height = text_box_bottom - text_box_top

        # Draw semi-transparent background box for text
        text_box_rect = pygame.Rect(
            text_box_x, text_box_top, text_box_width, text_box_height
        )

        # Create semi-transparent surface for the box
        text_box_surface = pygame.Surface((text_box_width, text_box_height))
        text_box_surface.set_alpha(220)  # Semi-transparent (220/255)
        text_box_surface.fill(Colors.DARKER_BG.value)
        screen.blit(text_box_surface, (text_box_x, text_box_top))

        # Draw border around text box
        pygame.draw.rect(screen, Colors.BORDER.value, text_box_rect, 2)

        # Title with flicker and shake
        title_center_x = self.game.cfg.screen_width // 2 + shake_x
        title_center_y = 200 + shake_y

        # Add subtle glow effect to title (render behind, slightly offset copies)
        glow_color = tuple(c // 4 for c in flickered_accent)  # Very dim glow
        glow_surface = self.game.cfg.font_large.render(
            "CypherDetective", True, glow_color
        )
        for offset_x, offset_y in [
            (-2, -2),
            (2, -2),
            (-2, 2),
            (2, 2),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
        ]:
            glow_rect = glow_surface.get_rect(
                center=(title_center_x + offset_x, title_center_y + offset_y)
            )
            screen.blit(glow_surface, glow_rect)

        # Render main title on top
        title = self.game.cfg.font_large.render(
            "CypherDetective", True, flickered_accent
        )
        title_rect = title.get_rect(center=(title_center_x, title_center_y))
        screen.blit(title, title_rect)

        # Subtitle with subtle flicker (less intense, slower)
        subtitle_flicker1 = math.sin(self.flicker_timer * 0.6) * 0.5
        subtitle_flicker2 = math.sin(self.flicker_timer * 1.2) * 0.3
        subtitle_flicker = 1.0 + (subtitle_flicker1 + subtitle_flicker2) * 0.06
        subtitle_flicker = max(0.94, min(1.06, subtitle_flicker))
        base_text_dim = Colors.TEXT_DIM.value
        flickered_text_dim = tuple(
            min(255, max(0, int(c * subtitle_flicker))) for c in base_text_dim
        )

        subtitle = self.game.cfg.font_medium.render(
            "Solve the crime with Cypher queries", True, flickered_text_dim
        )
        subtitle_rect = subtitle.get_rect(center=(self.game.cfg.screen_width // 2, 260))
        screen.blit(subtitle, subtitle_rect)

        # Instructions with very subtle flicker
        instructions = ["Press ENTER to Play", "Press ESC to Quit"]
        y_offset = 400
        for i, instruction in enumerate(instructions):
            # Very subtle flicker for instructions (slightly offset per line)
            inst_flicker = math.sin(self.flicker_timer * 0.4 + i * 0.5) * 0.5
            inst_flicker = 1.0 + inst_flicker * 0.04
            inst_flicker = max(0.96, min(1.04, inst_flicker))
            base_text = Colors.TEXT.value
            flickered_text = tuple(
                min(255, max(0, int(c * inst_flicker))) for c in base_text
            )

            text = self.game.cfg.font_small.render(instruction, True, flickered_text)
            text_rect = text.get_rect(
                center=(self.game.cfg.screen_width // 2, y_offset)
            )
            screen.blit(text, text_rect)
            y_offset += 40

        # Create button if it doesn't exist
        if not self.case_button:
            button_size = self.button_image.get_size()
            button_padding = 10  # Padding from edges
            # Position in bottom right corner of text box
            button_x = text_box_x + text_box_width - button_size[0] - button_padding
            button_y = text_box_top + text_box_height - button_size[1] - button_padding

            # Create invisible button that covers the image area
            self.case_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    button_x, button_y, button_size[0], button_size[1]
                ),
                text="",
                manager=self.pygame_gui_manager,
                object_id="#case_details_button",
            )

        # Draw pygame_gui elements first
        self.pygame_gui_manager.draw_ui(screen)

        # Blit button image on top (positioned where the button is)
        if self.case_button:
            button_rect = self.case_button.rect
            screen.blit(self.button_image, (button_rect.x, button_rect.y))

    def _create_case_panel(self):
        """Create the scrollable case details panel"""
        # Calculate text box bounds (same as in render)
        text_box_width = self.game.cfg.screen_width * 0.4
        text_box_x = self.game.cfg.screen_width * 0.5 - text_box_width / 2
        text_box_bottom = self.game.cfg.screen_height * 0.65

        # Position panel below text box
        panel_spacing = 10
        panel_y = text_box_bottom + panel_spacing
        panel_height = min(400, self.game.cfg.screen_height - panel_y - 20)

        # Create panel
        panel_rect = pygame.Rect(text_box_x, panel_y, text_box_width, panel_height)
        self.case_panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.pygame_gui_manager,
            object_id="#case_panel",
        )

        # Create scrollable text box inside panel
        content_text = (
            "To: Detective Cypher<br>"
            "From: Officer L. Grant<br>"
            "Subject: Preliminary Report - Death of John Doe<br><br>"
            "Detective Cypher,<br><br>"
            "This report summarizes the current understanding of the homicide of John Doe, "
            "who was found deceased in his apartment late Monday evening from an apparent gunshot wound. "
            "The scene showed no signs of forced entry, and no witnesses have come forward yet.<br><br>"
            "Ten individuals connected to the victim have been identified as potential suspects. "
            "Interviews and background checks are underway to verify alibis and determine possible motives.<br><br>"
            "At this stage, investigators are focusing on reconstructing the timeline of events leading up to the shooting "
            "and identifying any financial, personal, or professional conflicts that may have contributed to the crime. "
            "Further updates will follow as results become available. Since this is a high profile case, we need to move quickly.<br><br>"
            "Respectfully,<br>"
            "Officer L. Grant"
        )

        text_box_rect = pygame.Rect(10, 10, text_box_width - 20, panel_height - 20)
        pygame_gui.elements.UITextBox(
            relative_rect=text_box_rect,
            html_text=content_text,
            manager=self.pygame_gui_manager,
            container=self.case_panel,
        )

    def update(self, time_delta: float):
        """Update the state with noir effects timing"""
        self.time_accumulator += time_delta

        # Update flicker timer (flickers more frequently)
        self.flicker_timer += time_delta * 8.0  # Fast flicker rate

        # Update shake timer (shakes less frequently)
        self.shake_timer += time_delta * 3.0  # Slower shake rate

        # Update pygame_gui manager
        self.pygame_gui_manager.update(time_delta)
