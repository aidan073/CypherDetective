from enum import Enum


class Colors(Enum):
    DARK_BG: tuple[int, int, int] = (25, 20, 35)  # Midnight purple-black
    DARKER_BG: tuple[int, int, int] = (10, 8, 15)  # Near-black with purple tint
    LIGHT_BG: tuple[int, int, int] = (45, 40, 55)  # Dark gray with purple tint
    ACCENT: tuple[int, int, int] = (180, 160, 200)  # Muted lavender-purple accent
    TEXT: tuple[int, int, int] = (230, 230, 235)  # Light gray-white
    TEXT_DIM: tuple[int, int, int] = (140, 135, 150)  # Medium gray with slight purple
    TEXT_BRIGHT: tuple[int, int, int] = (255, 255, 255)  # Pure white
    ERROR: tuple[int, int, int] = (180, 100, 120)  # Muted dark red
    SUCCESS: tuple[int, int, int] = (120, 180, 140)  # Muted dark green
    BORDER: tuple[int, int, int] = (80, 70, 90)  # Dark gray-purple
    BUTTON_HOVER: tuple[int, int, int] = (55, 50, 65)  # Lighter dark gray-purple
    BUTTON_ACTIVE: tuple[int, int, int] = (70, 60, 80)  # Medium gray-purple
