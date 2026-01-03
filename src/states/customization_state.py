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
        # Preview surface matches the inner area of the preview box
        self.preview_surface = pygame.Surface((260, 200), pygame.SRCALPHA)
    
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
        preview_width = 260
        preview_height = 200
        self.preview_surface.fill((0, 0, 0, 0))
        
        # Draw a simple preview based on selected category
        if self.selected_category == 0:  # Player
            colors = self.customization.get_player_colors()
            # Draw simple player representation - centered in preview
            player_width = 40
            player_height = 50
            player_x = (preview_width - player_width) // 2
            player_y = (preview_height - player_height) // 2
            pygame.draw.rect(self.preview_surface, colors['primary'],
                           (player_x, player_y, player_width, player_height), border_radius=8)
            # Eyes centered on player
            pygame.draw.circle(self.preview_surface, colors['accent'], (player_x + 12, player_y + 15), 5)
            pygame.draw.circle(self.preview_surface, colors['accent'], (player_x + 28, player_y + 15), 5)
        
        elif self.selected_category == 1:  # Platform
            colors = self.customization.get_platform_colors()
            # Draw platform - centered in preview
            platform_width = 180
            platform_x = (preview_width - platform_width) // 2
            platform_y = (preview_height - 40) // 2  # Center vertically
            pygame.draw.rect(self.preview_surface, colors['top'], (platform_x, platform_y, platform_width, 8))
            pygame.draw.rect(self.preview_surface, colors['base'], (platform_x, platform_y + 8, platform_width, 32))
        
        elif self.selected_category == 2:  # Background
            colors = self.customization.get_background_colors()
            # Draw gradient - fill entire preview surface
            for y in range(preview_height):
                ratio = y / preview_height
                color = (
                    int(colors['sky_top'][0] + (colors['sky_bottom'][0] - colors['sky_top'][0]) * ratio),
                    int(colors['sky_top'][1] + (colors['sky_bottom'][1] - colors['sky_top'][1]) * ratio),
                    int(colors['sky_top'][2] + (colors['sky_bottom'][2] - colors['sky_top'][2]) * ratio),
                )
                pygame.draw.line(self.preview_surface, color, (0, y), (preview_width, y))
    
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
        tab_spacing = 20  # Spacing between tabs
        total_width = len(self.categories) * tab_width + (len(self.categories) - 1) * tab_spacing
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        y = 120
        
        for i, category in enumerate(self.categories):
            x = start_x + i * (tab_width + tab_spacing)
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
        
        # Layout themes in grid - positioned on left side with padding from preview
        cols = 2  # Reduced to 2 columns for better spacing
        button_width = 160
        button_height = 60
        spacing = 15
        start_x = 40  # Fixed left margin
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
        # Position preview on right side with proper padding
        preview_box_width = 280
        preview_box_height = 230
        preview_x = SCREEN_WIDTH - preview_box_width - 40  # 40px right margin
        preview_y = 230  # Below title
        
        # Preview title above box
        font = pygame.font.Font(None, 32)
        title = font.render("Preview", True, UI_TEXT)
        title_rect = title.get_rect(centerx=preview_x + preview_box_width // 2, bottom=preview_y - 10)
        screen.blit(title, title_rect)
        
        # Preview box
        preview_rect = pygame.Rect(preview_x, preview_y, preview_box_width, preview_box_height)
        pygame.draw.rect(screen, UI_SECONDARY, preview_rect, border_radius=12)
        pygame.draw.rect(screen, UI_TEXT, preview_rect, 2, border_radius=12)
        
        # Preview surface - centered inside the box with padding
        surface_x = preview_x + (preview_box_width - 260) // 2
        surface_y = preview_y + (preview_box_height - 200) // 2
        screen.blit(self.preview_surface, (surface_x, surface_y))
    
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
        
        # Update background colors if title_state has a background attribute
        background_colors = self.customization.get_background_colors()
        if hasattr(self.game, 'title_state') and self.game.title_state:
            if hasattr(self.game.title_state, 'background') and self.game.title_state.background:
                self.game.title_state.background.set_colors(background_colors)
    
    def _go_back(self):
        """Return to title screen."""
        self.exit()
        self.game.current_state = self.game.title_state
        self.game.current_state.enter()