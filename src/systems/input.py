"""
Input handling system with buffering and edge detection.
"""
import pygame


class InputHandler:
    """
    Handles keyboard and mouse input with advanced features:
    - Edge detection (pressed/released events)
    - Input buffering for jump
    - Variable jump height support
    """
    
    def __init__(self):
        # Current frame state
        self.jump_pressed = False  # Just pressed this frame
        self.jump_held = False  # Currently held
        self.jump_released = False  # Just released this frame
        
        # Previous frame state for edge detection
        self._prev_jump = False
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.mouse_held = False
        
        self._prev_mouse = False
        
        # Pause/menu
        self.pause_pressed = False
        self._prev_pause = False
    
    def update(self):
        """
        Update input state. Call once per frame before game logic.
        """
        # Get current keyboard state
        keys = pygame.key.get_pressed()
        current_jump = keys[pygame.K_SPACE]
        current_pause = keys[pygame.K_ESCAPE]
        
        # Detect jump edges
        self.jump_pressed = current_jump and not self._prev_jump
        self.jump_held = current_jump
        self.jump_released = not current_jump and self._prev_jump
        
        # Detect pause edge
        self.pause_pressed = current_pause and not self._prev_pause
        
        # Update previous state
        self._prev_jump = current_jump
        self._prev_pause = current_pause
        
        # Get mouse state
        self.mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        current_mouse = mouse_buttons[0]  # Left click
        
        self.mouse_clicked = current_mouse and not self._prev_mouse
        self.mouse_held = current_mouse
        
        self._prev_mouse = current_mouse
    
    def reset(self):
        """Reset all input states."""
        self.jump_pressed = False
        self.jump_held = False
        self.jump_released = False
        self.mouse_clicked = False
        self.mouse_held = False
        self.pause_pressed = False
        self._prev_jump = False
        self._prev_mouse = False
        self._prev_pause = False