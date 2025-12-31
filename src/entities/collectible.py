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
            'duration': 15.0,  # seconds
            'description': 'Triple jump!'
        }
    }
    
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
        Render collectible with animations.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        # Get screen position
        screen_pos = camera.world_to_screen(self.position)
        x = int(screen_pos.x)
        y = int(screen_pos.y + self.float_offset)
        
        # Apply pulse scale
        size = int(self.size * self.pulse_scale)
        
        # Draw based on type
        if self.type == CollectibleType.COIN:
            self._render_coin(screen, x, y, size)
        elif self.type == CollectibleType.SPEED_BOOST:
            self._render_speed_boost(screen, x, y, size)
        elif self.type == CollectibleType.SHIELD:
            self._render_shield(screen, x, y, size)
        elif self.type == CollectibleType.MAGNET:
            self._render_magnet(screen, x, y, size)
        elif self.type == CollectibleType.DOUBLE_POINTS:
            self._render_double_points(screen, x, y, size)
        elif self.type == CollectibleType.EXTRA_JUMP:
            self._render_extra_jump(screen, x, y, size)
    
    def _render_coin(self, screen, x, y, size):
        """Render coin collectible."""
        # Outer circle (gold)
        pygame.draw.circle(screen, self.color, (x, y), size // 2)
        # Inner circle (yellow)
        pygame.draw.circle(screen, self.secondary_color, (x, y), size // 3)
        # Center dot
        pygame.draw.circle(screen, self.color, (x, y), size // 6)
    
    def _render_speed_boost(self, screen, x, y, size):
        """Render speed boost power-up (lightning bolt)."""
        # Background circle
        pygame.draw.circle(screen, self.secondary_color, (x, y), size // 2)
        
        # Lightning bolt shape
        points = [
            (x, y - size // 3),
            (x - size // 6, y),
            (x + size // 8, y),
            (x - size // 8, y + size // 3),
            (x + size // 6, y - size // 8),
            (x - size // 8, y - size // 8)
        ]
        pygame.draw.polygon(screen, self.color, points)
    
    def _render_shield(self, screen, x, y, size):
        """Render shield power-up."""
        # Shield shape
        points = [
            (x, y - size // 2),
            (x + size // 3, y - size // 4),
            (x + size // 3, y + size // 4),
            (x, y + size // 2),
            (x - size // 3, y + size // 4),
            (x - size // 3, y - size // 4)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, self.secondary_color, points, 3)
    
    def _render_magnet(self, screen, x, y, size):
        """Render magnet power-up (horseshoe magnet)."""
        # U-shape magnet
        rect_width = size // 4
        rect_height = size // 2
        
        # Left bar
        pygame.draw.rect(screen, self.color, 
                        (x - size // 3, y - rect_height // 2, rect_width, rect_height))
        # Right bar
        pygame.draw.rect(screen, self.secondary_color,
                        (x + size // 3 - rect_width, y - rect_height // 2, rect_width, rect_height))
        # Bottom connector
        pygame.draw.rect(screen, self.color,
                        (x - size // 3, y + rect_height // 2 - rect_width, 
                         size * 2 // 3, rect_width))
    
    def _render_double_points(self, screen, x, y, size):
        """Render double points power-up (2x symbol)."""
        # Background circle
        pygame.draw.circle(screen, self.secondary_color, (x, y), size // 2)
        
        # Draw "2x" text
        font = pygame.font.Font(None, size)
        text = font.render("2x", True, self.color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    
    def _render_extra_jump(self, screen, x, y, size):
        """Render extra jump power-up (up arrow)."""
        # Background circle
        pygame.draw.circle(screen, self.secondary_color, (x, y), size // 2)
        
        # Up arrow
        points = [
            (x, y - size // 3),
            (x + size // 4, y),
            (x + size // 8, y),
            (x + size // 8, y + size // 3),
            (x - size // 8, y + size // 3),
            (x - size // 8, y),
            (x - size // 4, y)
        ]
        pygame.draw.polygon(screen, self.color, points)