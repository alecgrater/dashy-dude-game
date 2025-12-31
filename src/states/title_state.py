"""
Title screen state with menu and animations.
"""
import pygame
import math
from src.states.base_state import BaseState
from src.graphics.background import Background
from src.systems.save_system import SaveSystem
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
        # Get background colors from customization
        background_colors = game.customization.get_background_colors()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT, background_colors)
        self.save_system = game.save_system
        self.animation_time = 0.0
        self.play_button_rect = None
        self.customize_button_rect = None
        self.quit_button_rect = None
        self.mouse_pos = (0, 0)
        
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
        
        # Render customize button
        self._render_customize_button(screen)
        
        # Render quit button
        self._render_quit_button(screen)
        
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
    
    def _render_customize_button(self, screen):
        """Render customize button."""
        button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        button_y = SCREEN_HEIGHT // 2 + 130
        
        # Check if mouse is hovering
        self.customize_button_rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        is_hovered = self.customize_button_rect.collidepoint(self.mouse_pos)
        
        # Add pulse animation to button
        pulse = 1.0 + math.sin(self.animation_time * 4) * 0.05 if is_hovered else 1.0
        
        # Draw button with scale
        if pulse != 1.0:
            scaled_width = int(BUTTON_WIDTH * pulse)
            scaled_height = int(BUTTON_HEIGHT * pulse)
            button_x = SCREEN_WIDTH // 2 - scaled_width // 2
            button_y_adjusted = button_y + (BUTTON_HEIGHT - scaled_height) // 2
            self.customize_button_rect = pygame.Rect(button_x, button_y_adjusted, scaled_width, scaled_height)
        
        # Render button using UI renderer
        self.game.ui_renderer.render_button(
            screen, "CUSTOMIZE",
            self.customize_button_rect.x, self.customize_button_rect.y,
            self.customize_button_rect.width, self.customize_button_rect.height,
            is_hovered
        )
    
    def _render_quit_button(self, screen):
        """Render quit button."""
        button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        button_y = SCREEN_HEIGHT // 2 + 210
        
        # Check if mouse is hovering
        self.quit_button_rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        is_hovered = self.quit_button_rect.collidepoint(self.mouse_pos)
        
        # Add pulse animation to button
        pulse = 1.0 + math.sin(self.animation_time * 4) * 0.05 if is_hovered else 1.0
        
        # Draw button with scale
        if pulse != 1.0:
            scaled_width = int(BUTTON_WIDTH * pulse)
            scaled_height = int(BUTTON_HEIGHT * pulse)
            button_x = SCREEN_WIDTH // 2 - scaled_width // 2
            button_y_adjusted = button_y + (BUTTON_HEIGHT - scaled_height) // 2
            self.quit_button_rect = pygame.Rect(button_x, button_y_adjusted, scaled_width, scaled_height)
        
        # Render button using UI renderer with red color for quit
        # Draw custom quit button with red tint
        button_rect = self.quit_button_rect
        color = (180, 50, 50) if is_hovered else (120, 40, 40)
        
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, UI_TEXT, button_rect, 3, border_radius=10)
        
        # Draw text
        font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        text_surface = font.render("QUIT", True, UI_TEXT)
        text_x = button_rect.x + (button_rect.width - text_surface.get_width()) // 2
        text_y = button_rect.y + (button_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _render_high_score(self, screen):
        """Render high score display with top 5 scores in top right corner."""
        high_scores = self.save_system.get_scores()
        
        if not high_scores:
            return
        
        # Title
        title_font = pygame.font.Font(None, 36)
        title_text = "HIGH SCORES"
        title_surface = title_font.render(title_text, True, UI_ACCENT)
        title_shadow = title_font.render(title_text, True, UI_TEXT_SHADOW)
        
        # Position in top right corner
        title_x = SCREEN_WIDTH - title_surface.get_width() - 30
        title_y = 30
        
        screen.blit(title_shadow, (title_x + 2, title_y + 2))
        screen.blit(title_surface, (title_x, title_y))
        
        # Display top 5 scores
        score_font = pygame.font.Font(None, 24)
        y_offset = title_y + 40
        
        for i, entry in enumerate(high_scores[:5]):
            # Rank and score
            rank_text = f"#{i+1}"
            score_text = f"{entry.score}"
            
            # Color based on rank
            if i == 0:
                color = (255, 215, 0)  # Gold
            elif i == 1:
                color = (192, 192, 192)  # Silver
            elif i == 2:
                color = (205, 127, 50)  # Bronze
            else:
                color = UI_TEXT
            
            # Render rank
            rank_surface = score_font.render(rank_text, True, color)
            rank_shadow = score_font.render(rank_text, True, UI_TEXT_SHADOW)
            rank_x = SCREEN_WIDTH - 180
            
            screen.blit(rank_shadow, (rank_x + 1, y_offset + 1))
            screen.blit(rank_surface, (rank_x, y_offset))
            
            # Render score
            score_surface = score_font.render(score_text, True, color)
            score_shadow = score_font.render(score_text, True, UI_TEXT_SHADOW)
            score_x = SCREEN_WIDTH - 120
            
            screen.blit(score_shadow, (score_x + 1, y_offset + 1))
            screen.blit(score_surface, (score_x, y_offset))
            
            y_offset += 28
    
    def _render_controls(self, screen):
        """Render control instructions with epic styled box."""
        controls = [
            "SPACE - Jump / Double Jump / Helicopter Glide",
            "Hold SPACE after double jump to activate helicopter",
            "ESC - Pause Game"
        ]
        
        font = pygame.font.Font(None, 22)  # Smaller font
        
        # Calculate box dimensions (smaller)
        padding = 15
        line_height = 24
        box_width = 450
        box_height = len(controls) * line_height + padding * 2
        box_x = 20  # Top left position
        box_y = 20
        
        # Create a surface for the box with alpha channel
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        # Draw outer glow effect (multiple layers) - purple tones
        glow_colors = [
            (150, 100, 200, 30),
            (150, 100, 200, 20),
            (150, 100, 200, 10)
        ]
        for i, glow_color in enumerate(glow_colors):
            glow_offset = (i + 1) * 3
            glow_rect = pygame.Rect(-glow_offset, -glow_offset,
                                   box_width + glow_offset * 2,
                                   box_height + glow_offset * 2)
            pygame.draw.rect(box_surface, glow_color, glow_rect, border_radius=15)
        
        # Draw main background with solid purple
        background_rect = pygame.Rect(0, 0, box_width, box_height)
        pygame.draw.rect(box_surface, (100, 50, 150, 220), background_rect, border_radius=12)
        
        # Draw border with purple accent color
        border_rect = pygame.Rect(0, 0, box_width, box_height)
        pygame.draw.rect(box_surface, (180, 120, 255, 255), border_rect, 3, border_radius=12)
        
        # Draw inner border for extra style
        inner_border_rect = pygame.Rect(3, 3, box_width - 6, box_height - 6)
        pygame.draw.rect(box_surface, (200, 150, 255, 100), inner_border_rect, 1, border_radius=10)
        
        # Blit the box to the screen
        screen.blit(box_surface, (box_x, box_y))
        
        # Render text with enhanced styling (left-aligned)
        y_offset = box_y + padding + 5
        text_x = box_x + padding
        for i, control in enumerate(controls):
            # Render shadow for depth
            shadow = font.render(control, True, (0, 0, 0, 180))
            screen.blit(shadow, (text_x + 2, y_offset + i * line_height + 2))
            
            # Render main text with bright color
            text = font.render(control, True, (255, 255, 255))
            screen.blit(text, (text_x, y_offset + i * line_height))
    
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
                elif self.customize_button_rect and self.customize_button_rect.collidepoint(event.pos):
                    # Open customization menu
                    self._open_customization()
                elif self.quit_button_rect and self.quit_button_rect.collidepoint(event.pos):
                    # Quit game
                    self._quit_game()
        
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
    
    def _open_customization(self):
        """Open customization menu."""
        print("Opening customization menu...")
        self.exit()
        
        # Switch to customization state
        from src.states.customization_state import CustomizationState
        if not hasattr(self.game, 'customization_state'):
            self.game.customization_state = CustomizationState(self.game)
        self.game.current_state = self.game.customization_state
        self.game.current_state.enter()
    
    def _quit_game(self):
        """Quit the game."""
        print("Quitting game...")
        self.game.running = False