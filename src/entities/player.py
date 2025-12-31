"""
Player character with advanced jump mechanics.
"""
from enum import Enum
import pygame
from src.utils.constants import *
from src.utils.math_utils import Vector2


class PlayerState(Enum):
    """Player state machine states."""
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    DOUBLE_JUMPING = "double_jumping"
    HELICOPTER = "helicopter"
    FALLING = "falling"
    DEAD = "dead"


class Player:
    """
    Player character with:
    - Single jump
    - Double jump
    - Helicopter glide (Rayman-style)
    - Coyote time
    - Jump buffering
    - Variable jump height
    """
    
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(PLAYER_RUN_SPEED, 0)  # Always moving forward
        self.width = PLAYER_WIDTH * PLAYER_SCALE
        self.height = PLAYER_HEIGHT * PLAYER_SCALE
        
        # Collision box (slightly smaller for better feel)
        self.collision_width = PLAYER_COLLISION_WIDTH * PLAYER_SCALE
        self.collision_height = PLAYER_COLLISION_HEIGHT * PLAYER_SCALE
        
        # State
        self.state = PlayerState.IDLE
        self.on_ground = False
        self.current_platform = None
        
        # Jump mechanics
        self.jump_count = 0
        self.max_jumps = 2  # Single jump + double jump
        
        # Double jump speed boost
        self.speed_boost_active = False
        self.speed_boost_timer = 0.0
        self.base_speed = PLAYER_RUN_SPEED
        
        # Helicopter glide
        self.helicopter_active = False
        self.helicopter_time = 0.0
        self.helicopter_max_time = HELICOPTER_DURATION
        self.can_helicopter = False
        
        # Advanced mechanics
        self.coyote_time = 0.0
        self.jump_buffer = 0.0
        
        # Animation
        self.facing_right = True
        self.animation_controller = None
        
        # Particles
        self.particle_timer = 0.0
    
    def update(self, dt, input_handler, physics_engine):
        """
        Update player state and physics.
        
        Args:
            dt: Delta time in seconds
            input_handler: InputHandler instance
            physics_engine: PhysicsEngine instance
            
        Returns:
            Sound event name if an action occurred, None otherwise
        """
        sound_event = None
        
        # Update timers
        if not self.on_ground:
            self.coyote_time -= dt
        else:
            self.coyote_time = COYOTE_TIME
        
        if self.jump_buffer > 0:
            self.jump_buffer -= dt
        
        # Update speed boost timer
        if self.speed_boost_active:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
                self.velocity.x = self.base_speed
        
        # Handle input - only process new jump presses, not held
        if input_handler.jump_pressed:
            # Check if we can activate helicopter (third press after double jump)
            if self.can_helicopter and not self.helicopter_active and not self.on_ground:
                sound_event = self.activate_helicopter()
            # Otherwise try to jump
            elif self.can_jump():
                sound_event = self.jump()
        
        # Variable jump height
        if input_handler.jump_released and self.velocity.y < 0:
            self.velocity.y *= VARIABLE_JUMP_MULTIPLIER
        
        # Update helicopter
        if self.helicopter_active:
            self.helicopter_time += dt
            if self.helicopter_time >= self.helicopter_max_time:
                self.deactivate_helicopter()
            
            # Override gravity with slow fall
            self.velocity.y = HELICOPTER_FALL_SPEED
            
            # Particle timer
            self.particle_timer += dt
        
        # Apply physics
        if not self.helicopter_active:
            physics_engine.apply_gravity(self, dt)
        
        physics_engine.integrate_velocity(self, dt)
        
        # Update state
        self._update_state()
        
        # Update animation
        if self.animation_controller:
            self.animation_controller.update(dt, self.state)
        
        return sound_event
    
    def jump(self):
        """Execute jump based on current jump count. Returns sound event name."""
        if self.jump_count == 0:
            # First jump
            self.velocity.y = JUMP_VELOCITY
            self.state = PlayerState.JUMPING
            self.on_ground = False
            self.jump_count = 1
            self.coyote_time = 0
            return 'jump'
            
        elif self.jump_count == 1:
            # Double jump with speed boost
            self.velocity.y = DOUBLE_JUMP_VELOCITY
            self.state = PlayerState.DOUBLE_JUMPING
            self.jump_count = 2
            self.can_helicopter = True  # Enable helicopter after double jump
            
            # Activate speed boost
            self.speed_boost_active = True
            self.speed_boost_timer = DOUBLE_JUMP_BOOST_DURATION
            self.velocity.x = self.base_speed + DOUBLE_JUMP_SPEED_BOOST
            
            return 'double_jump'
        
        return None
    
    def activate_helicopter(self):
        """Start helicopter glide. Returns sound event name."""
        self.helicopter_active = True
        self.helicopter_time = 0.0
        self.state = PlayerState.HELICOPTER
        self.particle_timer = 0.0
        return 'helicopter'
    
    def deactivate_helicopter(self):
        """Stop helicopter glide."""
        self.helicopter_active = False
        self.can_helicopter = False
    
    def can_jump(self):
        """Check if player can jump (includes coyote time)."""
        # First jump: must be on ground or have coyote time
        if self.jump_count == 0:
            return (self.on_ground or self.coyote_time > 0)
        # Double jump: can jump if haven't used all jumps
        elif self.jump_count < self.max_jumps:
            return True
        return False
    
    def land_on_platform(self, platform):
        """Reset jump state when landing on platform. Returns sound event name."""
        self.on_ground = True
        self.current_platform = platform
        self.jump_count = 0
        self.helicopter_active = False
        self.helicopter_time = 0.0
        self.can_helicopter = False
        self.coyote_time = COYOTE_TIME
        
        # Reset speed boost on landing
        self.speed_boost_active = False
        self.velocity.x = self.base_speed
        
        return 'landing'
    
    def die(self):
        """Player death. Returns sound event name."""
        self.state = PlayerState.DEAD
        self.velocity.y = -300  # Small bounce
        return 'death'
    
    def _update_state(self):
        """Update player state based on conditions."""
        if self.state == PlayerState.DEAD:
            return
        
        if self.helicopter_active:
            self.state = PlayerState.HELICOPTER
        elif self.on_ground:
            self.state = PlayerState.RUNNING
        elif self.velocity.y < 0:
            if self.jump_count == 2:
                self.state = PlayerState.DOUBLE_JUMPING
            else:
                self.state = PlayerState.JUMPING
        else:
            self.state = PlayerState.FALLING
    
    def get_collision_rect(self):
        """
        Get collision rectangle for physics.
        
        Returns:
            pygame.Rect for collision detection
        """
        # Center the collision box
        offset_x = (self.width - self.collision_width) / 2
        offset_y = (self.height - self.collision_height) / 2
        
        return pygame.Rect(
            self.position.x + offset_x,
            self.position.y + offset_y,
            self.collision_width,
            self.collision_height
        )
    
    def get_render_position(self, camera):
        """
        Get screen position for rendering.
        
        Args:
            camera: Camera instance
        
        Returns:
            Tuple of (x, y) screen coordinates
        """
        screen_pos = camera.world_to_screen(self.position)
        return (int(screen_pos.x), int(screen_pos.y))
    
    def render(self, screen, camera):
        """
        Render player sprite.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        if self.animation_controller:
            sprite = self.animation_controller.get_current_sprite()
            if sprite:
                pos = self.get_render_position(camera)
                
                # Flip sprite if facing left
                if not self.facing_right:
                    sprite = pygame.transform.flip(sprite, True, False)
                
                screen.blit(sprite, pos)
        else:
            # Fallback: draw colored rectangle
            pos = self.get_render_position(camera)
            pygame.draw.rect(screen, PLAYER_PRIMARY,
                (pos[0], pos[1], self.width, self.height))