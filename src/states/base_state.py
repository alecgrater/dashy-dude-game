"""
Base state class for game state machine.
"""
from abc import ABC, abstractmethod


class BaseState(ABC):
    """
    Abstract base class for all game states.
    """
    
    def __init__(self, game):
        """
        Initialize state.
        
        Args:
            game: Reference to main Game instance
        """
        self.game = game
    
    @abstractmethod
    def enter(self):
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, dt):
        """
        Update state logic.
        
        Args:
            dt: Delta time in seconds
        """
        pass
    
    @abstractmethod
    def render(self, screen):
        """
        Render state visuals.
        
        Args:
            screen: pygame.Surface to draw on
        """
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: pygame.event.Event
        """
        pass