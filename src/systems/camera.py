"""
Camera system with smooth following, screen shake, and advanced effects.
"""
import random
import math
from src.utils.constants import *
from src.utils.math_utils import Vector2, lerp
from src.entities.player import PlayerState


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
        
        # Camera zoom
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 5.0
        
        # Advanced effects
        self.anticipation_offset = Vector2(0, 0)
        self.last_player_y = 0
        self.fall_distance = 0
        self.player_state_smoothing = 0.15  # Smoothing for state transitions
    
    def update(self, dt, player):
        """
        Update camera position to follow player smoothly with advanced effects.
        
        Args:
            dt: Delta time in seconds
            player: Player object to follow
        """
        # Track fall distance for shake intensity
        if player.velocity.y > 0:  # Falling
            self.fall_distance += player.velocity.y * dt
        else:
            self.fall_distance = 0
        
        # Dynamic zoom based on speed
        self._update_dynamic_zoom(player)
        
        # Camera anticipation (look ahead based on velocity)
        self._update_anticipation(player, dt)
        
        # Calculate desired camera position
        # Keep player at CAMERA_PLAYER_OFFSET_X ratio of screen width
        self.target_position.x = player.position.x - self.width * CAMERA_PLAYER_OFFSET_X
        
        # Add anticipation offset
        self.target_position.x += self.anticipation_offset.x
        
        # Vertical: only move camera if player is outside deadzone
        player_screen_y = player.position.y - self.position.y
        
        if player_screen_y < CAMERA_VERTICAL_DEADZONE:
            self.target_position.y = player.position.y - CAMERA_VERTICAL_DEADZONE
        elif player_screen_y > self.height - CAMERA_VERTICAL_DEADZONE:
            self.target_position.y = player.position.y - (self.height - CAMERA_VERTICAL_DEADZONE)
        else:
            self.target_position.y = self.position.y
        
        # Add vertical anticipation
        self.target_position.y += self.anticipation_offset.y
        
        # Smooth follow using lerp with state-based smoothing
        smoothing = self._get_state_smoothing(player)
        self.position.x = lerp(self.position.x, self.target_position.x, smoothing)
        self.position.y = lerp(self.position.y, self.target_position.y, smoothing)
        
        # Don't let camera go below 0
        self.position.y = max(0, self.position.y)
        
        # Update zoom
        self.zoom = lerp(self.zoom, self.target_zoom, self.zoom_speed * dt)
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            # Decay shake amount over time for smoother effect
            decay_factor = self.shake_duration / (self.shake_duration + dt) if self.shake_duration > 0 else 0
            current_shake = self.shake_amount * decay_factor
            self.shake_offset.x = random.uniform(-current_shake, current_shake)
            self.shake_offset.y = random.uniform(-current_shake, current_shake)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0
        
        # Store player Y for next frame
        self.last_player_y = player.position.y
    
    def _update_dynamic_zoom(self, player):
        """
        Update camera zoom based on player speed.
        
        Args:
            player: Player object
        """
        # Calculate total speed (horizontal + vertical)
        speed = math.sqrt(player.velocity.x ** 2 + player.velocity.y ** 2)
        
        # Zoom out slightly when moving fast
        if speed > CAMERA_ZOOM_SPEED_THRESHOLD:
            # Interpolate between normal and zoomed out based on speed
            speed_factor = min((speed - CAMERA_ZOOM_SPEED_THRESHOLD) / 400.0, 1.0)
            self.target_zoom = lerp(1.0, CAMERA_ZOOM_MIN, speed_factor)
        else:
            # Zoom in slightly when moving slow or idle
            self.target_zoom = lerp(1.0, CAMERA_ZOOM_MAX, 0.3)
    
    def _update_anticipation(self, player, dt):
        """
        Update camera anticipation to look ahead in movement direction.
        
        Args:
            player: Player object
            dt: Delta time in seconds
        """
        # Horizontal anticipation based on velocity
        target_x_offset = 0
        if abs(player.velocity.x) > 100:  # Only anticipate if moving significantly
            # Look ahead in direction of movement
            target_x_offset = (player.velocity.x / 600.0) * CAMERA_ANTICIPATION_DISTANCE
        
        # Vertical anticipation based on jump/fall state
        target_y_offset = 0
        if player.velocity.y < -200:  # Jumping up
            # Look up slightly
            target_y_offset = -CAMERA_ANTICIPATION_DISTANCE * 0.3
        elif player.velocity.y > 300:  # Falling fast
            # Look down slightly
            target_y_offset = CAMERA_ANTICIPATION_DISTANCE * 0.2
        
        # Smooth interpolation to target offset
        self.anticipation_offset.x = lerp(
            self.anticipation_offset.x,
            target_x_offset,
            CAMERA_ANTICIPATION_SMOOTHING
        )
        self.anticipation_offset.y = lerp(
            self.anticipation_offset.y,
            target_y_offset,
            CAMERA_ANTICIPATION_SMOOTHING
        )
    
    def _get_state_smoothing(self, player):
        """
        Get camera smoothing based on player state for smooth transitions.
        
        Args:
            player: Player object
        
        Returns:
            Smoothing factor (0-1)
        """
        # Use different smoothing for different states
        if player.state == PlayerState.DEAD:
            return 0.05  # Very smooth when dead
        elif player.state == PlayerState.HELICOPTER:
            return 0.08  # Smooth during helicopter
        elif player.state in [PlayerState.JUMPING, PlayerState.DOUBLE_JUMPING]:
            return 0.12  # Slightly more responsive during jumps
        else:
            return self.smoothing  # Default smoothing
    
    def apply_shake(self, amount, duration, zoom_out=False, fall_distance=None):
        """
        Apply screen shake effect with optional zoom and fall distance scaling.
        
        Args:
            amount: Shake intensity in pixels
            duration: Shake duration in seconds
            zoom_out: Whether to zoom out during shake
            fall_distance: Optional fall distance to scale shake intensity
        """
        # Scale shake based on fall distance if provided
        if fall_distance is not None and fall_distance > 0:
            # Calculate shake intensity based on fall distance
            fall_shake = min(
                fall_distance * CAMERA_SHAKE_FALL_MULTIPLIER,
                CAMERA_MAX_SHAKE_FROM_FALL
            )
            amount = max(amount, fall_shake)
        
        self.shake_amount = max(self.shake_amount, amount)  # Use larger shake if already shaking
        self.shake_duration = max(self.shake_duration, duration)
        
        if zoom_out:
            self.target_zoom = 0.95  # Slight zoom out
    
    def get_fall_distance(self):
        """
        Get the current fall distance for shake calculations.
        
        Returns:
            Fall distance in pixels
        """
        return self.fall_distance
    
    def reset_fall_distance(self):
        """Reset fall distance tracker."""
        self.fall_distance = 0
    
    def reset_zoom(self):
        """Reset zoom to normal."""
        self.target_zoom = 1.0
    
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