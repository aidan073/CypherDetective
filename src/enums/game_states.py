from enum import Enum, auto


class GameState(Enum):
    MENU = auto()
    LEVEL_SELECTOR = auto()
    GAMEPLAY = auto()


class GamePlayState(Enum):
    QUERY_INPUT = auto()
    QUERY_RESULT = auto()
