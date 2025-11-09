from abc import ABC, abstractmethod

# For type hinting
from pygame.event import Event


class StateInterface(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        """Handle a pygame event"""

    @abstractmethod
    def render(self):
        """Render the state"""

    @abstractmethod
    def update(self, time_delta: float):
        """Update the state"""
