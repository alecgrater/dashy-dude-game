"""
UI rendering system with animated elements.
"""
import pygame
import math
from src.utils.constants import *


class ScorePopup:
    """Animated score popup with AAA-game-quality effects."""
    
    def __init__(self, x, y, score, combo=1, is_text=False):
        self.x = x
        self.y = y
        self.initial_y = y
        self.score = score
        self.combo = combo
        self.is_text = is_text  # If True, score is a text string
        self.lifetime = 0.0
        self.max_lifetime = 2.0 if is_text else 1.5  # Longer for better visibility
        self.velocity_y = -120 if is_text else -150  # Faster upward movement
        self.alpha = 255
        
        # Enhanced animation properties
        self.scale = 0.0  # Start from 0 for pop-in effect
        self.rotation = 0.0
        self.glow_intensity = 1.0
        self.shake_x = 0.0
        self.shake_y = 0.0
        
        # Particle-like trail effect
        self.trail_positions = []
        self.trail_max = 5
    
    def update(self, dt):
        """Update popup animation with advanced effects."""
        self.lifetime += dt
        progress = self.lifetime / self.max_lifetime
        
        # Store trail positions for motion blur effect
        if len(self.trail_positions) >= self.trail_max:
            self.trail_positions.pop(0)
        self.trail_positions.append((self.x, self.y, self.alpha * 0.3))
        
        # Movement with easing
        if self.lifetime < 0.3:
            # Quick pop-up phase with overshoot
            ease_progress = self.lifetime / 0.3
            ease_factor = 1.0 - (1.0 - ease_progress) ** 3  # Cubic ease-out
            self.y = self.initial_y + self.velocity_y * ease_factor * 0.3
        else:
            # Slower float upward
            self.y += self.velocity_y * dt * 0.5
        
        # Elastic pop-in scale animation
        if self.lifetime < 0.2:
            # Overshoot scale for impact
            t = self.lifetime / 0.2
            self.scale = 1.0 + 0.5 * math.sin(t * math.pi * 2) * (1.0 - t)
            self.scale = max(0.0, min(1.5, self.scale))
        elif self.lifetime < 0.4:
            # Settle to normal size
            t = (self.lifetime - 0.2) / 0.2
            self.scale = 1.5 - 0.5 * t
        else:
            # Slight pulse during display
            pulse = 1.0 + 0.05 * math.sin(self.lifetime * 10)
            self.scale = 1.0 * pulse
        
        # Rotation for combo/power-up text
        if self.is_text or self.combo > 1:
            self.rotation = math.sin(self.lifetime * 8) * 5  # Gentle wobble
        
        # Glow pulse effect
        self.glow_intensity = 0.5 + 0.5 * math.sin(self.lifetime * 12)
        
        # Micro shake for impact
        if self.lifetime < 0.15:
            shake_amount = (0.15 - self.lifetime) * 20
            self.shake_x = (math.sin(self.lifetime * 50) * shake_amount)
            self.shake_y = (math.cos(self.lifetime * 50) * shake_amount)
        else:
            self.shake_x = 0
            self.shake_y = 0
        
        # Fade out in last 40% of lifetime with smooth curve
        fade_start = self.max_lifetime * 0.6
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            # Smooth fade curve
            fade_curve = 1.0 - fade_progress ** 2
            self.alpha = int(255 * fade_curve)
        
        return self.lifetime < self.max_lifetime
    
    def render(self, screen, font, camera_x, camera_y):
        """Render the popup with advanced visual effects."""
        screen_x = self.x - camera_x + self.shake_x
        screen_y = self.y - camera_y + self.shake_y
        
        # Determine text and colors based on type
        if self.is_text:
            # Power-up text with gradient effect
            text = str(self.score).upper()
            base_color = (0, 255, 255)  # Cyan
            glow_color = (255, 255, 0)  # Yellow glow
            font_size = 52  # Larger for power-ups
        elif self.combo > 1:
            text = f"+{self.score} ×{self.combo}!"
            # Color based on combo level
            if self.combo >= 5:
                base_color = (255, 50, 255)  # Magenta for high combos
                glow_color = (255, 200, 0)  # Gold glow
            else:
                base_color = (255, 215, 0)  # Gold
                glow_color = (255, 100, 0)  # Orange glow
            font_size = 48 + min(self.combo * 2, 20)  # Larger for higher combos
        else:
            text = f"+{self.score}"
            base_color = (255, 255, 255)  # White
            glow_color = (200, 200, 255)  # Slight blue glow
            font_size = 44
        
        # Create larger font for better readability
        display_font = pygame.font.Font(None, int(font_size * self.scale))
        
        # Render glow layers for depth (multiple passes)
        glow_alpha = int(self.alpha * self.glow_intensity * 0.6)
        for glow_offset in [8, 6, 4, 2]:
            glow_surface = display_font.render(text, True, glow_color)
            glow_surface.set_alpha(glow_alpha // (glow_offset // 2))
            glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
            
            # Draw glow in all directions
            for dx, dy in [(glow_offset, 0), (-glow_offset, 0), (0, glow_offset), (0, -glow_offset),
                          (glow_offset, glow_offset), (-glow_offset, -glow_offset),
                          (glow_offset, -glow_offset), (-glow_offset, glow_offset)]:
                screen.blit(glow_surface, (glow_rect.x + dx, glow_rect.y + dy))
        
        # Render thick black outline for readability (stroke effect)
        outline_color = (0, 0, 0)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2), (3, 0), (-3, 0), (0, 3), (0, -3)]:
            outline_surface = display_font.render(text, True, outline_color)
            outline_surface.set_alpha(self.alpha)
            outline_rect = outline_surface.get_rect(center=(int(screen_x + offset[0]), int(screen_y + offset[1])))
            screen.blit(outline_surface, outline_rect)
        
        # Render main text with full alpha
        text_surface = display_font.render(text, True, base_color)
        text_surface.set_alpha(self.alpha)
        
        # Apply rotation if needed
        if abs(self.rotation) > 0.1:
            text_surface = pygame.transform.rotate(text_surface, self.rotation)
        
        # Center and draw main text
        text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(text_surface, text_rect)
        
        # Render motion trail for extra juice
        if len(self.trail_positions) > 1:
            for i, (tx, ty, trail_alpha) in enumerate(self.trail_positions[:-1]):
                trail_screen_x = tx - camera_x
                trail_screen_y = ty - camera_y
                trail_scale = self.scale * (0.5 + 0.5 * (i / len(self.trail_positions)))
                trail_font = pygame.font.Font(None, int(font_size * trail_scale))
                trail_surface = trail_font.render(text, True, base_color)
                trail_surface.set_alpha(int(trail_alpha))
                trail_rect = trail_surface.get_rect(center=(int(trail_screen_x), int(trail_screen_y)))
                screen.blit(trail_surface, trail_rect)


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
    
    def render_score(self, screen, score, high_score=0):
        """
        Render score display with optional high score.
        
        Args:
            screen: pygame.Surface to draw on
            score: Current score value
            high_score: High score to display (optional)
        """
        score_text = self.font_medium.render(f"Score: {score}", True, UI_TEXT)
        score_shadow = self.font_medium.render(f"Score: {score}", True, UI_TEXT_SHADOW)
        
        # Draw shadow
        screen.blit(score_shadow, (UI_PADDING + 2, UI_PADDING + 2))
        # Draw text
        screen.blit(score_text, (UI_PADDING, UI_PADDING))
        
        # Draw high score below current score if available
        if high_score > 0:
            high_score_text = self.font_small.render(f"Best: {high_score}", True, UI_ACCENT)
            high_score_shadow = self.font_small.render(f"Best: {high_score}", True, UI_TEXT_SHADOW)
            
            y_offset = UI_PADDING + 40
            screen.blit(high_score_shadow, (UI_PADDING + 2, y_offset + 2))
            screen.blit(high_score_text, (UI_PADDING, y_offset))
    
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
            
            # Larger font for higher combos (moderate increase)
            base_size = BUTTON_FONT_SIZE
            if self.combo_count >= 10:
                base_size = int(BUTTON_FONT_SIZE * 1.3)
            
            font_size = int(base_size * pulse)
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(text, True, color)
            
            # Position at top center
            x = (screen.get_width() - text_surface.get_width()) // 2
            y = UI_PADDING + 60
            
            # Shadow for combo text
            shadow = font.render(text, True, UI_TEXT_SHADOW)
            screen.blit(shadow, (x + 2, y + 2))
            screen.blit(text_surface, (x, y))
            
            # Render timer text with bigger font
            timer_text = f"{self.combo_timer:.1f}s"
            timer_font_size = int(base_size * 1.2 * pulse)  # Bigger timer text
            timer_font = pygame.font.Font(None, timer_font_size)
            
            # Timer color changes based on urgency
            if self.combo_timer < 0.5:
                timer_color = (255, 50, 50)  # Red - urgent!
            elif self.combo_timer < 1.0:
                timer_color = (255, 165, 0)  # Orange - warning
            else:
                timer_color = (100, 255, 100)  # Green - safe
            
            timer_surface = timer_font.render(timer_text, True, timer_color)
            
            # Position timer to the right of combo text with some spacing
            timer_x = x + text_surface.get_width() + 20
            timer_y = y + (text_surface.get_height() - timer_surface.get_height()) // 2
            
            # Calculate bubble dimensions to fit only the timer
            bubble_padding = 20
            bubble_width = timer_surface.get_width() + bubble_padding * 2
            bubble_height = timer_surface.get_height() + bubble_padding * 2
            bubble_x = timer_x - bubble_padding
            bubble_y = timer_y - bubble_padding
            
            # Draw comic-style speech bubble background behind timer only
            self._draw_comic_bubble(screen, bubble_x, bubble_y, bubble_width, bubble_height, pulse)
            
            # Shadow for timer
            timer_shadow = timer_font.render(timer_text, True, (0, 0, 0))
            screen.blit(timer_shadow, (timer_x + 2, timer_y + 2))
            screen.blit(timer_surface, (timer_x, timer_y))
    
    def _draw_comic_bubble(self, screen, x, y, width, height, pulse=1.0):
        """Draw a comic-style speech bubble background."""
        # Main bubble colors
        bubble_fill = (135, 206, 250)  # Sky blue
        bubble_outline = (0, 0, 0)  # Black outline
        
        # Create a surface for the bubble with alpha
        bubble_surface = pygame.Surface((int(width + 80), int(height + 80)), pygame.SRCALPHA)
        
        # Center point for drawing on the surface
        center_x = 40
        center_y = 40
        
        # Draw simple circle
        radius = min(width, height) * 0.5 * pulse
        circle_center = (int(center_x + width / 2), int(center_y + height / 2))
        
        # Draw filled circle
        pygame.draw.circle(bubble_surface, bubble_fill, circle_center, int(radius))
        
        # Draw thick black outline
        pygame.draw.circle(bubble_surface, bubble_outline, circle_center, int(radius), 4)
        
        # Add halftone dots pattern for comic effect
        dot_spacing = 10
        dot_radius = 2
        for dx in range(0, int(width), dot_spacing):
            for dy in range(0, int(height), dot_spacing):
                dot_x = center_x + width * 0.25 + dx
                dot_y = center_y + height * 0.25 + dy
                # Check if point is inside the bubble
                dist_to_center = math.sqrt((dot_x - circle_center[0])**2 + (dot_y - circle_center[1])**2)
                if dist_to_center < radius * 0.7:
                    pygame.draw.circle(bubble_surface, (100, 180, 230), (int(dot_x), int(dot_y)), dot_radius)
        
        # Blit the bubble surface to the screen
        screen.blit(bubble_surface, (x - 40, y - 40))
    
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