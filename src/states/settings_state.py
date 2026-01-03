"""
Settings state for game configuration.
Includes FPS counter toggle, VSync toggle, and other performance settings.
"""

import pygame
import math
from src.states.base_state import BaseState
from src.graphics.background import Background
from src.utils.constants import *


class SettingsState(BaseState):
    """Settings menu state with modern UI similar to statistics run history."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Background
        background_colors = game.customization.get_background_colors()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT, background_colors)
        
        # Settings options
        self.settings = {
            'show_fps': False,
            'vsync': True,
        }
        
        # Load saved settings
        saved_settings = self.game.save_system.get_settings()
        if saved_settings:
            self.settings.update(saved_settings)
        
        # Menu options
        self.options = [
            {'name': 'FPS Counter', 'key': 'show_fps', 'type': 'toggle', 'description': 'Show frames per second counter'},
            {'name': 'VSync', 'key': 'vsync', 'type': 'toggle', 'description': 'Synchronize with display refresh rate'},
            {'name': 'Back to Menu', 'key': 'back', 'type': 'action', 'description': 'Return to title screen'},
        ]
        
        self.selected_index = 0
        self.key_repeat_timer = 0
        self.key_repeat_delay = 0.15
        
        # UI state for mouse interaction
        self.mouse_pos = (0, 0)
        self.option_rects = []
        self.toggle_rects = []  # Separate rects for toggle buttons
        self.animation_time = 0.0
        self.back_button_rect = None
    
    def enter(self):
        """Called when entering this state."""
        self.animation_time = 0.0
    
    def exit(self):
        """Called when exiting this state."""
        # Save settings
        self.game.save_system.save_settings(self.settings)
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('title')
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_option()
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self._toggle_option()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check option items
                for i, (item_rect, toggle_rect) in enumerate(zip(self.option_rects, self.toggle_rects)):
                    option = self.options[i]
                    
                    if option['type'] == 'toggle':
                        # Check if clicked on toggle button specifically
                        if toggle_rect and toggle_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self._activate_option()
                            return
                        # Or clicked anywhere on the item
                        elif item_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self._activate_option()
                            return
                    elif option['type'] == 'action':
                        if item_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self._activate_option()
                            return
    
    def _activate_option(self):
        """Activate the selected option."""
        option = self.options[self.selected_index]
        
        if option['type'] == 'toggle':
            self.settings[option['key']] = not self.settings[option['key']]
            # Update game settings immediately for real-time effect
            self.game.settings[option['key']] = self.settings[option['key']]
        elif option['key'] == 'back':
            self.game.change_state('title')
    
    def _toggle_option(self):
        """Toggle the selected option (for left/right keys)."""
        option = self.options[self.selected_index]
        
        if option['type'] == 'toggle':
            self.settings[option['key']] = not self.settings[option['key']]
            # Update game settings immediately for real-time effect
            self.game.settings[option['key']] = self.settings[option['key']]
    
    def update(self, dt):
        """Update settings state."""
        self.animation_time += dt
        self.background.update(dt)
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Handle key repeat for navigation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            self.key_repeat_timer += dt
            if self.key_repeat_timer >= self.key_repeat_delay:
                self.key_repeat_timer = 0
                if keys[pygame.K_UP]:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif keys[pygame.K_DOWN]:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
        else:
            self.key_repeat_timer = 0
    
    def render(self, screen):
        """Render settings menu."""
        # Background with overlay
        class SimpleCamera:
            def __init__(self):
                self.position = pygame.math.Vector2(0, 0)
        
        camera = SimpleCamera()
        self.background.render(screen, camera)
        
        # Semi-transparent overlay for readability
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Title (consistent style with other menus)
        self._render_title(screen)
        
        # Render options with modern UI style
        self._render_options(screen)
        
        # Instructions
        self._render_instructions(screen)
    
    def _render_title(self, screen):
        """Render menu title with consistent style."""
        font = pygame.font.Font(None, 64)
        title_text = "SETTINGS"
        
        # Shadow
        shadow = font.render(title_text, True, UI_TEXT_SHADOW)
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 53))
        screen.blit(shadow, shadow_rect)
        
        # Main text with accent color
        text = font.render(title_text, True, UI_ACCENT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(text, text_rect)
    
    def _render_options(self, screen):
        """Render settings options with modern card-style UI."""
        content_y = 140
        content_x = 80
        item_height = 70
        item_width = SCREEN_WIDTH - 160
        
        self.option_rects = []
        self.toggle_rects = []
        
        for i, option in enumerate(self.options):
            item_y = content_y + i * (item_height + 15)
            item_rect = pygame.Rect(content_x, item_y, item_width, item_height)
            self.option_rects.append(item_rect)
            
            is_selected = (i == self.selected_index)
            is_hovered = item_rect.collidepoint(self.mouse_pos)
            
            # Background with hover/selection effect
            if is_selected:
                bg_color = (80, 80, 110)
                border_color = UI_ACCENT
            elif is_hovered:
                bg_color = (70, 70, 95)
                border_color = (120, 120, 150)
            else:
                bg_color = (50, 50, 70)
                border_color = (80, 80, 100)
            
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, item_rect, 2, border_radius=10)
            
            # Option name
            name_font = pygame.font.Font(None, 32)
            name_color = UI_ACCENT if is_selected else UI_TEXT
            name_text = name_font.render(option['name'], True, name_color)
            screen.blit(name_text, (content_x + 20, item_y + 15))
            
            # Description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(option.get('description', ''), True, (150, 150, 150))
            screen.blit(desc_text, (content_x + 20, item_y + 45))
            
            # Toggle button or action indicator
            if option['type'] == 'toggle':
                toggle_rect = self._render_toggle_button(
                    screen, item_rect.right - 100, item_y + 20,
                    self.settings[option['key']], is_hovered or is_selected
                )
                self.toggle_rects.append(toggle_rect)
            else:
                # Action indicator (arrow)
                arrow_font = pygame.font.Font(None, 36)
                arrow_text = arrow_font.render("→", True, UI_ACCENT if is_hovered or is_selected else (100, 100, 120))
                screen.blit(arrow_text, (item_rect.right - 40, item_y + 22))
                self.toggle_rects.append(None)
    
    def _render_toggle_button(self, screen, x, y, is_on, is_active):
        """Render a toggle switch button."""
        toggle_width = 60
        toggle_height = 30
        toggle_rect = pygame.Rect(x, y, toggle_width, toggle_height)
        
        # Background track
        if is_on:
            track_color = (80, 180, 80) if is_active else (60, 140, 60)
        else:
            track_color = (100, 100, 100) if is_active else (70, 70, 70)
        
        pygame.draw.rect(screen, track_color, toggle_rect, border_radius=15)
        
        # Toggle knob
        knob_radius = 12
        knob_x = x + toggle_width - knob_radius - 4 if is_on else x + knob_radius + 4
        knob_y = y + toggle_height // 2
        knob_color = (255, 255, 255) if is_on else (180, 180, 180)
        pygame.draw.circle(screen, knob_color, (knob_x, knob_y), knob_radius)
        
        # ON/OFF text
        status_font = pygame.font.Font(None, 18)
        status_text = "ON" if is_on else "OFF"
        text_color = (255, 255, 255) if is_on else (150, 150, 150)
        text_surface = status_font.render(status_text, True, text_color)
        
        if is_on:
            text_x = x + 8
        else:
            text_x = x + toggle_width - 28
        
        screen.blit(text_surface, (text_x, y + 8))
        
        return toggle_rect
    
    def _render_instructions(self, screen):
        """Render control instructions."""
        instructions = [
            "Arrow Keys / Mouse: Navigate",
            "Enter/Space/Click: Toggle/Select",
            "ESC: Back"
        ]
        
        y_offset = SCREEN_HEIGHT - 100
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (120, 120, 120))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 25