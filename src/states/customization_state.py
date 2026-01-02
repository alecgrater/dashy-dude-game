"""
Customization menu state for selecting themes.
"""
import pygame
from src.states.base_state import BaseState
from src.systems.customization import PlayerTheme, PlatformTheme, BackgroundTheme
from src.utils.constants import *


class CustomizationState(BaseState):
    """
    Customization menu for selecting player, platform, and background themes.
    """
    
    def __init__(self, game):
        """
        Initialize customization state.
        
        Args:
            game: Reference to main Game instance
        """
        super().__init__(game)
        self.customization = game.customization
        self.save_system = game.save_system
        
        # Menu state
        self.selected_category = 0  # 0=Player, 1=Platform, 2=Background
        self.categories = ["Player", "Platform", "Background"]
        self.category_buttons = []
        
        # Theme selection
        self.theme_buttons = []
        self.back_button_rect = None
        self.mouse_pos = (0, 0)
        self.animation_time = 0.0
        
        # Preview
        self.preview_surface = None
        self._create_preview()
    
    def _create_preview(self):
        """Create preview surface showing current theme."""
        self.preview_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
    
    def enter(self):
        """Called when entering this state."""
        self.animation_time = 0.0
        print("Customization menu opened")
    
    def exit(self):
        """Called when exiting this state."""
        # Save customization choices
        self.save_system.save_customization(self.customization.to_dict())
    
    def update(self, dt):
        """
        Update customization menu.
        
        Args:
            dt: Delta time in seconds
        """
        self.animation_time += dt
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Update preview
        self._update_preview()
    
    def _update_preview(self):
        """Update the theme preview."""
        self.preview_surface.fill((0, 0, 0, 0))
        
        # Draw a simple preview based on selected category
        if self.selected_category == 0:  # Player
            colors = self.customization.get_player_colors()
            # Draw simple player representation
            pygame.draw.rect(self.preview_surface, colors['primary'],
                           (130, 80, 40, 50), border_radius=8)
            pygame.draw.circle(self.preview_surface, colors['accent'], (145, 95), 5)
            pygame.draw.circle(self.preview_surface, colors['accent'], (155, 95), 5)
        
        elif self.selected_category == 1:  # Platform
            colors = self.customization.get_platform_colors()
            # Draw platform
            pygame.draw.rect(self.preview_surface, colors['top'], (50, 150, 200, 8))
            pygame.draw.rect(self.preview_surface, colors['base'], (50, 158, 200, 32))
        
        elif self.selected_category == 2:  # Background
            colors = self.customization.get_background_colors()
            # Draw gradient
            for y in range(200):
                ratio = y / 200
                color = (
                    int(colors['sky_top'][0] + (colors['sky_bottom'][0] - colors['sky_top'][0]) * ratio),
                    int(colors['sky_top'][1] + (colors['sky_bottom'][1] - colors['sky_top'][1]) * ratio),
                    int(colors['sky_top'][2] + (colors['sky_bottom'][2] - colors['sky_top'][2]) * ratio),
                )
                pygame.draw.line(self.preview_surface, color, (0, y), (300, y))
    
    def render(self, screen):
        """
        Render customization menu.
        
        Args:
            screen: pygame.Surface to draw on
        """
        # Dark background
        screen.fill((20, 20, 30))
        
        # Title
        self._render_title(screen)
        
        # Category tabs
        self._render_category_tabs(screen)
        
        # Theme options
        self._render_theme_options(screen)
        
        # Preview
        self._render_preview(screen)
        
        # Back button
        self._render_back_button(screen)
    
    def _render_title(self, screen):
        """Render menu title."""
        font = pygame.font.Font(None, 64)
        title_text = "CUSTOMIZATION"
        
        # Shadow
        shadow = font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 53))
        screen.blit(shadow, shadow_rect)
        
        # Main text
        text = font.render(title_text, True, UI_ACCENT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(text, text_rect)
    
    def _render_category_tabs(self, screen):
        """Render category selection tabs."""
        self.category_buttons = []
        tab_width = 150
        tab_height = 50
        start_x = SCREEN_WIDTH // 2 - (len(self.categories) * tab_width) // 2
        y = 120
        
        for i, category in enumerate(self.categories):
            x = start_x + i * tab_width
            rect = pygame.Rect(x, y, tab_width, tab_height)
            self.category_buttons.append(rect)
            
            is_selected = i == self.selected_category
            is_hovered = rect.collidepoint(self.mouse_pos)
            
            # Draw tab
            color = UI_ACCENT if is_selected else UI_SECONDARY
            if is_hovered and not is_selected:
                color = (color[0] + 20, color[1] + 20, color[2] + 20)
            
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, UI_TEXT, rect, 2, border_radius=8)
            
            # Text
            font = pygame.font.Font(None, 32)
            text = font.render(category, True, UI_TEXT)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
    
    def _render_theme_options(self, screen):
        """Render available theme options for selected category."""
        self.theme_buttons = []
        
        # Get themes for current category
        if self.selected_category == 0:
            themes = list(PlayerTheme)
            current_theme = self.customization.player_theme
        elif self.selected_category == 1:
            themes = list(PlatformTheme)
            current_theme = self.customization.platform_theme
        else:
            themes = list(BackgroundTheme)
            current_theme = self.customization.background_theme
        
        # Layout themes in grid
        cols = 3
        button_width = 180
        button_height = 60
        spacing = 20
        start_x = SCREEN_WIDTH // 2 - (cols * button_width + (cols - 1) * spacing) // 2
        start_y = 200
        
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
        for i, theme in enumerate(themes):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            rect = pygame.Rect(x, y, button_width, button_height)
            self.theme_buttons.append((rect, theme))
            
            is_unlocked = self.customization.is_unlocked(theme)
            is_selected = theme == current_theme
            is_hovered = rect.collidepoint(self.mouse_pos) and is_unlocked
            
            # Draw button
            if not is_unlocked:
                color = (60, 60, 60)
            elif is_selected:
                color = (100, 200, 100)
            elif is_hovered:
                color = (80, 80, 120)
            else:
                color = UI_SECONDARY
            
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, UI_TEXT if is_unlocked else (100, 100, 100),
                           rect, 2, border_radius=8)
            
            # Theme name
            name = theme.value.replace('_', ' ').title()
            text = font.render(name, True, UI_TEXT if is_unlocked else (120, 120, 120))
            text_rect = text.get_rect(center=(rect.centerx, rect.centery - 10))
            screen.blit(text, text_rect)
            
            # Unlock requirement or selected indicator
            if is_selected:
                status_text = "✓ ACTIVE"
                status_color = (150, 255, 150)
            elif not is_unlocked:
                unlock_score = self.customization.get_unlock_score(theme)
                status_text = f"Unlock: {unlock_score}"
                status_color = (200, 200, 100)
            else:
                status_text = "Click to select"
                status_color = (180, 180, 180)
            
            status = small_font.render(status_text, True, status_color)
            status_rect = status.get_rect(center=(rect.centerx, rect.centery + 15))
            screen.blit(status, status_rect)
    
    def _render_preview(self, screen):
        """Render theme preview."""
        preview_x = SCREEN_WIDTH - 350
        preview_y = 200
        
        # Preview box
        preview_rect = pygame.Rect(preview_x, preview_y, 320, 220)
        pygame.draw.rect(screen, UI_SECONDARY, preview_rect, border_radius=12)
        pygame.draw.rect(screen, UI_TEXT, preview_rect, 2, border_radius=12)
        
        # Title
        font = pygame.font.Font(None, 32)
        title = font.render("Preview", True, UI_TEXT)
        title_rect = title.get_rect(center=(preview_rect.centerx, preview_y - 20))
        screen.blit(title, title_rect)
        
        # Preview surface
        screen.blit(self.preview_surface, (preview_x + 10, preview_y + 10))
    
    def _render_back_button(self, screen):
        """Render back button."""
        button_width = 150
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT - 100
        
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovered = self.back_button_rect.collidepoint(self.mouse_pos)
        
        # Draw button
        color = (100, 100, 150) if is_hovered else UI_SECONDARY
        pygame.draw.rect(screen, color, self.back_button_rect, border_radius=8)
        pygame.draw.rect(screen, UI_TEXT, self.back_button_rect, 2, border_radius=8)
        
        # Text
        font = pygame.font.Font(None, 36)
        text = font.render("BACK", True, UI_TEXT)
        text_rect = text.get_rect(center=self.back_button_rect.center)
        screen.blit(text, text_rect)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: pygame.event.Event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check category tabs
            for i, rect in enumerate(self.category_buttons):
                if rect.collidepoint(event.pos):
                    self.selected_category = i
                    return
            
            # Check theme buttons
            for rect, theme in self.theme_buttons:
                if rect.collidepoint(event.pos):
                    if self.customization.is_unlocked(theme):
                        # Set theme
                        if self.selected_category == 0:
                            self.customization.set_player_theme(theme)
                        elif self.selected_category == 1:
                            self.customization.set_platform_theme(theme)
                        else:
                            self.customization.set_background_theme(theme)
                        
                        # Update game's graphics
                        self._apply_theme_to_game()
                    return
            
            # Check back button
            if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                self._go_back()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
    
    def _apply_theme_to_game(self):
        """Apply selected themes to game graphics."""
        # Update sprite generator colors
        player_colors = self.customization.get_player_colors()
        platform_colors = self.customization.get_platform_colors()
        
        self.game.sprite_generator.set_player_colors(player_colors)
        self.game.sprite_generator.set_platform_colors(platform_colors)
        
        # Regenerate sprites
        self.game.sprites = self.game.sprite_generator.generate_all_sprites()
        
        # Update background colors
        background_colors = self.customization.get_background_colors()
        if hasattr(self.game, 'title_state') and self.game.title_state:
            self.game.title_state.background.set_colors(background_colors)
    
    def _go_back(self):
        """Return to title screen."""
        self.exit()
        self.game.current_state = self.game.title_state
        self.game.current_state.enter()