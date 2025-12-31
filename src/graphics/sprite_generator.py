"""
Procedural sprite generation for all game graphics.
Creates modern pixel art style sprites at runtime.
"""
import pygame
import math
from src.utils.constants import *


class SpriteGenerator:
    """
    Generates all game sprites procedurally.
    No external assets needed - everything is drawn programmatically.
    """
    
    def __init__(self):
        self.sprite_cache = {}
    
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
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Eyes
            pygame.draw.circle(surface, PLAYER_ACCENT, (13, 14 + offset_y), 2)
            pygame.draw.circle(surface, PLAYER_ACCENT, (19, 14 + offset_y), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (13, 14 + offset_y), 2, 1)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (19, 14 + offset_y), 2, 1)
            
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
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Legs (alternating)
            leg_offset = 2 if i % 2 == 0 else -2
            # Left leg
            pygame.draw.rect(surface, PLAYER_SECONDARY,
                (11 + leg_offset, 24 + bob, 4, 6))
            # Right leg
            pygame.draw.rect(surface, PLAYER_SECONDARY,
                (17 - leg_offset, 24 + bob, 4, 6))
            
            # Eyes
            pygame.draw.circle(surface, PLAYER_ACCENT, (13, 12 + bob), 2)
            pygame.draw.circle(surface, PLAYER_ACCENT, (19, 12 + bob), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (13, 12 + bob), 2, 1)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (19, 12 + bob), 2, 1)
            
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
            
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Eyes (excited)
            eye_y = body_rect.top + 6
            pygame.draw.circle(surface, PLAYER_ACCENT, (13, eye_y), 2)
            pygame.draw.circle(surface, PLAYER_ACCENT, (19, eye_y), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (13, eye_y), 2, 1)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (19, eye_y), 2, 1)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_double_jump_frames(self):
        """Generate 4-frame double jump with spin."""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            
            # Rotation effect
            angle = i * 90
            
            # Body (slightly rotated appearance)
            if i % 2 == 0:
                body_rect = pygame.Rect(8, 8, 16, 20)
            else:
                body_rect = pygame.Rect(10, 8, 12, 20)
            
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Eyes
            pygame.draw.circle(surface, PLAYER_ACCENT, (16, 14), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (16, 14), 2, 1)
            
            # Motion lines
            for j in range(3):
                line_y = 10 + j * 6
                pygame.draw.line(surface, PLAYER_SECONDARY,
                    (4, line_y), (8, line_y), 2)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
        
        return frames
    
    def _generate_helicopter_frames(self):
        """Generate 4-frame helicopter animation with spinning rotor."""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT + 8), pygame.SRCALPHA)
            
            # Body
            body_rect = pygame.Rect(8, 12, 16, 18)
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Rotor (spinning)
            rotor_angle = i * 90
            rotor_length = 12
            center_x, center_y = 16, 8
            
            # Draw rotor blades
            for angle in [rotor_angle, rotor_angle + 180]:
                rad = math.radians(angle)
                end_x = center_x + math.cos(rad) * rotor_length
                end_y = center_y + math.sin(rad) * rotor_length
                pygame.draw.line(surface, PLAYER_ACCENT,
                    (center_x, center_y), (end_x, end_y), 3)
                pygame.draw.line(surface, PLAYER_OUTLINE,
                    (center_x, center_y), (end_x, end_y), 1)
            
            # Rotor center
            pygame.draw.circle(surface, PLAYER_SECONDARY, (center_x, center_y), 3)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (center_x, center_y), 3, 1)
            
            # Eyes (determined)
            pygame.draw.circle(surface, PLAYER_ACCENT, (13, 18), 2)
            pygame.draw.circle(surface, PLAYER_ACCENT, (19, 18), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (13, 18), 2, 1)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (19, 18), 2, 1)
            
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
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2, border_radius=4)
            
            # Eyes (worried)
            pygame.draw.circle(surface, PLAYER_ACCENT, (13, 12), 2)
            pygame.draw.circle(surface, PLAYER_ACCENT, (19, 12), 2)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (13, 12), 2, 1)
            pygame.draw.circle(surface, PLAYER_OUTLINE, (19, 12), 2, 1)
            
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
        width = MAX_PLATFORM_WIDTH
        height = PLATFORM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Grass top
        pygame.draw.rect(surface, PLATFORM_GRASS, (0, 0, width, 4))
        
        # Main body
        pygame.draw.rect(surface, PLATFORM_BASE, (0, 4, width, height - 4))
        
        # Highlight
        pygame.draw.rect(surface, PLATFORM_HIGHLIGHT, (0, 4, width, 2))
        
        # Scale up
        scaled = pygame.transform.scale(surface,
            (width * PLATFORM_SCALE, height * PLATFORM_SCALE))
        
        return scaled
    
    def _generate_moving_platform(self):
        """Generate moving platform with purple tint."""
        width = MAX_PLATFORM_WIDTH
        height = PLATFORM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Purple grass top
        pygame.draw.rect(surface, PLATFORM_MOVING, (0, 0, width, 4))
        
        # Main body
        pygame.draw.rect(surface, PLATFORM_BASE, (0, 4, width, height - 4))
        
        # Highlight
        pygame.draw.rect(surface, PLATFORM_HIGHLIGHT, (0, 4, width, 2))
        
        # Arrows to indicate movement
        for x in range(10, width - 10, 20):
            pygame.draw.polygon(surface, PLATFORM_MOVING,
                [(x, 8), (x + 4, 12), (x, 16)])
        
        scaled = pygame.transform.scale(surface,
            (width * PLATFORM_SCALE, height * PLATFORM_SCALE))
        
        return scaled
    
    def _generate_small_platform(self):
        """Generate small platform with yellow tint."""
        width = SMALL_PLATFORM_WIDTH
        height = PLATFORM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Yellow grass top
        pygame.draw.rect(surface, PLATFORM_SMALL, (0, 0, width, 4))
        
        # Main body
        pygame.draw.rect(surface, PLATFORM_BASE, (0, 4, width, height - 4))
        
        # Highlight
        pygame.draw.rect(surface, PLATFORM_HIGHLIGHT, (0, 4, width, 2))
        
        scaled = pygame.transform.scale(surface,
            (width * PLATFORM_SCALE, height * PLATFORM_SCALE))
        
        return scaled
    
    def _generate_crumbling_platform(self):
        """Generate crumbling platform with red tint and cracks."""
        width = MAX_PLATFORM_WIDTH
        height = PLATFORM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Red grass top
        pygame.draw.rect(surface, PLATFORM_CRUMBLING, (0, 0, width, 4))
        
        # Main body
        pygame.draw.rect(surface, PLATFORM_BASE, (0, 4, width, height - 4))
        
        # Cracks
        for x in range(5, width, 15):
            pygame.draw.line(surface, PLAYER_OUTLINE, (x, 6), (x + 3, 10), 1)
            pygame.draw.line(surface, PLAYER_OUTLINE, (x + 3, 10), (x + 1, 14), 1)
        
        scaled = pygame.transform.scale(surface,
            (width * PLATFORM_SCALE, height * PLATFORM_SCALE))
        
        return scaled
    
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
        """Generate dust particle sprite."""
        size = 8
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_DUST, (size // 2, size // 2), size // 2)
        return surface
    
    def _generate_helicopter_particle(self):
        """Generate helicopter trail particle."""
        size = 12
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_HELICOPTER, (size // 2, size // 2), size // 2)
        return surface
    
    def _generate_splash_particle(self):
        """Generate water splash particle."""
        size = 16
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, PARTICLE_SPLASH, (size // 2, size // 2), size // 2)
        return surface