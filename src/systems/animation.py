"""
Animation system for sprite frame management.
"""
from enum import Enum
from src.utils.constants import *
from src.entities.player import PlayerState


class AnimationState(Enum):
    """Player animation states."""
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    DOUBLE_JUMPING = "double_jumping"
    HELICOPTER = "helicopter"
    FALLING = "falling"


class AnimationController:
    """
    Controls sprite animations with frame timing.
    """
    
    def __init__(self, sprite_sheets):
        """
        Initialize animation controller.
        
        Args:
            sprite_sheets: Dictionary mapping animation names to frame lists
        """
        self.sprite_sheets = sprite_sheets
        self.current_animation = AnimationState.IDLE
        self.current_frame = 0
        self.animation_time = 0.0
        
        # Frame durations for each animation (seconds per frame)
        self.frame_durations = {
            AnimationState.IDLE: 1.0 / IDLE_FPS,
            AnimationState.RUNNING: 1.0 / RUN_FPS,
            AnimationState.JUMPING: 1.0 / JUMP_FPS,
            AnimationState.DOUBLE_JUMPING: 1.0 / DOUBLE_JUMP_FPS,
            AnimationState.HELICOPTER: 1.0 / HELICOPTER_FPS,
            AnimationState.FALLING: 1.0 / JUMP_FPS,
        }
    
    def update(self, dt, player_state):
        """
        Update animation based on player state.
        
        Args:
            dt: Delta time in seconds
            player_state: Current PlayerState enum value
        """
        # Map player state to animation state
        new_animation = self._get_animation_for_state(player_state)
        
        # Change animation if needed
        if new_animation != self.current_animation:
            self.change_animation(new_animation)
        
        # Update frame timing
        self.animation_time += dt
        frame_duration = self.frame_durations[self.current_animation]
        
        if self.animation_time >= frame_duration:
            self.animation_time = 0.0
            self.current_frame += 1
            
            # Loop animation
            animation_key = self.current_animation.value
            if animation_key in self.sprite_sheets:
                frames = self.sprite_sheets[animation_key]
                if self.current_frame >= len(frames):
                    self.current_frame = 0
    
    def get_current_sprite(self):
        """
        Get the current animation frame sprite.
        
        Returns:
            pygame.Surface of current frame
        """
        animation_key = self.current_animation.value
        if animation_key in self.sprite_sheets:
            frames = self.sprite_sheets[animation_key]
            if frames and self.current_frame < len(frames):
                return frames[self.current_frame]
        
        # Return first frame of idle as fallback
        if "idle" in self.sprite_sheets and self.sprite_sheets["idle"]:
            return self.sprite_sheets["idle"][0]
        
        return None
    
    def change_animation(self, animation_state):
        """
        Change to a new animation.
        
        Args:
            animation_state: AnimationState enum value
        """
        self.current_animation = animation_state
        self.current_frame = 0
        self.animation_time = 0.0
    
    def _get_animation_for_state(self, player_state):
        """
        Map player state to animation state.
        
        Args:
            player_state: PlayerState enum value
        
        Returns:
            AnimationState enum value
        """
        mapping = {
            PlayerState.IDLE: AnimationState.IDLE,
            PlayerState.RUNNING: AnimationState.RUNNING,
            PlayerState.JUMPING: AnimationState.JUMPING,
            PlayerState.DOUBLE_JUMPING: AnimationState.DOUBLE_JUMPING,
            PlayerState.HELICOPTER: AnimationState.HELICOPTER,
            PlayerState.FALLING: AnimationState.FALLING,
        }
        
        return mapping.get(player_state, AnimationState.IDLE)