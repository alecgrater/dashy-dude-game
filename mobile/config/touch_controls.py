"""
Touch input handling for mobile devices.
Converts touch events to game actions.
"""
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Callable


class TouchAction(Enum):
    """Possible touch actions."""
    NONE = auto()
    TAP = auto()
    HOLD = auto()
    RELEASE = auto()
    SWIPE_UP = auto()
    SWIPE_DOWN = auto()
    SWIPE_LEFT = auto()
    SWIPE_RIGHT = auto()


class GameAction(Enum):
    """Game actions triggered by touch."""
    NONE = auto()
    JUMP = auto()
    DOUBLE_JUMP = auto()
    HELICOPTER_START = auto()
    HELICOPTER_STOP = auto()
    PAUSE = auto()
    MENU_SELECT = auto()


@dataclass
class Touch:
    """Represents a single touch point."""
    id: int
    start_x: float
    start_y: float
    current_x: float
    current_y: float
    start_time: float
    is_active: bool = True
    
    @property
    def duration(self) -> float:
        """Get touch duration in seconds."""
        return time.time() - self.start_time
    
    @property
    def delta_x(self) -> float:
        """Get horizontal movement."""
        return self.current_x - self.start_x
    
    @property
    def delta_y(self) -> float:
        """Get vertical movement."""
        return self.current_y - self.start_y
    
    @property
    def distance(self) -> float:
        """Get total distance moved."""
        return (self.delta_x ** 2 + self.delta_y ** 2) ** 0.5


@dataclass
class TouchState:
    """Current state of touch input."""
    active_touches: List[Touch] = field(default_factory=list)
    last_tap_time: float = 0.0
    tap_count: int = 0
    is_holding: bool = False
    hold_start_time: float = 0.0


