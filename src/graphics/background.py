"""
Background rendering with parallax scrolling.
"""
import pygame
import math
from src.utils.constants import *
from typing import Dict, Tuple, Optional


class Background:
    """
    Renders layered background with parallax scrolling effect.
    """
    
    def __init__(self, width, height, colors: Optional[Dict[str, Tuple[int, int, int]]] = None):
        """
        Initialize background with optional custom colors.
        
        Args:
            width: Screen width
            height: Screen height
            colors: Dictionary with 'sky_top', 'sky_bottom', 'water_dark', 'water_light' colors
        """
        self.width = width
        self.height = height
        self.colors = colors or {
            'sky_top': SKY_TOP,
            'sky_bottom': SKY_BOTTOM,
            'water_dark': WATER_DARK,
            'water_light': WATER_LIGHT,
        }
        self.sky_surface = self._create_sky_gradient()
        self.water_offset = 0.0
    
    def set_colors(self, colors: Dict[str, Tuple[int, int, int]]):
        """Update background colors and regenerate gradient."""
        self.colors = colors
        self.sky_surface = self._create_sky_gradient()
    
    def _create_sky_gradient(self):
        """Create sky gradient surface."""
        surface = pygame.Surface((self.width, self.height))
        
        # Draw gradient from top to bottom
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(self.colors['sky_top'][0] + (self.colors['sky_bottom'][0] - self.colors['sky_top'][0]) * ratio),
                int(self.colors['sky_top'][1] + (self.colors['sky_bottom'][1] - self.colors['sky_top'][1]) * ratio),
                int(self.colors['sky_top'][2] + (self.colors['sky_bottom'][2] - self.colors['sky_top'][2]) * ratio),
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))
        
        return surface
    
    def update(self, dt):
        """
        Update animated background elements.
        
        Args:
            dt: Delta time in seconds
        """
        # Animate water
        self.water_offset += dt * 50  # Slow wave animation
    
    def render(self, screen, camera):
        """
        Render background layers.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        # Sky (static)
        screen.blit(self.sky_surface, (0, 0))
        
        # Water surface
        self._render_water(screen, camera)
    
    def _render_water(self, screen, camera):
        """Render water surface with waves."""
        water_y = WATER_LEVEL - camera.position.y
        
        if water_y < self.height:
            # Water body
            water_rect = pygame.Rect(0, int(water_y), self.width,
                                     self.height - int(water_y))
            pygame.draw.rect(screen, self.colors['water_dark'], water_rect)
            
            # Animated wave surface
            wave_points = []
            for x in range(0, self.width + 10, 10):
                wave_offset = math.sin((x + self.water_offset) * 0.05) * WATER_WAVE_AMPLITUDE
                wave_points.append((x, water_y + wave_offset))
            
            # Draw wave line
            if len(wave_points) > 1:
                pygame.draw.lines(screen, self.colors['water_light'], False, wave_points, 3)