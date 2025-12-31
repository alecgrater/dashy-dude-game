"""
Platform entity with different types and behaviors.
"""
from enum import Enum
import pygame
import math
from src.utils.constants import *
from src.utils.math_utils import Vector2, lerp


class PlatformType(Enum):
    """Platform types with different behaviors."""
    STATIC = "static"
    MOVING = "moving"
    SMALL = "small"
    CRUMBLING = "crumbling"


class Platform:
    """
    Platform entity that player can land on.
    Supports different types with unique behaviors.
    """
    
    def __init__(self, x=0, y=0, width=MAX_PLATFORM_WIDTH, height=PLATFORM_HEIGHT,
                 platform_type=PlatformType.STATIC):
        self.position = Vector2(x, y)
        self.width = width * PLATFORM_SCALE
        self.height = height * PLATFORM_SCALE
        self.platform_type = platform_type
        self.active = True
        
        # Moving platform
        self.move_speed = 100.0  # pixels/second
        self.move_range = 150.0  # pixels
        self.start_x = x
        self.move_direction = 1
        self.move_time = 0.0
        
        # Crumbling platform
        self.crumble_timer = 0.0
        self.crumble_delay = 0.5  # seconds before crumbling
        self.is_crumbling = False
        self.player_landed = False
        
        # Sprite
        self.sprite = None
        
        # Squash and stretch
        self.scale_y = 1.0
        self.target_scale_y = 1.0
        self.squash_speed = 20.0
    
    def update(self, dt):
        """
        Update platform behavior.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return
        
        if self.platform_type == PlatformType.MOVING:
            self._update_moving(dt)
        elif self.platform_type == PlatformType.CRUMBLING:
            self._update_crumbling(dt)
        
        # Update squash and stretch
        self.scale_y = lerp(self.scale_y, self.target_scale_y, self.squash_speed * dt)
        self.target_scale_y = lerp(self.target_scale_y, 1.0, 8.0 * dt)
        
        # Clamp scale
        self.scale_y = max(0.5, min(1.2, self.scale_y))
    
    def _update_moving(self, dt):
        """Update moving platform position."""
        self.move_time += dt
        
        # Oscillate using sine wave
        offset = math.sin(self.move_time * 2.0) * self.move_range
        self.position.x = self.start_x + offset
    
    def _update_crumbling(self, dt):
        """Update crumbling platform state."""
        if self.player_landed and not self.is_crumbling:
            self.crumble_timer += dt
            if self.crumble_timer >= self.crumble_delay:
                self.is_crumbling = True
                self.active = False
    
    def on_player_land(self):
        """Called when player lands on this platform."""
        if self.platform_type == PlatformType.CRUMBLING:
            self.player_landed = True
        
        # Squash effect on landing
        self.target_scale_y = 0.7
    
    def reset(self, x, y, width, height, platform_type=PlatformType.STATIC):
        """
        Reset platform for object pooling.
        
        Args:
            x, y: Position
            width, height: Dimensions (will be scaled)
            platform_type: PlatformType enum
        """
        self.position.x = x
        self.position.y = y
        self.width = width * PLATFORM_SCALE
        self.height = height * PLATFORM_SCALE
        self.platform_type = platform_type
        self.active = True
        
        # Reset moving platform
        self.start_x = x
        self.move_time = 0.0
        self.move_direction = 1
        
        # Reset crumbling platform
        self.crumble_timer = 0.0
        self.is_crumbling = False
        self.player_landed = False
        
        # Reset squash and stretch
        self.scale_y = 1.0
        self.target_scale_y = 1.0
    
    def get_rect(self):
        """
        Get collision rectangle.
        
        Returns:
            pygame.Rect for collision detection
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            int(self.width),
            int(self.height)
        )
    
    def get_render_position(self, camera):
        """
        Get screen position for rendering.
        
        Args:
            camera: Camera instance
        
        Returns:
            Tuple of (x, y) screen coordinates
        """
        screen_pos = camera.world_to_screen(self.position)
        return (int(screen_pos.x), int(screen_pos.y))
    
    def render(self, screen, camera, sprites):
        """
        Render platform sprite.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
            sprites: Dictionary of platform sprites
        """
        if not self.active:
            return
        
        # Check if visible
        if not camera.is_visible(self.position.x, self.position.y,
                                 self.width, self.height):
            return
        
        pos = self.get_render_position(camera)
        
        # Calculate scaled height
        scaled_height = int(self.height * self.scale_y)
        height_diff = self.height - scaled_height
        
        # Get appropriate sprite
        sprite_key = self.platform_type.value
        if sprite_key in sprites:
            sprite = sprites[sprite_key]
            
            # Scale sprite to match platform width and squash/stretch
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite,
                    (int(self.width), scaled_height))
                
                # Apply transparency if crumbling
                if self.platform_type == PlatformType.CRUMBLING and self.player_landed:
                    alpha = int(255 * (1.0 - self.crumble_timer / self.crumble_delay))
                    scaled_sprite.set_alpha(alpha)
                
                screen.blit(scaled_sprite, (pos[0], pos[1] + height_diff))
        else:
            # Fallback: draw colored rectangle with squash/stretch
            color = PLATFORM_BASE
            if self.platform_type == PlatformType.MOVING:
                color = PLATFORM_MOVING
            elif self.platform_type == PlatformType.SMALL:
                color = PLATFORM_SMALL
            elif self.platform_type == PlatformType.CRUMBLING:
                color = PLATFORM_CRUMBLING
            
            pygame.draw.rect(screen, color,
                (pos[0], pos[1] + height_diff, self.width, scaled_height))