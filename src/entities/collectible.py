"""
Collectible items and power-ups.
"""
from enum import Enum
import pygame
import math
from src.utils.constants import *
from src.utils.math_utils import Vector2


class CollectibleType(Enum):
    """Types of collectibles."""
    COIN = "coin"
    SPEED_BOOST = "speed_boost"
    SHIELD = "shield"
    MAGNET = "magnet"
    DOUBLE_POINTS = "double_points"
    EXTRA_JUMP = "extra_jump"


class Collectible:
    """
    Collectible item with:
    - Different types (coins, power-ups)
    - Floating animation
    - Rotation animation
    - Magnetic attraction (when magnet active)
    - Collection effects
    """
    
    # Collectible properties by type
    PROPERTIES = {
        CollectibleType.COIN: {
            'color': (255, 215, 0),  # Gold
            'secondary_color': (255, 255, 0),  # Yellow
            'size': 20,
            'points': 5,
            'duration': 0,  # Instant effect
            'description': '+5 points'
        },
        CollectibleType.SPEED_BOOST: {
            'color': (0, 255, 255),  # Cyan
            'secondary_color': (0, 200, 255),  # Light blue
            'size': 24,
            'points': 0,
            'duration': 5.0,  # seconds
            'description': 'Speed boost!'
        },
        CollectibleType.SHIELD: {
            'color': (100, 200, 255),  # Light blue
            'secondary_color': (150, 220, 255),  # Lighter blue
            'size': 26,
            'points': 0,
            'duration': 0,  # Until used
            'description': 'Shield active!'
        },
        CollectibleType.MAGNET: {
            'color': (255, 0, 255),  # Magenta
            'secondary_color': (255, 100, 255),  # Pink
            'size': 24,
            'points': 0,
            'duration': 8.0,  # seconds
            'description': 'Magnet active!'
        },
        CollectibleType.DOUBLE_POINTS: {
            'color': (255, 165, 0),  # Orange
            'secondary_color': (255, 200, 0),  # Light orange
            'size': 26,
            'points': 0,
            'duration': 10.0,  # seconds
            'description': '2x Points!'
        },
        CollectibleType.EXTRA_JUMP: {
            'color': (50, 255, 50),  # Bright green
            'secondary_color': (100, 255, 100),  # Light green
            'size': 24,
            'points': 0,
            'duration': 0,  # No timer - lasts until third jump is used
            'description': 'Triple jump!'
        }
    }
    
    # Class-level sprite cache (shared across all instances)
    _sprite_cache = {}
    
    def __init__(self, x, y, collectible_type):
        """
        Initialize collectible.
        
        Args:
            x: X position
            y: Y position
            collectible_type: CollectibleType enum value
        """
        self.position = Vector2(x, y)
        self.type = collectible_type
        self.properties = self.PROPERTIES[collectible_type]
        
        # Visual properties
        self.size = self.properties['size']
        self.color = self.properties['color']
        self.secondary_color = self.properties['secondary_color']
        
        # Animation
        self.float_offset = 0.0
        self.float_speed = 2.0  # Hz
        self.float_amplitude = 10.0  # pixels
        self.rotation = 0.0
        self.rotation_speed = 180.0  # degrees per second
        self.pulse_scale = 1.0
        self.pulse_speed = 3.0  # Hz
        
        # State
        self.collected = False
        self.alive = True
        self.time_alive = 0.0
        
        # Magnetic attraction
        self.velocity = Vector2(0, 0)
        self.attracted = False
        self.attraction_speed = 800.0  # pixels/second
        
        # Pre-render sprite if not cached
        if collectible_type not in Collectible._sprite_cache:
            self._cache_sprite()
    
    def _cache_sprite(self):
        """Pre-render and cache the collectible sprite."""
        # Create surface with alpha channel
        size = self.size * 2  # Extra space for effects
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Render to surface based on type
        if self.type == CollectibleType.COIN:
            pygame.draw.circle(surface, self.color, (center, center), self.size // 2)
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 3)
            pygame.draw.circle(surface, self.color, (center, center), self.size // 6)
        
        elif self.type == CollectibleType.SPEED_BOOST:
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 2)
            points = [
                (center, center - self.size // 3),
                (center - self.size // 6, center),
                (center + self.size // 8, center),
                (center - self.size // 8, center + self.size // 3),
                (center + self.size // 6, center - self.size // 8),
                (center - self.size // 8, center - self.size // 8)
            ]
            pygame.draw.polygon(surface, self.color, points)
        
        elif self.type == CollectibleType.SHIELD:
            points = [
                (center, center - self.size // 2),
                (center + self.size // 3, center - self.size // 4),
                (center + self.size // 3, center + self.size // 4),
                (center, center + self.size // 2),
                (center - self.size // 3, center + self.size // 4),
                (center - self.size // 3, center - self.size // 4)
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, self.secondary_color, points, 3)
        
        elif self.type == CollectibleType.MAGNET:
            rect_width = self.size // 4
            rect_height = self.size // 2
            pygame.draw.rect(surface, self.color,
                            (center - self.size // 3, center - rect_height // 2, rect_width, rect_height))
            pygame.draw.rect(surface, self.secondary_color,
                            (center + self.size // 3 - rect_width, center - rect_height // 2, rect_width, rect_height))
            pygame.draw.rect(surface, self.color,
                            (center - self.size // 3, center + rect_height // 2 - rect_width,
                             self.size * 2 // 3, rect_width))
        
        elif self.type == CollectibleType.DOUBLE_POINTS:
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 2)
            font = pygame.font.Font(None, self.size)
            text = font.render("2x", True, self.color)
            text_rect = text.get_rect(center=(center, center))
            surface.blit(text, text_rect)
        
        elif self.type == CollectibleType.EXTRA_JUMP:
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 2)
            points = [
                (center, center - self.size // 3),
                (center + self.size // 4, center),
                (center + self.size // 8, center),
                (center + self.size // 8, center + self.size // 3),
                (center - self.size // 8, center + self.size // 3),
                (center - self.size // 8, center),
                (center - self.size // 4, center)
            ]
            pygame.draw.polygon(surface, self.color, points)
        
        # Cache the surface
        Collectible._sprite_cache[self.type] = surface
    
    def update(self, dt, player_pos=None, magnet_active=False):
        """
        Update collectible animation and behavior.
        
        Args:
            dt: Delta time in seconds
            player_pos: Player position Vector2 (for magnet attraction)
            magnet_active: Whether magnet power-up is active
        """
        self.time_alive += dt
        
        # Floating animation
        self.float_offset = math.sin(self.time_alive * self.float_speed * 2 * math.pi) * self.float_amplitude
        
        # Rotation animation
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360
        
        # Pulse animation
        self.pulse_scale = 1.0 + math.sin(self.time_alive * self.pulse_speed * 2 * math.pi) * 0.1
        
        # Magnetic attraction
        if magnet_active and player_pos and not self.collected:
            self.attracted = True
            # Calculate direction to player
            dx = player_pos.x - self.position.x
            dy = player_pos.y - self.position.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # Normalize and apply attraction
                self.velocity.x = (dx / distance) * self.attraction_speed
                self.velocity.y = (dy / distance) * self.attraction_speed
                
                # Move towards player
                self.position.x += self.velocity.x * dt
                self.position.y += self.velocity.y * dt
    
    def collect(self):
        """Mark collectible as collected."""
        self.collected = True
        self.alive = False
    
    def get_collision_rect(self):
        """
        Get collision rectangle.
        
        Returns:
            pygame.Rect for collision detection
        """
        # Use slightly smaller collision box for better feel
        collision_size = self.size * 0.8
        return pygame.Rect(
            self.position.x - collision_size / 2,
            self.position.y - collision_size / 2 + self.float_offset,
            collision_size,
            collision_size
        )
    
    def render(self, screen, camera):
        """
        Render collectible with animations using cached sprite (optimized).
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        # Get cached sprite
        cached_sprite = Collectible._sprite_cache.get(self.type)
        if not cached_sprite:
            return
        
        # Get screen position
        screen_pos = camera.world_to_screen(self.position)
        x = int(screen_pos.x)
        y = int(screen_pos.y + self.float_offset)
        
        # Skip pulse scaling for better performance - use cached sprite directly
        sprite_size = cached_sprite.get_width()
        screen.blit(cached_sprite, (x - sprite_size // 2, y - sprite_size // 2))
    
    @classmethod
    def clear_cache(cls):
        """Clear the sprite cache (useful when changing themes)."""
        cls._sprite_cache.clear()