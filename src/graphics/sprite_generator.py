"""
Procedural sprite generation for all game graphics.
Creates modern pixel art style sprites at runtime.
"""
import pygame
import math
from src.utils.constants import *
from typing import Dict, Tuple, Optional


class SpriteGenerator:
    """
    Generates all game sprites procedurally.
    No external assets needed - everything is drawn programmatically.
    """
    
    def __init__(self, player_colors: Optional[Dict[str, Tuple[int, int, int]]] = None,
                 platform_colors: Optional[Dict[str, Tuple[int, int, int]]] = None):
        """
        Initialize sprite generator with optional custom colors.
        
        Args:
            player_colors: Dictionary with 'primary', 'secondary', 'accent', 'outline' colors
            platform_colors: Dictionary with platform color scheme
        """
        self.sprite_cache = {}
        self.platform_cache = {}  # Cache for different platform sizes
        self.particle_cache = {}  # Cache for particles
        self.player_colors = player_colors or {
            'primary': PLAYER_PRIMARY,
            'secondary': PLAYER_SECONDARY,
            'accent': PLAYER_ACCENT,
            'outline': PLAYER_OUTLINE,
        }
        self.platform_colors = platform_colors or {
            'base': PLATFORM_BASE,
            'highlight': PLATFORM_HIGHLIGHT,
            'top': PLATFORM_GRASS,
            'moving': PLATFORM_MOVING,
            'small': PLATFORM_SMALL,
            'crumbling': PLATFORM_CRUMBLING,
        }
    
    def set_player_colors(self, colors: Dict[str, Tuple[int, int, int]]):
        """Update player colors and clear related caches."""
        self.player_colors = colors
        self.sprite_cache.pop('player', None)
        self.particle_cache.clear()  # Particles may use player colors
    
    def set_platform_colors(self, colors: Dict[str, Tuple[int, int, int]]):
        """Update platform colors and clear related caches."""
        self.platform_colors = colors
        self.sprite_cache.pop('platforms', None)
        self.platform_cache.clear()  # Clear platform size cache
    
    def generate_all_sprites(self):
        """
        Generate all game sprites and cache them.
        
        Returns:
            Dictionary of sprite collections
        """
        sprites = {
            'player': self.generate_player_sprites(),
            'platforms': self.generate_platform_sprites(),
            'particles': self.generate_particle_sprites(),
        }
        
        self.sprite_cache = sprites
        return sprites
    
    def generate_player_sprites(self):
        """
        Generate all player animation frames.
        
        Returns:
            Dictionary mapping animation names to frame lists
        """
        return {
            'idle': self._generate_idle_frames(),
            'running': self._generate_run_frames(),
            'jumping': self._generate_jump_frames(),
            'double_jumping': self._generate_double_jump_frames(),
            'helicopter': self._generate_helicopter_frames(),
            'falling': self._generate_fall_frames(),
        }
    
    def _generate_idle_frames(self):
        """Generate 4-frame idle animation with breathing motion."""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Breathing offset
            offset_y = int(math.sin(i * math.pi / 2) * 2)
            
            # Body (rounded rectangle)
            body_rect = pygame.Rect(8, 8 + offset_y, 16, 20)
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Eyes
            pygame.draw.circle(surface, self.player_colors['accent'], (13, 14 + offset_y), 2)
            pygame.draw.circle(surface, self.player_colors['accent'], (19, 14 + offset_y), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (13, 14 + offset_y), 2, 1)
            pygame.draw.circle(surface, self.player_colors['outline'], (19, 14 + offset_y), 2, 1)
            
            # Scale up
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_run_frames(self):
        """Generate 6-frame run cycle with bobbing motion."""
        frames = []
        for i in range(6):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Bobbing motion
            bob = int(math.sin(i * math.pi / 3) * 3)
            
            # Body
            body_rect = pygame.Rect(8, 6 + bob, 16, 20)
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Legs (alternating)
            leg_offset = 2 if i % 2 == 0 else -2
            # Left leg
            pygame.draw.rect(surface, self.player_colors['secondary'],
                (11 + leg_offset, 24 + bob, 4, 6))
            # Right leg
            pygame.draw.rect(surface, self.player_colors['secondary'],
                (17 - leg_offset, 24 + bob, 4, 6))
            
            # Eyes
            pygame.draw.circle(surface, self.player_colors['accent'], (13, 12 + bob), 2)
            pygame.draw.circle(surface, self.player_colors['accent'], (19, 12 + bob), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (13, 12 + bob), 2, 1)
            pygame.draw.circle(surface, self.player_colors['outline'], (19, 12 + bob), 2, 1)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_jump_frames(self):
        """Generate 3-frame jump animation."""
        frames = []
        for i in range(3):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Squash and stretch
            if i == 0:  # Anticipation
                body_rect = pygame.Rect(7, 10, 18, 18)
            elif i == 1:  # Peak
                body_rect = pygame.Rect(9, 6, 14, 22)
            else:  # Falling
                body_rect = pygame.Rect(8, 8, 16, 20)
            
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Eyes (excited)
            eye_y = body_rect.top + 6
            pygame.draw.circle(surface, self.player_colors['accent'], (13, eye_y), 2)
            pygame.draw.circle(surface, self.player_colors['accent'], (19, eye_y), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (13, eye_y), 2, 1)
            pygame.draw.circle(surface, self.player_colors['outline'], (19, eye_y), 2, 1)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_double_jump_frames(self):
        """Generate 4-frame double jump with spin."""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Body (slightly rotated appearance based on frame)
            if i % 2 == 0:
                body_rect = pygame.Rect(8, 8, 16, 20)
            else:
                body_rect = pygame.Rect(10, 8, 12, 20)
            
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Eyes
            pygame.draw.circle(surface, self.player_colors['accent'], (16, 14), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (16, 14), 2, 1)
            
            # Motion lines
            for j in range(3):
                line_y = 10 + j * 6
                pygame.draw.line(surface, self.player_colors['secondary'],
                    (4, line_y), (8, line_y), 2)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_helicopter_frames(self):
        """Generate 8-frame helicopter animation with smooth spinning rotor."""
        frames = []
        for i in range(8):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT + 8), pygame.SRCALPHA)
            
            # Body with slight bobbing motion
            bob = int(math.sin(i * math.pi / 4) * 1)
            body_rect = pygame.Rect(8, 12 + bob, 16, 18)
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Rotor (spinning) - 45 degrees per frame for smooth rotation
            rotor_angle = i * 45
            rotor_length = 12
            center_x, center_y = 16, 8 + bob
            
            # Draw rotor blades
            for angle in [rotor_angle, rotor_angle + 180]:
                rad = math.radians(angle)
                end_x = center_x + math.cos(rad) * rotor_length
                end_y = center_y + math.sin(rad) * rotor_length
                pygame.draw.line(surface, self.player_colors['accent'],
                    (center_x, center_y), (end_x, end_y), 3)
                pygame.draw.line(surface, self.player_colors['outline'],
                    (center_x, center_y), (end_x, end_y), 1)
            
            # Rotor center
            pygame.draw.circle(surface, self.player_colors['secondary'], (center_x, center_y), 3)
            pygame.draw.circle(surface, self.player_colors['outline'], (center_x, center_y), 3, 1)
            
            # Eyes (determined)
            pygame.draw.circle(surface, self.player_colors['accent'], (13, 18 + bob), 2)
            pygame.draw.circle(surface, self.player_colors['accent'], (19, 18 + bob), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (13, 18 + bob), 2, 1)
            pygame.draw.circle(surface, self.player_colors['outline'], (19, 18 + bob), 2, 1)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, (PLAYER_HEIGHT + 8) * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_fall_frames(self):
        """Generate falling animation (similar to jump but stretched)."""
        frames = []
        for i in range(2):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Stretched body
            body_rect = pygame.Rect(9, 6, 14, 24)
            pygame.draw.rect(surface, self.player_colors['primary'], body_rect, border_radius=4)
            pygame.draw.rect(surface, self.player_colors['outline'], body_rect, 2, border_radius=4)
            
            # Eyes (worried)
            pygame.draw.circle(surface, self.player_colors['accent'], (13, 12), 2)
            pygame.draw.circle(surface, self.player_colors['accent'], (19, 12), 2)
            pygame.draw.circle(surface, self.player_colors['outline'], (13, 12), 2, 1)
            pygame.draw.circle(surface, self.player_colors['outline'], (19, 12), 2, 1)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def generate_platform_sprites(self):
        """
        Generate platform sprites for different types.
        
        Returns:
            Dictionary of platform type sprites
        """
        return {
            'static': self._generate_static_platform(),
            'moving': self._generate_moving_platform(),
            'small': self._generate_small_platform(),
            'crumbling': self._generate_crumbling_platform(),
        }
    
    def _generate_static_platform(self):
        """Generate standard platform sprite."""
        return self._generate_platform_with_size('static', MAX_PLATFORM_WIDTH)
    
    def _generate_platform_with_size(self, platform_type: str, width: int):
        """
        Generate platform sprite with specific width (cached).
        
        Args:
            platform_type: Type of platform ('static', 'moving', 'small', 'crumbling')
            width: Width of the platform
        
        Returns:
            Cached or newly generated platform sprite
        """
        cache_key = f"{platform_type}_{width}"
        
        # Check cache first
        if cache_key in self.platform_cache:
            return self.platform_cache[cache_key]
        
        height = PLATFORM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw based on platform type
        if platform_type == 'static':
            pygame.draw.rect(surface, self.platform_colors['top'], (0, 0, width, 4))
            pygame.draw.rect(surface, self.platform_colors['base'], (0, 4, width, height - 4))
            pygame.draw.rect(surface, self.platform_colors['highlight'], (0, 4, width, 2))
        elif platform_type == 'moving':
            pygame.draw.rect(surface, self.platform_colors['moving'], (0, 0, width, 4))
            pygame.draw.rect(surface, self.platform_colors['base'], (0, 4, width, height - 4))
            pygame.draw.rect(surface, self.platform_colors['highlight'], (0, 4, width, 2))
            # Arrows to indicate movement
            for x in range(10, width - 10, 20):
                pygame.draw.polygon(surface, self.platform_colors['moving'],
                    [(x, 8), (x + 4, 12), (x, 16)])
        elif platform_type == 'small':
            pygame.draw.rect(surface, self.platform_colors['small'], (0, 0, width, 4))
            pygame.draw.rect(surface, self.platform_colors['base'], (0, 4, width, height - 4))
            pygame.draw.rect(surface, self.platform_colors['highlight'], (0, 4, width, 2))
        elif platform_type == 'crumbling':
            pygame.draw.rect(surface, self.platform_colors['crumbling'], (0, 0, width, 4))
            pygame.draw.rect(surface, self.platform_colors['base'], (0, 4, width, height - 4))
            # Cracks
            for x in range(5, width, 15):
                pygame.draw.line(surface, self.player_colors['outline'], (x, 6), (x + 3, 10), 1)
                pygame.draw.line(surface, self.player_colors['outline'], (x + 3, 10), (x + 1, 14), 1)
        
        # Scale up
        scaled = pygame.transform.scale(surface,
            (width * PLATFORM_SCALE, height * PLATFORM_SCALE))
        
        # Cache the result
        self.platform_cache[cache_key] = scaled
        
        return scaled
    
    def _generate_moving_platform(self):
        """Generate moving platform with purple tint."""
        return self._generate_platform_with_size('moving', MAX_PLATFORM_WIDTH)
    
    def _generate_small_platform(self):
        """Generate small platform with yellow tint."""
        return self._generate_platform_with_size('small', SMALL_PLATFORM_WIDTH)
    
    def _generate_crumbling_platform(self):
        """Generate crumbling platform with red tint and cracks."""
        return self._generate_platform_with_size('crumbling', MAX_PLATFORM_WIDTH)
    
    def generate_particle_sprites(self):
        """
        Generate particle sprites.
        
        Returns:
            Dictionary of particle type sprites
        """
        return {
            'dust': self._generate_dust_particle(),
            'helicopter': self._generate_helicopter_particle(),
            'splash': self._generate_splash_particle(),
        }
    
    def _generate_dust_particle(self):
        """Generate dust particle sprite (cached)."""
        if 'dust' in self.particle_cache:
            return self.particle_cache['dust']
        
        size = 8
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_DUST, (size // 2, size // 2), size // 2)
        self.particle_cache['dust'] = surface
        return surface
    
    def _generate_helicopter_particle(self):
        """Generate helicopter trail particle (cached)."""
        if 'helicopter' in self.particle_cache:
            return self.particle_cache['helicopter']
        
        size = 12
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_HELICOPTER, (size // 2, size // 2), size // 2)
        self.particle_cache['helicopter'] = surface
        return surface
    
    def _generate_splash_particle(self):
        """Generate water splash particle (cached)."""
        if 'splash' in self.particle_cache:
            return self.particle_cache['splash']
        
        size = 16
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_SPLASH, (size // 2, size // 2), size // 2)
        self.particle_cache['splash'] = surface
        return surface
    
    def get_cached_platform(self, platform_type: str, width: int):
        """
        Get a cached platform sprite or generate if not cached.
        
        Args:
            platform_type: Type of platform
            width: Width of the platform
        
        Returns:
            Platform sprite surface
        """
        return self._generate_platform_with_size(platform_type, width)
    
    def clear_cache(self):
        """Clear all sprite caches to free memory."""
        self.sprite_cache.clear()
        self.platform_cache.clear()
        self.particle_cache.clear()
