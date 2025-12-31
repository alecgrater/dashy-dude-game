"""
UI rendering system.
"""
import pygame
from src.utils.constants import *


class UIRenderer:
    """
    Renders UI elements like score, buttons, and text.
    """
    
    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.font_medium = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.font_small = pygame.font.Font(None, BUTTON_FONT_SIZE)
    
    def render_score(self, screen, score):
        """
        Render score display.
        
        Args:
            screen: pygame.Surface to draw on
            score: Current score value
        """
        score_text = self.font_medium.render(f"Score: {score}", True, UI_TEXT)
        score_shadow = self.font_medium.render(f"Score: {score}", True, UI_TEXT_SHADOW)
        
        # Draw shadow
        screen.blit(score_shadow, (UI_PADDING + 2, UI_PADDING + 2))
        # Draw text
        screen.blit(score_text, (UI_PADDING, UI_PADDING))
    
    def render_title(self, screen, title):
        """
        Render large title text.
        
        Args:
            screen: pygame.Surface to draw on
            title: Title string
        """
        text = self.font_large.render(title, True, UI_TEXT)
        shadow = self.font_large.render(title, True, UI_TEXT_SHADOW)
        
        # Center on screen
        x = (screen.get_width() - text.get_width()) // 2
        y = screen.get_height() // 4
        
        screen.blit(shadow, (x + 3, y + 3))
        screen.blit(text, (x, y))
    
    def render_button(self, screen, text, x, y, width, height, hovered=False):
        """
        Render a button.
        
        Args:
            screen: pygame.Surface to draw on
            text: Button text
            x, y: Button position
            width, height: Button dimensions
            hovered: Whether mouse is hovering over button
        
        Returns:
            pygame.Rect of button for collision detection
        """
        button_rect = pygame.Rect(x, y, width, height)
        
        # Button color
        color = UI_ACCENT if hovered else UI_PRIMARY
        
        # Draw button
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, UI_TEXT, button_rect, 3, border_radius=10)
        
        # Draw text
        text_surface = self.font_small.render(text, True, UI_TEXT)
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        return button_rect
    
    def render_text(self, screen, text, x, y, font_size="medium", color=UI_TEXT):
        """
        Render text at position.
        
        Args:
            screen: pygame.Surface to draw on
            text: Text string
            x, y: Position
            font_size: "large", "medium", or "small"
            color: Text color
        """
        if font_size == "large":
            font = self.font_large
        elif font_size == "small":
            font = self.font_small
        else:
            font = self.font_medium
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
    
    def render_centered_text(self, screen, text, y, font_size="medium", color=UI_TEXT, shadow=True):
        """
        Render text centered horizontally on screen.
        
        Args:
            screen: pygame.Surface to draw on
            text: Text string
            y: Vertical position
            font_size: "large", "medium", or "small"
            color: Text color
            shadow: Whether to render shadow
        
        Returns:
            pygame.Rect of rendered text
        """
        if font_size == "large":
            font = self.font_large
        elif font_size == "small":
            font = self.font_small
        else:
            font = self.font_medium
        
        text_surface = font.render(text, True, color)
        x = (screen.get_width() - text_surface.get_width()) // 2
        
        # Draw shadow if requested
        if shadow:
            shadow_surface = font.render(text, True, UI_TEXT_SHADOW)
            screen.blit(shadow_surface, (x + 2, y + 2))
        
        # Draw text
        screen.blit(text_surface, (x, y))
        
        return pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
    
    def render_animated_title(self, screen, text, y, scale=1.0, color=UI_ACCENT):
        """
        Render large animated title with effects.
        
        Args:
            screen: pygame.Surface to draw on
            text: Title text
            y: Vertical position
            scale: Scale factor for animation
            color: Text color
        """
        font_size = int(TITLE_FONT_SIZE * scale)
        font = pygame.font.Font(None, font_size)
        
        # Render shadow
        shadow = font.render(text, True, UI_TEXT_SHADOW)
        shadow_rect = shadow.get_rect(center=(screen.get_width() // 2 + 4, y + 4))
        screen.blit(shadow, shadow_rect)
        
        # Render main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y))
        screen.blit(text_surface, text_rect)