"""
UI rendering system with animated elements.
"""
import pygame
import math
from src.utils.constants import *


class ScorePopup:
    """Animated score popup that appears when landing on platforms."""
    
    def __init__(self, x, y, score, combo=1, is_text=False):
        self.x = x
        self.y = y
        self.score = score
        self.combo = combo
        self.is_text = is_text  # If True, score is a text string
        self.lifetime = 0.0
        self.max_lifetime = 1.5 if is_text else 1.0  # Text lasts longer
        self.velocity_y = -80 if is_text else -100  # Float upward
        self.alpha = 255
    
    def update(self, dt):
        """Update popup animation."""
        self.lifetime += dt
        self.y += self.velocity_y * dt
        
        # Fade out in last 30% of lifetime
        fade_start = self.max_lifetime * 0.7
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            self.alpha = int(255 * (1 - fade_progress))
        
        return self.lifetime < self.max_lifetime
    
    def render(self, screen, font, camera_x, camera_y):
        """Render the popup."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Scale based on lifetime (pop in effect)
        scale = min(1.0, self.lifetime * 5)
        
        # Create text
        if self.is_text:
            # Display text message (for power-ups)
            text = str(self.score)
            color = (0, 255, 255)  # Cyan for power-ups
        elif self.combo > 1:
            text = f"+{self.score} x{self.combo}!"
            color = (255, 215, 0)  # Gold for combo
        else:
            text = f"+{self.score}"
            color = (255, 255, 255)
        
        # Render with alpha
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(self.alpha)
        
        # Apply scale
        if scale < 1.0:
            new_width = int(text_surface.get_width() * scale)
            new_height = int(text_surface.get_height() * scale)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        
        # Center text
        text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(text_surface, text_rect)


class UIRenderer:
    """
    Renders UI elements like score, buttons, and text with animations.
    """
    
    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.font_medium = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.font_small = pygame.font.Font(None, BUTTON_FONT_SIZE)
        
        # Animated elements
        self.score_popups = []
        self.combo_count = 0
        self.combo_timer = 0.0
        self.fade_alpha = 0  # For state transitions
        self.fade_direction = 0  # 0=none, 1=fade in, -1=fade out
    
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
    
    def add_score_popup(self, x, y, score, combo=1, is_text=False):
        """
        Add an animated score popup.
        
        Args:
            x, y: World position for popup
            score: Score value to display (or text string if is_text=True)
            combo: Combo multiplier
            is_text: If True, score is treated as a text message
        """
        self.score_popups.append(ScorePopup(x, y, score, combo, is_text))
    
    def update_score_popups(self, dt):
        """Update all score popups."""
        self.score_popups = [popup for popup in self.score_popups if popup.update(dt)]
    
    def render_score_popups(self, screen, camera_x, camera_y):
        """Render all score popups."""
        for popup in self.score_popups:
            popup.render(screen, self.font_small, camera_x, camera_y)
    
    def update_combo(self, dt):
        """Update combo timer."""
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
    
    def add_combo(self):
        """Increment combo counter."""
        self.combo_count += 1
        self.combo_timer = COMBO_TIMEOUT
    
    def get_combo_multiplier(self):
        """Get current combo multiplier that scales infinitely."""
        if self.combo_count <= 1:
            return 1
        elif self.combo_count <= 2:
            return 2
        elif self.combo_count <= 4:
            return 3
        elif self.combo_count <= 9:
            return 4
        elif self.combo_count <= 19:
            return 5
        else:
            # After 20 combo, add 1 multiplier for every 10 additional combos
            return 5 + ((self.combo_count - 20) // 10) + 1
    
    def render_combo(self, screen):
        """Render combo counter if active."""
        if self.combo_count > 1:
            # Pulse effect based on timer (faster pulse for higher combos)
            pulse_speed = min(10 + self.combo_count * 0.5, 20)
            pulse = 1.0 + 0.1 * math.sin(self.combo_timer * pulse_speed)
            
            # Color based on combo level with gradient
            if self.combo_count >= 20:
                # Rainbow effect for mega combos
                hue = (self.combo_timer * 100) % 360
                color = self._hsv_to_rgb(hue, 1.0, 1.0)
            elif self.combo_count >= 10:
                color = (255, 0, 255)  # Magenta
            elif self.combo_count >= 5:
                color = (255, 215, 0)  # Gold
            elif self.combo_count >= 3:
                color = (255, 165, 0)  # Orange
            else:
                color = (255, 255, 255)  # White
            
            multiplier = self.get_combo_multiplier()
            text = f"COMBO x{multiplier} ({self.combo_count})"
            
            # Larger font for higher combos
            base_size = BUTTON_FONT_SIZE
            if self.combo_count >= 10:
                base_size = int(BUTTON_FONT_SIZE * 1.3)
            
            font_size = int(base_size * pulse)
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(text, True, color)
            
            # Position at top center
            x = (screen.get_width() - text_surface.get_width()) // 2
            y = UI_PADDING + 60
            
            # Shadow
            shadow = font.render(text, True, UI_TEXT_SHADOW)
            screen.blit(shadow, (x + 2, y + 2))
            screen.blit(text_surface, (x, y))
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color to RGB tuple."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def render_speed_lines(self, screen, player_x, player_y, camera_x, camera_y, intensity=1.0):
        """
        Render speed lines effect during boost.
        
        Args:
            screen: pygame.Surface to draw on
            player_x, player_y: Player world position
            camera_x, camera_y: Camera position
            intensity: Line intensity (0-1)
        """
        if intensity <= 0:
            return
        
        # Convert to screen space
        screen_x = player_x - camera_x
        screen_y = player_y - camera_y
        
        # Draw horizontal speed lines
        num_lines = int(8 * intensity)
        for i in range(num_lines):
            # Random offset from player
            offset_y = (i - num_lines / 2) * 20
            line_y = screen_y + offset_y
            
            # Line length based on intensity
            line_length = int(100 * intensity)
            line_start_x = screen_x - 50
            line_end_x = line_start_x - line_length
            
            # Alpha based on intensity
            alpha = int(150 * intensity)
            color = (255, 255, 255, alpha)
            
            # Create surface with alpha
            line_surface = pygame.Surface((line_length, 3), pygame.SRCALPHA)
            pygame.draw.line(line_surface, color, (0, 1), (line_length, 1), 3)
            screen.blit(line_surface, (line_end_x, line_y))
    
    def start_fade(self, fade_in=True):
        """Start a fade transition."""
        if fade_in:
            self.fade_alpha = 255
            self.fade_direction = -1
        else:
            self.fade_alpha = 0
            self.fade_direction = 1
    
    def update_fade(self, dt):
        """Update fade transition."""
        if self.fade_direction != 0:
            fade_speed = 500  # Alpha units per second
            self.fade_alpha += self.fade_direction * fade_speed * dt
            
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_direction = 0
            elif self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_direction = 0
    
    def render_fade(self, screen):
        """Render fade overlay."""
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(fade_surface, (0, 0))
    
    def is_fading(self):
        """Check if currently fading."""
        return self.fade_direction != 0