"""
CypherDetective - A noir-themed detective game where you solve crimes using Cypher queries
"""

from src.db.connect import DatabaseConnection
from src.level.levels import get_level, get_total_levels
from src.save_handler.save_system import (
    load_progress,
    save_progress,
    complete_level,
    is_level_unlocked,
    get_highest_unlocked_level,
)

import sys
import pygame


# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Noir color scheme
COLORS = {
    "dark_bg": (20, 20, 25),
    "darker_bg": (15, 15, 20),
    "light_bg": (40, 40, 50),
    "accent": (200, 150, 100),  # Sepia/gold accent
    "text": (220, 220, 220),
    "text_dim": (150, 150, 150),
    "text_bright": (255, 255, 255),
    "error": (200, 80, 80),
    "success": (100, 200, 100),
    "border": (100, 100, 120),
    "button_hover": (60, 60, 75),
    "button_active": (80, 80, 95),
}

# Fonts
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_TINY = pygame.font.Font(None, 18)


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CypherDetective")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game states: 'menu', 'level_select', 'gameplay', 'result'
        self.state = "menu"

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

        # Input handling
        self.input_active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
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

            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_p or event.key == pygame.K_RETURN:
                        self.state = "level_select"

                elif self.state == "level_select":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
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

                elif self.state == "gameplay":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "level_select"
                        self.current_level = None
                        self.current_query = ""
                        self.query_result = None
                        self.error_message = None
                        self.success_message = None
                    elif event.key == pygame.K_RETURN:
                        self.execute_query()
                    elif event.key == pygame.K_BACKSPACE:
                        self.current_query = self.current_query[:-1]
                    elif event.key == pygame.K_TAB:
                        # Insert tab as spaces
                        self.current_query += "    "
                    else:
                        # Add character to query
                        if event.unicode:
                            self.current_query += event.unicode

                elif self.state == "result":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        if self.success_message:
                            # Level completed, go back to level select
                            self.state = "level_select"
                            self.state = "level_select"
                        else:
                            # Try again
                            self.state = "gameplay"
                            self.error_message = None

    def update(self, dt):
        """Update game state"""
        # Update cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # Blink every 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def start_level(self, level_num):
        """Start a specific level"""
        self.current_level = get_level(level_num)
        self.current_query = ""
        self.query_result = None
        self.error_message = None
        self.success_message = None
        self.state = "gameplay"

    def execute_query(self):
        """Execute the player's Cypher query"""
        if not self.db:
            if self.db_error:
                self.error_message = f"Database not connected: {self.db_error}. Please check your NEO4J_URI environment variable."
            else:
                self.error_message = (
                    "Database not connected. Please configure your Neo4j connection."
                )
            return

        if not self.current_query.strip():
            self.error_message = "Please enter a query."
            return

        # Validate query is read-only
        if not self.db.validate_query(self.current_query):
            self.error_message = "Error: Write operations are not allowed. Only read queries (MATCH, RETURN) are permitted."
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
                    self.state = "result"
                else:
                    self.error_message = "Query executed successfully, but the results don't match the clue. Try again."
            else:
                # No validator, just show results
                self.error_message = "Query executed. Check if results match the clue."

        except Exception as e:
            self.error_message = f"Query error: {str(e)}"
            self.query_result = None

    def render(self):
        """Render the current game state"""
        self.screen.fill(COLORS["dark_bg"])

        if self.state == "menu":
            self.render_menu()
        elif self.state == "level_select":
            self.render_level_select()
        elif self.state == "gameplay":
            self.render_gameplay()
        elif self.state == "result":
            self.render_result()

        pygame.display.flip()

    def render_menu(self):
        """Render main menu"""
        # Title
        title = FONT_LARGE.render("CypherDetective", True, COLORS["accent"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = FONT_MEDIUM.render(
            "Solve the crime with Cypher queries", True, COLORS["text_dim"]
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)

        # Database connection status
        if self.db:
            status_text = FONT_SMALL.render(
                "✓ Database Connected", True, COLORS["success"]
            )
        else:
            status_text = FONT_SMALL.render(
                "✗ Database Not Connected", True, COLORS["error"]
            )
        status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2, 310))
        self.screen.blit(status_text, status_rect)

        # Instructions
        instructions = ["Press P or ENTER to Play", "Press ESC to Quit"]
        y_offset = 400
        for instruction in instructions:
            text = FONT_SMALL.render(instruction, True, COLORS["text"])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

        # Noir decoration - diagonal lines
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(
                self.screen, COLORS["darker_bg"], (i, 0), (i + 200, SCREEN_HEIGHT), 1
            )

    def render_level_select(self):
        """Render level selection screen"""
        # Title
        title = FONT_LARGE.render("Select Level", True, COLORS["accent"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Level buttons
        total_levels = get_total_levels()
        highest_unlocked = get_highest_unlocked_level()

        button_width = 300
        button_height = 80
        start_x = SCREEN_WIDTH // 2 - (button_width // 2)
        start_y = 250
        spacing = 100

        for i in range(1, total_levels + 1):
            level = get_level(i)
            y = start_y + (i - 1) * spacing

            # Check if unlocked
            unlocked = is_level_unlocked(i)

            # Button background
            color = COLORS["light_bg"] if unlocked else COLORS["darker_bg"]
            border_color = COLORS["accent"] if unlocked else COLORS["text_dim"]

            button_rect = pygame.Rect(start_x, y, button_width, button_height)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, 2)

            # Level text
            if unlocked:
                level_text = FONT_MEDIUM.render(
                    f"Level {i}: {level.title}", True, COLORS["text_bright"]
                )
            else:
                level_text = FONT_MEDIUM.render(
                    f"Level {i}: Locked", True, COLORS["text_dim"]
                )

            text_rect = level_text.get_rect(center=button_rect.center)
            self.screen.blit(level_text, text_rect)

            # Key hint
            if unlocked:
                key_text = FONT_TINY.render(
                    f"Press {i} to play", True, COLORS["text_dim"]
                )
                key_rect = key_text.get_rect(
                    center=(button_rect.centerx, button_rect.centery + 30)
                )
                self.screen.blit(key_text, key_rect)

        # Back instruction
        back_text = FONT_SMALL.render(
            "Press ESC to return to menu", True, COLORS["text_dim"]
        )
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def render_gameplay(self):
        """Render gameplay screen"""
        if not self.current_level:
            return

        # Level title
        title = FONT_MEDIUM.render(
            f"Level {self.current_level.level_num}: {self.current_level.title}",
            True,
            COLORS["accent"],
        )
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Lead/Clue box
        clue_box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 120)
        pygame.draw.rect(self.screen, COLORS["darker_bg"], clue_box)
        pygame.draw.rect(self.screen, COLORS["border"], clue_box, 2)

        # Clue text
        clue_label = FONT_SMALL.render("LEAD:", True, COLORS["accent"])
        self.screen.blit(clue_label, (clue_box.x + 10, clue_box.y + 10))

        # Wrap clue text
        clue_lines = self.wrap_text(
            self.current_level.lead, FONT_SMALL, clue_box.width - 20
        )
        y_offset = clue_box.y + 35
        for line in clue_lines:
            text = FONT_SMALL.render(line, True, COLORS["text"])
            self.screen.blit(text, (clue_box.x + 10, y_offset))
            y_offset += 25

        # Hint (if available)
        if self.current_level.hint:
            hint_y = clue_box.bottom + 10
            hint_label = FONT_TINY.render("HINT:", True, COLORS["text_dim"])
            self.screen.blit(hint_label, (50, hint_y))
            hint_lines = self.wrap_text(
                self.current_level.hint, FONT_TINY, SCREEN_WIDTH - 100
            )
            y_offset = hint_y + 20
            for line in hint_lines:
                text = FONT_TINY.render(line, True, COLORS["text_dim"])
                self.screen.blit(text, (50, y_offset))
                y_offset += 18

        # Query input box
        input_box = pygame.Rect(50, 300, SCREEN_WIDTH - 100, 200)
        pygame.draw.rect(self.screen, COLORS["darker_bg"], input_box)
        pygame.draw.rect(self.screen, COLORS["border"], input_box, 2)

        input_label = FONT_SMALL.render("CYPHER QUERY:", True, COLORS["accent"])
        self.screen.blit(input_label, (input_box.x + 10, input_box.y + 10))

        # Query text with word wrap
        query_lines = self.wrap_text(
            self.current_query, FONT_SMALL, input_box.width - 40
        )
        y_offset = input_box.y + 35
        for line in query_lines:
            text = FONT_SMALL.render(line, True, COLORS["text_bright"])
            self.screen.blit(text, (input_box.x + 20, y_offset))
            y_offset += 25

        # Cursor
        if self.cursor_visible and y_offset < input_box.bottom - 10:
            cursor_x = input_box.x + 20
            if query_lines:
                # Calculate cursor position based on last line
                last_line = query_lines[-1]
                text_width = FONT_SMALL.size(last_line)[0]
                cursor_x += text_width
            pygame.draw.line(
                self.screen,
                COLORS["text_bright"],
                (cursor_x, y_offset - 20),
                (cursor_x, y_offset - 5),
                2,
            )

        # Error/Success message
        message_y = input_box.bottom + 20
        if self.error_message:
            error_lines = self.wrap_text(
                self.error_message, FONT_SMALL, SCREEN_WIDTH - 100
            )
            y_offset = message_y
            for line in error_lines:
                text = FONT_SMALL.render(line, True, COLORS["error"])
                self.screen.blit(text, (50, y_offset))
                y_offset += 25

        if self.success_message:
            success_lines = self.wrap_text(
                self.success_message, FONT_SMALL, SCREEN_WIDTH - 100
            )
            y_offset = message_y
            for line in success_lines:
                text = FONT_SMALL.render(line, True, COLORS["success"])
                self.screen.blit(text, (50, y_offset))
                y_offset += 25

        # Query results (if available)
        if self.query_result is not None:
            results_y = message_y + 60
            results_label = FONT_SMALL.render("QUERY RESULTS:", True, COLORS["accent"])
            self.screen.blit(results_label, (50, results_y))

            results_box = pygame.Rect(50, results_y + 25, SCREEN_WIDTH - 100, 150)
            pygame.draw.rect(self.screen, COLORS["darker_bg"], results_box)
            pygame.draw.rect(self.screen, COLORS["border"], results_box, 2)

            # Display results (limited)
            if self.query_result:
                result_text = str(self.query_result[:3])  # Limit to first 3 records
                if len(self.query_result) > 3:
                    result_text += (
                        f"\n... and {len(self.query_result) - 3} more records"
                    )
            else:
                result_text = "No results returned"

            result_lines = self.wrap_text(
                result_text, FONT_TINY, results_box.width - 20
            )
            y_offset = results_box.y + 10
            for line in result_lines[:6]:  # Limit display lines
                text = FONT_TINY.render(line, True, COLORS["text"])
                self.screen.blit(text, (results_box.x + 10, y_offset))
                y_offset += 16

        # Instructions
        instructions = [
            "Press ENTER to execute query",
            "Press ESC to return to level select",
        ]
        y_offset = SCREEN_HEIGHT - 60
        for instruction in instructions:
            text = FONT_TINY.render(instruction, True, COLORS["text_dim"])
            self.screen.blit(text, (50, y_offset))
            y_offset += 20

    def render_result(self):
        """Render result screen"""
        if self.success_message:
            # Success screen
            message = FONT_LARGE.render(self.success_message, True, COLORS["success"])
            message_rect = message.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )
            self.screen.blit(message, message_rect)

            next_text = FONT_MEDIUM.render(
                "Press ENTER to continue", True, COLORS["text"]
            )
            next_rect = next_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(next_text, next_rect)
        else:
            # Error screen
            if self.error_message:
                message = FONT_MEDIUM.render(self.error_message, True, COLORS["error"])
                message_rect = message.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                )
                self.screen.blit(message, message_rect)

            retry_text = FONT_SMALL.render(
                "Press ENTER to try again", True, COLORS["text"]
            )
            retry_rect = retry_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            )
            self.screen.blit(retry_text, retry_rect)

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
