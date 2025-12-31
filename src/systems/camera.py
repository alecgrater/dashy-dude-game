"""
Camera system with smooth following and screen shake.
"""
import random
from src.utils.constants import *
from src.utils.math_utils import Vector2, lerp


class Camera:
    """
    Camera that smoothly follows the player with screen shake support.
    """
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = Vector2(0, 0)
        self.target_position = Vector2(0, 0)
        self.smoothing = CAMERA_SMOOTHING
        
        # Screen shake
        self.shake_amount = 0.0
        self.shake_duration = 0.0
        self.shake_offset = Vector2(0, 0)
    
    def update(self, dt, player):
        """
        Update camera position to follow player smoothly.
        
        Args:
            dt: Delta time in seconds
            player: Player object to follow
        """
        # Calculate desired camera position
        # Keep player at CAMERA_PLAYER_OFFSET_X ratio of screen width
        self.target_position.x = player.position.x - self.width * CAMERA_PLAYER_OFFSET_X
        
        # Vertical: only move camera if player is outside deadzone
        player_screen_y = player.position.y - self.position.y
        
        if player_screen_y < CAMERA_VERTICAL_DEADZONE:
            self.target_position.y = player.position.y - CAMERA_VERTICAL_DEADZONE
        elif player_screen_y > self.height - CAMERA_VERTICAL_DEADZONE:
            self.target_position.y = player.position.y - (self.height - CAMERA_VERTICAL_DEADZONE)
        else:
            self.target_position.y = self.position.y
        
        # Smooth follow using lerp
        self.position.x = lerp(self.position.x, self.target_position.x, self.smoothing)
        self.position.y = lerp(self.position.y, self.target_position.y, self.smoothing)
        
        # Don't let camera go below 0
        self.position.y = max(0, self.position.y)
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0
    
    def apply_shake(self, amount, duration):
        """
        Apply screen shake effect.
        
        Args:
            amount: Shake intensity in pixels
            duration: Shake duration in seconds
        """
        self.shake_amount = amount
        self.shake_duration = duration
    
    def world_to_screen(self, world_pos):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Vector2 in world space
        
        Returns:
            Vector2 in screen space
        """
        return Vector2(
            world_pos.x - self.position.x + self.shake_offset.x,
            world_pos.y - self.position.y + self.shake_offset.y
        )
    
    def screen_to_world(self, screen_pos):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Vector2 in screen space
        
        Returns:
            Vector2 in world space
        """
        return Vector2(
            screen_pos.x + self.position.x - self.shake_offset.x,
            screen_pos.y + self.position.y - self.shake_offset.y
        )
    
    def is_visible(self, x, y, width, height):
        """
        Check if rectangle is visible in camera view.
        
        Args:
            x, y: Top-left position in world space
            width, height: Rectangle dimensions
        
        Returns:
            True if rectangle is at least partially visible
        """
        # Add some margin for objects just off-screen
        margin = 100
        
        return (x + width > self.position.x - margin and
                x < self.position.x + self.width + margin and
                y + height > self.position.y - margin and
                y < self.position.y + self.height + margin)
    
    def get_view_rect(self):
        """
        Get the camera's view rectangle in world space.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        return (self.position.x, self.position.y, self.width, self.height)