class TouchController:
    """
    Handles touch input and converts to game actions.
    
    Usage:
        controller = TouchController()
        
        # In event loop:
        for event in pygame.event.get():
            action = controller.handle_event(event)
            if action == GameAction.JUMP:
                player.jump()
        
        # In update loop:
        action = controller.update(dt)
        if action == GameAction.HELICOPTER_START:
            player.start_helicopter()
    """
    
    # Touch thresholds
    TAP_THRESHOLD = 0.2  # seconds
    HOLD_THRESHOLD = 0.3  # seconds
    DOUBLE_TAP_THRESHOLD = 0.3  # seconds between taps
    SWIPE_THRESHOLD = 50  # pixels
    
    def __init__(self, screen_width: int = 844, screen_height: int = 390):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = TouchState()
        self.callbacks: dict[GameAction, List[Callable]] = {}
        
        # Track jump state for double jump detection
        self.jump_count = 0
        self.last_jump_time = 0.0
        self.is_helicopter_active = False
        
    def register_callback(self, action: GameAction, callback: Callable):
        """Register a callback for a game action."""
        if action not in self.callbacks:
            self.callbacks[action] = []
        self.callbacks[action].append(callback)
    
    def _trigger_action(self, action: GameAction):
        """Trigger callbacks for an action."""
        if action in self.callbacks:
            for callback in self.callbacks[action]:
                callback()
    
    def handle_touch_down(self, touch_id: int, x: float, y: float) -> GameAction:
        """
        Handle touch down event.
        
        Args:
            touch_id: Unique identifier for the touch
            x: X coordinate
            y: Y coordinate
        
        Returns:
            GameAction triggered by this touch
        """
        touch = Touch(
            id=touch_id,
            start_x=x,
            start_y=y,
            current_x=x,
            current_y=y,
            start_time=time.time()
        )
        self.state.active_touches.append(touch)
        
        # Check for double tap
        current_time = time.time()
        if current_time - self.state.last_tap_time < self.DOUBLE_TAP_THRESHOLD:
            self.state.tap_count += 1
        else:
            self.state.tap_count = 1
        
        return GameAction.NONE
    
    def handle_touch_move(self, touch_id: int, x: float, y: float) -> GameAction:
        """
        Handle touch move event.
        
        Args:
            touch_id: Unique identifier for the touch
            x: New X coordinate
            y: New Y coordinate
        
        Returns:
            GameAction triggered by this movement
        """
        for touch in self.state.active_touches:
            if touch.id == touch_id:
                touch.current_x = x
                touch.current_y = y
                break
        
        return GameAction.NONE
    
    def handle_touch_up(self, touch_id: int, x: float, y: float) -> GameAction:
        """
        Handle touch up event.
        
        Args:
            touch_id: Unique identifier for the touch
            x: Final X coordinate
            y: Final Y coordinate
        
        Returns:
            GameAction triggered by this release
        """
        action = GameAction.NONE
        touch_to_remove = None
        
        for touch in self.state.active_touches:
            if touch.id == touch_id:
                touch.current_x = x
                touch.current_y = y
                touch.is_active = False
                touch_to_remove = touch
                
                # Determine action based on touch characteristics
                action = self._classify_touch(touch)
                break
        
        if touch_to_remove:
            self.state.active_touches.remove(touch_to_remove)
        
        # Stop helicopter on release
        if self.is_helicopter_active:
            self.is_helicopter_active = False
            self._trigger_action(GameAction.HELICOPTER_STOP)
            if action == GameAction.NONE:
                action = GameAction.HELICOPTER_STOP
        
        self.state.is_holding = False
        
        return action
    
    def _classify_touch(self, touch: Touch) -> GameAction:
        """
        Classify a completed touch into an action.
        
        Args:
            touch: The completed touch
        
        Returns:
            The game action this touch represents
        """
        duration = touch.duration
        distance = touch.distance
        
        # Check for swipe
        if distance > self.SWIPE_THRESHOLD:
            # Determine swipe direction
            if abs(touch.delta_x) > abs(touch.delta_y):
                # Horizontal swipe
                if touch.delta_x > 0:
                    return GameAction.NONE  # Swipe right - not used
                else:
                    return GameAction.NONE  # Swipe left - not used
            else:
                # Vertical swipe
                if touch.delta_y < 0:  # Swipe up (negative Y is up)
                    return self._handle_jump()
                else:
                    return GameAction.NONE  # Swipe down - not used
        
        # Check for tap (short duration, small movement)
        if duration < self.TAP_THRESHOLD:
            self.state.last_tap_time = time.time()
            return self._handle_jump()
        
        return GameAction.NONE
    
    def _handle_jump(self) -> GameAction:
        """
        Handle jump action, tracking for double jump.
        
        Returns:
            JUMP or DOUBLE_JUMP action
        """
        current_time = time.time()
        
        # Reset jump count if too much time has passed
        if current_time - self.last_jump_time > 0.5:
            self.jump_count = 0
        
        self.jump_count += 1
        self.last_jump_time = current_time
        
        if self.jump_count == 1:
            self._trigger_action(GameAction.JUMP)
            return GameAction.JUMP
        elif self.jump_count >= 2:
            self._trigger_action(GameAction.DOUBLE_JUMP)
            return GameAction.DOUBLE_JUMP
        
        return GameAction.JUMP
    
    def update(self, dt: float) -> GameAction:
        """
        Update touch state and check for hold actions.
        
        Args:
            dt: Delta time in seconds
        
        Returns:
            GameAction if a hold action is triggered
        """
        if not self.state.active_touches:
            return GameAction.NONE
        
        # Check for hold (for helicopter)
        for touch in self.state.active_touches:
            if touch.is_active and touch.duration > self.HOLD_THRESHOLD:
                if not self.state.is_holding:
                    self.state.is_holding = True
                    self.state.hold_start_time = time.time()
                
                # Activate helicopter if holding after a jump
                if self.jump_count >= 2 and not self.is_helicopter_active:
                    self.is_helicopter_active = True
                    self._trigger_action(GameAction.HELICOPTER_START)
                    return GameAction.HELICOPTER_START
        
        return GameAction.NONE
    
    def reset(self):
        """Reset touch state (e.g., on game over)."""
        self.state = TouchState()
        self.jump_count = 0
        self.last_jump_time = 0.0
        self.is_helicopter_active = False
    
    def reset_jump_count(self):
        """Reset jump count (e.g., when landing)."""
        self.jump_count = 0
    
    def is_touching(self) -> bool:
        """Check if there are any active touches."""
        return len(self.state.active_touches) > 0
    
    def get_touch_position(self) -> Optional[Tuple[float, float]]:
        """Get the position of the first active touch."""
        if self.state.active_touches:
            touch = self.state.active_touches[0]
            return (touch.current_x, touch.current_y)
        return None


class PygameTouchAdapter:
    """
    Adapter to convert Pygame touch/mouse events to TouchController events.
    
    On desktop, mouse events are treated as touch events for testing.
    On mobile (iOS), actual touch events are used.
    """
    
    def __init__(self, controller: TouchController):
        self.controller = controller
        self.mouse_touch_id = 0  # Fake touch ID for mouse
    
    def handle_event(self, event) -> GameAction:
        """
        Handle a Pygame event and convert to game action.
        
        Args:
            event: Pygame event
        
        Returns:
            GameAction triggered by this event
        """
        import pygame
        
        # Handle mouse events (for desktop testing)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.controller.handle_touch_down(
                    self.mouse_touch_id, event.pos[0], event.pos[1]
                )
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                return self.controller.handle_touch_up(
                    self.mouse_touch_id, event.pos[0], event.pos[1]
                )
        
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left button held
                return self.controller.handle_touch_move(
                    self.mouse_touch_id, event.pos[0], event.pos[1]
                )
        
        # Handle actual touch events (for mobile)
        elif event.type == pygame.FINGERDOWN:
            x = event.x * self.controller.screen_width
            y = event.y * self.controller.screen_height
            return self.controller.handle_touch_down(event.finger_id, x, y)
        
        elif event.type == pygame.FINGERUP:
            x = event.x * self.controller.screen_width
            y = event.y * self.controller.screen_height
            return self.controller.handle_touch_up(event.finger_id, x, y)
        
        elif event.type == pygame.FINGERMOTION:
            x = event.x * self.controller.screen_width
            y = event.y * self.controller.screen_height
            return self.controller.handle_touch_move(event.finger_id, x, y)
        
        return GameAction.NONE