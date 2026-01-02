"""
Settings state for game configuration.
Includes FPS counter toggle, VSync toggle, and other performance settings.
"""

import pygame
from src.states.base_state import BaseState
from src.utils.constants import *


class SettingsState(BaseState):
    """Settings menu state."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
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
            {'name': 'FPS Counter', 'key': 'show_fps', 'type': 'toggle'},
            {'name': 'VSync', 'key': 'vsync', 'type': 'toggle'},
            {'name': 'Back', 'key': 'back', 'type': 'action'},
        ]
        
        self.selected_index = 0
        self.key_repeat_timer = 0
        self.key_repeat_delay = 0.15
    
    def enter(self):
        """Called when entering this state."""
        pass
    
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
        # Background
        screen.fill((20, 30, 50))
        
        # Title
        title_text = self.font_large.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Options
        y_offset = 200
        for i, option in enumerate(self.options):
            # Determine color based on selection
            if i == self.selected_index:
                color = (255, 255, 100)
                prefix = "> "
            else:
                color = (200, 200, 200)
                prefix = "  "
            
            # Render option name
            if option['type'] == 'toggle':
                value = "ON" if self.settings[option['key']] else "OFF"
                text = f"{prefix}{option['name']}: {value}"
            else:
                text = f"{prefix}{option['name']}"
            
            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(option_text, option_rect)
            
            y_offset += 60
        
        # Instructions
        instructions = [
            "Arrow Keys: Navigate",
            "Enter/Space: Select",
            "Left/Right: Toggle",
            "ESC: Back"
        ]
        
        y_offset = SCREEN_HEIGHT - 150
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (150, 150, 150))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 30