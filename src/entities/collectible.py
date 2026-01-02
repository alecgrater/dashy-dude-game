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
        """Pre-render and cache the collectible sprite with distinctive icons."""
        # Create surface with alpha channel
        size = self.size * 2  # Extra space for effects
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Render to surface based on type
        if self.type == CollectibleType.COIN:
            # Golden coin with $ symbol and shine
            radius = self.size // 2
            # Outer ring
            pygame.draw.circle(surface, (180, 150, 0), (center, center), radius)
            # Inner gold
            pygame.draw.circle(surface, self.color, (center, center), radius - 2)
            # Highlight arc (shine effect)
            pygame.draw.arc(surface, (255, 255, 200),
                           (center - radius + 4, center - radius + 4, radius * 2 - 8, radius * 2 - 8),
                           0.5, 1.5, 3)
            # Dollar sign
            font = pygame.font.Font(None, int(self.size * 0.8))
            text = font.render("$", True, (180, 130, 0))
            text_rect = text.get_rect(center=(center, center))
            surface.blit(text, text_rect)
        
        elif self.type == CollectibleType.SPEED_BOOST:
            # Lightning bolt icon
            # Background glow circle
            pygame.draw.circle(surface, (0, 100, 150, 100), (center, center), self.size // 2 + 4)
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 2)
            # Lightning bolt shape
            bolt_points = [
                (center + 2, center - self.size // 2 + 4),   # Top
                (center - 4, center - 2),                     # Upper left
                (center + 2, center - 2),                     # Upper middle
                (center - 2, center + self.size // 2 - 4),   # Bottom
                (center + 4, center + 2),                     # Lower right
                (center - 2, center + 2),                     # Lower middle
            ]
            pygame.draw.polygon(surface, self.color, bolt_points)
            # White highlight
            pygame.draw.polygon(surface, (255, 255, 255), bolt_points, 1)
        
        elif self.type == CollectibleType.SHIELD:
            # Shield/armor icon
            # Outer glow
            pygame.draw.circle(surface, (50, 150, 200, 80), (center, center), self.size // 2 + 4)
            # Shield shape (pointed bottom)
            shield_points = [
                (center, center - self.size // 2 + 2),        # Top center
                (center + self.size // 2 - 2, center - self.size // 3),  # Top right
                (center + self.size // 2 - 4, center + self.size // 6),  # Mid right
                (center, center + self.size // 2 - 2),        # Bottom point
                (center - self.size // 2 + 4, center + self.size // 6),  # Mid left
                (center - self.size // 2 + 2, center - self.size // 3),  # Top left
            ]
            pygame.draw.polygon(surface, self.color, shield_points)
            # Inner shield detail
            inner_points = [
                (center, center - self.size // 3),
                (center + self.size // 3 - 2, center - self.size // 5),
                (center + self.size // 3 - 4, center + self.size // 10),
                (center, center + self.size // 3 - 2),
                (center - self.size // 3 + 4, center + self.size // 10),
                (center - self.size // 3 + 2, center - self.size // 5),
            ]
            pygame.draw.polygon(surface, self.secondary_color, inner_points)
            # Cross/plus on shield
            pygame.draw.line(surface, (255, 255, 255),
                           (center, center - self.size // 5),
                           (center, center + self.size // 6), 2)
            pygame.draw.line(surface, (255, 255, 255),
                           (center - self.size // 6, center - self.size // 20),
                           (center + self.size // 6, center - self.size // 20), 2)
        
        elif self.type == CollectibleType.MAGNET:
            # U-shaped magnet icon
            # Background glow
            pygame.draw.circle(surface, (200, 0, 200, 80), (center, center), self.size // 2 + 4)
            pygame.draw.circle(surface, (40, 40, 60), (center, center), self.size // 2)
            # Magnet U-shape
            magnet_width = self.size // 3
            magnet_height = self.size // 2
            # Left pole (red)
            pygame.draw.rect(surface, (255, 50, 50),
                           (center - magnet_width - 2, center - magnet_height // 2,
                            magnet_width // 2 + 2, magnet_height))
            # Right pole (blue)
            pygame.draw.rect(surface, (50, 50, 255),
                           (center + magnet_width // 2, center - magnet_height // 2,
                            magnet_width // 2 + 2, magnet_height))
            # Bottom connector (gray)
            pygame.draw.rect(surface, (150, 150, 150),
                           (center - magnet_width - 2, center + magnet_height // 2 - 4,
                            magnet_width * 2 + 4, 6))
            # Magnetic field lines (small arcs)
            pygame.draw.arc(surface, self.secondary_color,
                          (center - self.size // 4, center - self.size // 2 - 2,
                           self.size // 2, self.size // 3),
                          3.14, 0, 2)
        
        elif self.type == CollectibleType.DOUBLE_POINTS:
            # Star burst with 2x text
            # Background star burst
            num_rays = 8
            outer_radius = self.size // 2
            inner_radius = self.size // 3
            star_points = []
            for i in range(num_rays * 2):
                angle = (i * math.pi / num_rays) - math.pi / 2
                if i % 2 == 0:
                    r = outer_radius
                else:
                    r = inner_radius
                px = center + int(r * math.cos(angle))
                py = center + int(r * math.sin(angle))
                star_points.append((px, py))
            pygame.draw.polygon(surface, self.secondary_color, star_points)
            pygame.draw.polygon(surface, self.color, star_points, 2)
            # Inner circle
            pygame.draw.circle(surface, self.color, (center, center), self.size // 4)
            # 2x text
            font = pygame.font.Font(None, int(self.size * 0.6))
            text = font.render("2x", True, (255, 255, 255))
            text_rect = text.get_rect(center=(center, center))
            surface.blit(text, text_rect)
        
        elif self.type == CollectibleType.EXTRA_JUMP:
            # Spring/bouncy arrow icon
            # Background circle
            pygame.draw.circle(surface, (20, 150, 20, 100), (center, center), self.size // 2 + 4)
            pygame.draw.circle(surface, self.secondary_color, (center, center), self.size // 2)
            # Spring coils
            coil_width = self.size // 3
            coil_y_start = center + self.size // 4
            for i in range(3):
                y = coil_y_start - i * 5
                pygame.draw.arc(surface, self.color,
                              (center - coil_width // 2, y - 3, coil_width, 6),
                              0, 3.14, 2)
            # Upward arrow
            arrow_points = [
                (center, center - self.size // 3),           # Top point
                (center - self.size // 4, center - self.size // 8),  # Left wing
                (center - self.size // 8, center - self.size // 8),  # Left inner
                (center - self.size // 8, center + self.size // 8),  # Left bottom
                (center + self.size // 8, center + self.size // 8),  # Right bottom
                (center + self.size // 8, center - self.size // 8),  # Right inner
                (center + self.size // 4, center - self.size // 8),  # Right wing
            ]
            pygame.draw.polygon(surface, self.color, arrow_points)
            pygame.draw.polygon(surface, (255, 255, 255), arrow_points, 1)
        
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