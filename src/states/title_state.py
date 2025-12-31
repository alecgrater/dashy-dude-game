"""
Title screen state with menu and animations.
"""
import pygame
import math
from src.states.base_state import BaseState
from src.graphics.background import Background
from src.utils.constants import *


class TitleState(BaseState):
    """
    Title screen with animated logo, play button, and high score display.
    """
    
    def __init__(self, game):
        """
        Initialize title state.
        
        Args:
            game: Reference to main Game instance
        """
        super().__init__(game)
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.animation_time = 0.0
        self.play_button_rect = None
        self.mouse_pos = (0, 0)
        self.high_score = 0  # TODO: Load from save file
        
        # Title animation
        self.title_bounce_offset = 0.0
        self.title_scale = 1.0
        
        # Cloud decorations
        self.clouds = self._generate_clouds()
    
    def _generate_clouds(self):
        """Generate decorative clouds for title screen."""
        clouds = []
        for i in range(5):
            cloud = {
                'x': (i * 300) % SCREEN_WIDTH,
                'y': 50 + (i * 40) % 200,
                'speed': 20 + (i * 10),
                'size': 60 + (i * 20)
            }
            clouds.append(cloud)
        return clouds
    
    def enter(self):
        """Called when entering this state."""
        self.animation_time = 0.0
        print("Title screen loaded")
        print("Click 'Play' to start!")
    
    def exit(self):
        """Called when exiting this state."""
        pass
    
    def update(self, dt):
        """
        Update title screen animations.
        
        Args:
            dt: Delta time in seconds
        """
        self.animation_time += dt
        
        # Update background
        self.background.update(dt)
        
        # Animate title (bounce effect)
        self.title_bounce_offset = math.sin(self.animation_time * 2) * 10
        self.title_scale = 1.0 + math.sin(self.animation_time * 3) * 0.05
        
        # Animate clouds
        for cloud in self.clouds:
            cloud['x'] += cloud['speed'] * dt
            if cloud['x'] > SCREEN_WIDTH + cloud['size']:
                cloud['x'] = -cloud['size']
        
        # Get mouse position
        self.mouse_pos = pygame.mouse.get_pos()
    
    def render(self, screen):
        """
        Render title screen.
        
        Args:
            screen: pygame.Surface to draw on
        """
        # Render background with animated water
        # Create a simple camera-like object for background rendering
        class SimpleCamera:
            def __init__(self):
                self.position = pygame.math.Vector2(0, 0)
        
        camera = SimpleCamera()
        self.background.render(screen, camera)
        
        # Render clouds
        self._render_clouds(screen)
        
        # Render animated title
        self._render_title(screen)
        
        # Render play button
        self._render_play_button(screen)
        
        # Render high score
        self._render_high_score(screen)
        
        # Render controls hint
        self._render_controls(screen)
    
    def _render_clouds(self, screen):
        """Render decorative clouds."""
        for cloud in self.clouds:
            # Draw simple cloud shape (3 circles)
            cloud_surface = pygame.Surface((cloud['size'], cloud['size'] // 2), pygame.SRCALPHA)
            
            # Main cloud body
            pygame.draw.circle(cloud_surface, (255, 255, 255, 150),
                             (cloud['size'] // 2, cloud['size'] // 4),
                             cloud['size'] // 4)
            pygame.draw.circle(cloud_surface, (255, 255, 255, 150),
                             (cloud['size'] // 3, cloud['size'] // 3),
                             cloud['size'] // 5)
            pygame.draw.circle(cloud_surface, (255, 255, 255, 150),
                             (cloud['size'] * 2 // 3, cloud['size'] // 3),
                             cloud['size'] // 5)
            
            screen.blit(cloud_surface, (int(cloud['x']), int(cloud['y'])))
    
    def _render_title(self, screen):
        """Render animated game title."""
        # Title text with animation
        title_text = "ENDLESS LAKE"
        
        # Calculate position with bounce
        base_y = SCREEN_HEIGHT // 4
        animated_y = base_y + self.title_bounce_offset
        
        # Render title with scale effect
        font = pygame.font.Font(None, int(TITLE_FONT_SIZE * self.title_scale))
        
        # Render shadow
        shadow = font.render(title_text, True, UI_TEXT_SHADOW)
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, animated_y + 4))
        screen.blit(shadow, shadow_rect)
        
        # Render main text with gradient effect (simulate with multiple colors)
        text = font.render(title_text, True, UI_ACCENT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, animated_y))
        screen.blit(text, text_rect)
        
        # Render subtitle
        subtitle_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        subtitle = subtitle_font.render("An Endless Runner Adventure", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, animated_y + 60))
        screen.blit(subtitle, subtitle_rect)
    
    def _render_play_button(self, screen):
        """Render play button with hover effect."""
        button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        button_y = SCREEN_HEIGHT // 2 + 50
        
        # Check if mouse is hovering
        self.play_button_rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        is_hovered = self.play_button_rect.collidepoint(self.mouse_pos)
        
        # Add pulse animation to button
        pulse = 1.0 + math.sin(self.animation_time * 4) * 0.05 if is_hovered else 1.0
        
        # Draw button with scale
        if pulse != 1.0:
            scaled_width = int(BUTTON_WIDTH * pulse)
            scaled_height = int(BUTTON_HEIGHT * pulse)
            button_x = SCREEN_WIDTH // 2 - scaled_width // 2
            button_y_adjusted = button_y + (BUTTON_HEIGHT - scaled_height) // 2
            self.play_button_rect = pygame.Rect(button_x, button_y_adjusted, scaled_width, scaled_height)
        
        # Render button using UI renderer
        self.game.ui_renderer.render_button(
            screen, "PLAY", 
            self.play_button_rect.x, self.play_button_rect.y,
            self.play_button_rect.width, self.play_button_rect.height,
            is_hovered
        )
    
    def _render_high_score(self, screen):
        """Render high score display."""
        if self.high_score > 0:
            high_score_text = f"High Score: {self.high_score}"
            font = pygame.font.Font(None, SCORE_FONT_SIZE)
            
            # Render shadow
            shadow = font.render(high_score_text, True, UI_TEXT_SHADOW)
            shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT // 2 + 150 + 2))
            screen.blit(shadow, shadow_rect)
            
            # Render text
            text = font.render(high_score_text, True, UI_ACCENT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            screen.blit(text, text_rect)
    
    def _render_controls(self, screen):
        """Render control instructions."""
        controls = [
            "SPACE - Jump / Double Jump / Helicopter Glide",
            "Hold SPACE after double jump to activate helicopter",
            "ESC - Quit Game"
        ]
        
        font = pygame.font.Font(None, 28)
        y_offset = SCREEN_HEIGHT - 120
        
        for i, control in enumerate(controls):
            text = font.render(control, True, UI_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 30))
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: pygame.event.Event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.play_button_rect and self.play_button_rect.collidepoint(event.pos):
                    # Transition to play state
                    self._start_game()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Start game on space or enter
                self._start_game()
    
    def _start_game(self):
        """Transition to play state."""
        print("Starting game...")
        self.exit()
        
        # Switch to play state
        from src.states.play_state import PlayState
        self.game.play_state = PlayState(self.game)
        self.game.current_state = self.game.play_state
        self.game.current_state.enter()