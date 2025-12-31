"""
Difficulty progression system.
"""
from src.utils.constants import *


class DifficultyManager:
    """
    Manages game difficulty progression over time.
    Increases speed and platform challenge gradually.
    """
    
    def __init__(self):
        self.game_time = 0.0
        self.game_speed = BASE_GAME_SPEED
        self.difficulty_level = 1.0
    
    def update(self, dt):
        """
        Update difficulty based on elapsed time.
        
        Args:
            dt: Delta time in seconds
        """
        self.game_time += dt
        
        # Increase speed every interval
        speed_increases = int(self.game_time / SPEED_INCREASE_INTERVAL)
        self.game_speed = min(
            BASE_GAME_SPEED + (speed_increases * SPEED_INCREASE_AMOUNT),
            MAX_GAME_SPEED
        )
        
        # Calculate difficulty level (1.0 to 3.0)
        self.difficulty_level = 1.0 + (self.game_time / 60.0)
        self.difficulty_level = min(self.difficulty_level, 3.0)
    
    def get_game_speed(self):
        """
        Get current game speed.
        
        Returns:
            Speed in pixels/second
        """
        return self.game_speed
    
    def get_difficulty_level(self):
        """
        Get current difficulty level.
        
        Returns:
            Difficulty level (1.0 - 3.0)
        """
        return self.difficulty_level
    
    def reset(self):
        """Reset difficulty for new game."""
        self.game_time = 0.0
        self.game_speed = BASE_GAME_SPEED
        self.difficulty_level = 1.0