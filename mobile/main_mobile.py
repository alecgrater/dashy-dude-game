"""
Dashy Dude - Mobile Entry Point

This is the main entry point for the iOS version of Dashy Dude.
It initializes mobile-specific settings and touch controls.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import mobile configuration
from mobile.config.mobile_constants import (
    MOBILE_SCREEN_WIDTH, MOBILE_SCREEN_HEIGHT,
    LANDSCAPE_MODE, IS_IOS,
    MOBILE_MAX_PARTICLES, MOBILE_TARGET_FPS,
    SAFE_AREA_TOP, SAFE_AREA_BOTTOM,
    calculate_scale_factor, get_safe_area_rect
)
from mobile.config.touch_controls import TouchController, PygameTouchAdapter, GameAction

# Override constants for mobile before importing game
import src.utils.constants as constants

# Set mobile screen dimensions
if LANDSCAPE_MODE:
    constants.SCREEN_WIDTH = MOBILE_SCREEN_WIDTH
    constants.SCREEN_HEIGHT = MOBILE_SCREEN_HEIGHT
else:
    constants.SCREEN_WIDTH = MOBILE_SCREEN_HEIGHT
    constants.SCREEN_HEIGHT = MOBILE_SCREEN_WIDTH

# Reduce particles for mobile performance
constants.MAX_PARTICLES = MOBILE_MAX_PARTICLES
constants.FPS = MOBILE_TARGET_FPS

# Now import the game
import pygame
from src.game import Game


class MobileGame(Game):
    """
    Mobile-specific game class with touch controls.
    """
    
    def __init__(self):
        # Initialize touch controller before pygame
        self.touch_controller = TouchController(
            screen_width=constants.SCREEN_WIDTH,
            screen_height=constants.SCREEN_HEIGHT
        )
        self.touch_adapter = PygameTouchAdapter(self.touch_controller)
        
        # Call parent init
        super().__init__()
        
        # Calculate scale factor for UI
        self.scale_factor = calculate_scale_factor(
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT
        )
        
        # Get safe area for UI positioning
        self.safe_area = get_safe_area_rect(
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT
        )
        
        # Enable touch events
        pygame.event.set_allowed([
            pygame.FINGERDOWN,
            pygame.FINGERUP,
            pygame.FINGERMOTION,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ])
    
    def handle_events(self):
        """Handle pygame events with touch support."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            
            # Handle touch/mouse events
            action = self.touch_adapter.handle_event(event)
            
            # Convert touch actions to game input
            if action != GameAction.NONE:
                self._handle_touch_action(action)
            
            # Also pass event to current state for UI handling
            if self.current_state:
                self.current_state.handle_event(event)
    
    def _handle_touch_action(self, action: GameAction):
        """
        Convert touch action to game input.
        
        Args:
            action: The game action from touch input
        """
        # Simulate keyboard input for compatibility with existing code
        if action == GameAction.JUMP:
            # Simulate space key press
            self.input_handler.keys_pressed.add(pygame.K_SPACE)
            self.input_handler.keys_just_pressed.add(pygame.K_SPACE)
        
        elif action == GameAction.DOUBLE_JUMP:
            # Simulate space key press for double jump
            self.input_handler.keys_pressed.add(pygame.K_SPACE)
            self.input_handler.keys_just_pressed.add(pygame.K_SPACE)
        
        elif action == GameAction.HELICOPTER_START:
            # Keep space held for helicopter
            self.input_handler.keys_pressed.add(pygame.K_SPACE)
        
        elif action == GameAction.HELICOPTER_STOP:
            # Release space
            self.input_handler.keys_pressed.discard(pygame.K_SPACE)
            self.input_handler.keys_just_released.add(pygame.K_SPACE)
        
        elif action == GameAction.PAUSE:
            # Simulate escape key
            self.input_handler.keys_just_pressed.add(pygame.K_ESCAPE)
    
    def update(self, dt):
        """Update game logic with touch controller update."""
        # Update touch controller
        action = self.touch_controller.update(dt)
        if action != GameAction.NONE:
            self._handle_touch_action(action)
        
        # Call parent update
        super().update(dt)
    
    def render(self):
        """Render with mobile-specific adjustments."""
        # Call parent render
        super().render()
        
        # Optionally render touch indicators for debugging
        if hasattr(self, '_debug_touch') and self._debug_touch:
            self._render_touch_debug()
    
    def _render_touch_debug(self):
        """Render touch points for debugging."""
        for touch in self.touch_controller.state.active_touches:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0, 128),
                (int(touch.current_x), int(touch.current_y)),
                30,
                2
            )


def main():
    """Mobile main entry point."""
    print("=" * 50)
    print("DASHY DUDE - Mobile Edition")
    print("=" * 50)
    print()
    print("Touch Controls:")
    print("  TAP - Jump")
    print("  TAP AGAIN - Double Jump")
    print("  HOLD - Helicopter Glide")
    print()
    print("Starting game...")
    print()
    
    game = MobileGame()
    game.run()
    
    print()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()