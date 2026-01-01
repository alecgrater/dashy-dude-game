"""
Achievements menu state.
"""
import pygame
import math
from src.states.base_state import BaseState
from src.utils.constants import *


class AchievementsState(BaseState):
    """
    State for displaying achievements.
    """
    
    def __init__(self, game):
        super().__init__(game)
        self.back_button_rect = None
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 300  # pixels per second
    
    def enter(self):
        """Initialize achievements menu."""
        # Start with fade in
        self.game.ui_renderer.start_fade(fade_in=True)
        self.scroll_offset = 0
        print("Achievements menu entered")
    
    def exit(self):
        """Called when exiting this state."""
        pass
    
    def update(self, dt):
        """Update achievements menu."""
        # Update UI animations
        self.game.ui_renderer.update_fade(dt)
        
        # Handle scrolling with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed * dt)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed * dt)
    
    def _render_achievement_card(self, screen, achievement, x, y, width, height):
        """
        Render a single achievement card.
        
        Args:
            screen: Pygame screen surface
            achievement: Achievement object
            x, y: Position
            width, height: Card dimensions
        """
        # Determine colors based on unlock status
        if achievement.unlocked:
            bg_color = (40, 60, 40)
            border_color = achievement.icon_color
            text_color = (255, 255, 255)
            icon_alpha = 255
        else:
            bg_color = (30, 30, 30)
            border_color = (80, 80, 80)
            text_color = (120, 120, 120)
            icon_alpha = 100
        
        # Draw card background
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)
        
        # Draw achievement icon (star)
        icon_size = 40
        icon_x = x + 30
        icon_y = y + height // 2
        icon_color = (*achievement.icon_color, icon_alpha) if achievement.unlocked else (80, 80, 80, icon_alpha)
        
        # Draw star shape
        star_points = []
        for i in range(10):
            angle = (i * 36 - 90) * math.pi / 180
            if i % 2 == 0:
                radius = icon_size // 2
            else:
                radius = icon_size // 4
            px = icon_x + int(radius * math.cos(angle))
            py = icon_y + int(radius * math.sin(angle))
            star_points.append((px, py))
        
        # Create surface for star with alpha
        star_surface = pygame.Surface((icon_size * 2, icon_size * 2), pygame.SRCALPHA)
        adjusted_points = [(p[0] - icon_x + icon_size, p[1] - icon_y + icon_size) for p in star_points]
        pygame.draw.polygon(star_surface, icon_color, adjusted_points)
        screen.blit(star_surface, (icon_x - icon_size, icon_y - icon_size))
        
        # Draw text
        name_font = pygame.font.Font(None, 28)
        desc_font = pygame.font.Font(None, 20)
        
        # Achievement name
        name_text = name_font.render(achievement.name, True, text_color)
        screen.blit(name_text, (x + 80, y + 15))
        
        # Achievement description
        desc_text = desc_font.render(achievement.description, True, text_color)
        screen.blit(desc_text, (x + 80, y + 45))
        
        # Unlock date if unlocked
        if achievement.unlocked and achievement.unlock_date:
            date_font = pygame.font.Font(None, 16)
            # Format date nicely
            from datetime import datetime
            try:
                date_obj = datetime.fromisoformat(achievement.unlock_date)
                date_str = date_obj.strftime("%b %d, %Y")
            except:
                date_str = "Unlocked"
            date_text = date_font.render(date_str, True, (150, 150, 150))
            screen.blit(date_text, (x + 80, y + 70))
        else:
            # Show "Locked" status
            locked_font = pygame.font.Font(None, 18)
            locked_text = locked_font.render("🔒 LOCKED", True, (100, 100, 100))
            screen.blit(locked_text, (x + 80, y + 70))
    
    def render(self, screen):
        """Render achievements menu."""
        # Clear screen with dark background
        screen.fill((20, 20, 30))
        
        # Render title
        self.game.ui_renderer.render_title(screen, "ACHIEVEMENTS")
        
        # Get all achievements
        achievements = self.game.achievement_system.get_all_achievements()
        
        # Render completion stats
        unlocked_count = self.game.achievement_system.get_unlocked_count()
        total_count = self.game.achievement_system.get_total_count()
        completion_pct = self.game.achievement_system.get_completion_percentage()
        
        stats_font = pygame.font.Font(None, 24)
        stats_text = stats_font.render(
            f"Unlocked: {unlocked_count}/{total_count} ({completion_pct:.0f}%)",
            True,
            UI_TEXT
        )
        screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, 120))
        
        # Calculate scrollable area
        card_height = 100
        card_spacing = 15
        cards_start_y = 170
        total_height = len(achievements) * (card_height + card_spacing)
        visible_height = SCREEN_HEIGHT - cards_start_y - 100
        self.max_scroll = max(0, total_height - visible_height)
        
        # Create scrollable surface
        scroll_surface = pygame.Surface((SCREEN_WIDTH, visible_height))
        scroll_surface.fill((20, 20, 30))
        
        # Render achievement cards
        card_width = 600
        card_x = (SCREEN_WIDTH - card_width) // 2
        
        for i, achievement in enumerate(achievements):
            card_y = i * (card_height + card_spacing) - int(self.scroll_offset)
            
            # Only render if visible
            if -card_height < card_y < visible_height:
                self._render_achievement_card(
                    scroll_surface,
                    achievement,
                    card_x,
                    card_y,
                    card_width,
                    card_height
                )
        
        # Blit scrollable surface
        screen.blit(scroll_surface, (0, cards_start_y))
        
        # Render scroll indicator if needed
        if self.max_scroll > 0:
            indicator_font = pygame.font.Font(None, 20)
            if self.scroll_offset < self.max_scroll:
                scroll_text = indicator_font.render("▼ Scroll Down ▼", True, (150, 150, 150))
                screen.blit(scroll_text, (SCREEN_WIDTH // 2 - scroll_text.get_width() // 2, SCREEN_HEIGHT - 80))
            if self.scroll_offset > 0:
                scroll_text = indicator_font.render("▲ Scroll Up ▲", True, (150, 150, 150))
                screen.blit(scroll_text, (SCREEN_WIDTH // 2 - scroll_text.get_width() // 2, cards_start_y - 25))
        
        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()
        
        # Back button
        button_width = 200
        button_height = 50
        back_x = SCREEN_WIDTH // 2 - button_width // 2
        back_y = SCREEN_HEIGHT - 70
        self.back_button_rect = pygame.Rect(back_x, back_y, button_width, button_height)
        is_back_hovered = self.back_button_rect.collidepoint(mouse_pos)
        
        self.game.ui_renderer.render_button(
            screen, "BACK",
            back_x, back_y, button_width, button_height,
            is_back_hovered
        )
        
        # Render fade overlay
        self.game.ui_renderer.render_fade(screen)
    
    def handle_event(self, event):
        """Handle events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to title screen
                self.game.change_state('title')
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                # Return to title screen
                self.game.change_state('title')
        
        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            scroll_amount = event.y * 50  # Scroll speed
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - scroll_amount))