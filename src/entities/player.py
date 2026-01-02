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
        
        # Squash and stretch
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.target_scale_x = 1.0
        self.target_scale_y = 1.0
        self.squash_speed = 15.0
        
        # Triple jump hat
        self.hat_alpha = 0.0  # Alpha for hat fade effect
        self.hat_target_alpha = 0.0
        
        # Magnet visual
        self.magnet_active = False
        self.magnet_alpha = 0.0
        self.magnet_target_alpha = 0.0
        
        # Speed boost cape
        self.speed_boost_powerup_active = False
        self.cape_alpha = 0.0
        self.cape_target_alpha = 0.0
        self.cape_animation_time = 0.0
        
        # Triple jump tracking
        self.triple_jump_used = False
    
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
            # If helicopter is active, cancel it and enter falling state
            if self.helicopter_active:
                self.deactivate_helicopter()
                # No sound event, just cancel
            # Prioritize jumping if we still have jumps available
            elif self.can_jump():
                sound_event = self.jump()
            # Only activate helicopter if we've used both jumps (jump_count >= 2)
            # and we're not on the ground
            elif self.can_helicopter and not self.helicopter_active and not self.on_ground and self.jump_count >= 2:
                sound_event = self.activate_helicopter()
        
        # Variable jump height
        if input_handler.jump_released and self.velocity.y < 0:
            self.velocity.y *= VARIABLE_JUMP_MULTIPLIER
        
        # Update helicopter
        if self.helicopter_active:
            self.helicopter_time += dt
            # No time limit - helicopter lasts until landing on platform
            
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
        
        # Update squash and stretch
        self._update_squash_stretch(dt)
        
        # Update hat alpha (fade in when triple jump available, fade out when used)
        if self.max_jumps > 2 and self.jump_count < 3:
            # Triple jump available - show hat
            self.hat_target_alpha = 255.0
        else:
            # No triple jump or already used - hide hat
            self.hat_target_alpha = 0.0
        
        # Smooth transition for hat
        alpha_speed = 500.0  # Alpha units per second
        if self.hat_alpha < self.hat_target_alpha:
            self.hat_alpha = min(self.hat_alpha + alpha_speed * dt, self.hat_target_alpha)
        elif self.hat_alpha > self.hat_target_alpha:
            self.hat_alpha = max(self.hat_alpha - alpha_speed * dt, self.hat_target_alpha)
        
        # Update magnet alpha
        self.magnet_target_alpha = 255.0 if self.magnet_active else 0.0
        if self.magnet_alpha < self.magnet_target_alpha:
            self.magnet_alpha = min(self.magnet_alpha + alpha_speed * dt, self.magnet_target_alpha)
        elif self.magnet_alpha > self.magnet_target_alpha:
            self.magnet_alpha = max(self.magnet_alpha - alpha_speed * dt, self.magnet_target_alpha)
        
        # Update cape alpha
        self.cape_target_alpha = 255.0 if self.speed_boost_powerup_active else 0.0
        if self.cape_alpha < self.cape_target_alpha:
            self.cape_alpha = min(self.cape_alpha + alpha_speed * dt, self.cape_target_alpha)
        elif self.cape_alpha > self.cape_target_alpha:
            self.cape_alpha = max(self.cape_alpha - alpha_speed * dt, self.cape_target_alpha)
        
        # Update cape animation time for flowing effect
        if self.cape_alpha > 0:
            self.cape_animation_time += dt
        
        return sound_event
    
    def set_magnet_active(self, active):
        """Set whether the magnet power-up is active."""
        self.magnet_active = active
    
    def set_speed_boost_powerup_active(self, active):
        """Set whether the speed boost power-up is active."""
        self.speed_boost_powerup_active = active
    
    def jump(self):
        """Execute jump based on current jump count. Returns sound event name."""
        if self.jump_count == 0:
            # First jump
            self.velocity.y = JUMP_VELOCITY
            self.state = PlayerState.JUMPING
            self.on_ground = False
            self.jump_count = 1
            self.coyote_time = 0
            
            # Squash and stretch: compress then stretch
            self.target_scale_x = 1.2
            self.target_scale_y = 0.8
            
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
            
            # Squash and stretch: more dramatic for double jump
            self.target_scale_x = 1.3
            self.target_scale_y = 0.7
            
            return 'double_jump'
        
        elif self.jump_count == 2 and self.max_jumps > 2:
            # Triple jump (only available with extra jump power-up)
            self.velocity.y = TRIPLE_JUMP_VELOCITY  # Significantly higher jump!
            self.state = PlayerState.DOUBLE_JUMPING
            self.jump_count = 3
            # Helicopter already enabled from double jump
            
            # Mark triple jump as used (will be consumed on landing)
            self.triple_jump_used = True
            
            # Squash and stretch - more dramatic for the powerful triple jump
            self.target_scale_x = 1.4
            self.target_scale_y = 0.6
            
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
        
        # Squash and stretch: squash on landing
        self.target_scale_x = 0.8
        self.target_scale_y = 1.2
        
        # Signal that triple jump was used (if it was)
        # The play state will handle removing the power-up
        
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
    
    def _update_squash_stretch(self, dt):
        """Update squash and stretch animation."""
        # Lerp towards target scale
        self.scale_x += (self.target_scale_x - self.scale_x) * self.squash_speed * dt
        self.scale_y += (self.target_scale_y - self.scale_y) * self.squash_speed * dt
        
        # Return to normal scale
        self.target_scale_x += (1.0 - self.target_scale_x) * 5.0 * dt
        self.target_scale_y += (1.0 - self.target_scale_y) * 5.0 * dt
        
        # Clamp scales
        self.scale_x = max(0.5, min(1.5, self.scale_x))
        self.scale_y = max(0.5, min(1.5, self.scale_y))
    
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
        Render player sprite with squash and stretch.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        if self.animation_controller:
            sprite = self.animation_controller.get_current_sprite()
            if sprite:
                pos = self.get_render_position(camera)
                
                # Adjust position for helicopter sprite (which is taller due to rotor)
                if self.state == PlayerState.HELICOPTER:
                    # Helicopter sprite is 8 pixels taller (scaled by PLAYER_SCALE)
                    # Offset it down so the body aligns with the collision box
                    pos = (pos[0], pos[1] - (8 * PLAYER_SCALE))
                
                # Render speed lines BEHIND player first (so they don't overlap other visuals)
                if self.cape_alpha > 0:
                    self._render_cape(screen, pos)
                
                # Flip sprite if facing left
                if not self.facing_right:
                    sprite = pygame.transform.flip(sprite, True, False)
                
                # Apply squash and stretch
                if abs(self.scale_x - 1.0) > 0.01 or abs(self.scale_y - 1.0) > 0.01:
                    new_width = int(sprite.get_width() * self.scale_x)
                    new_height = int(sprite.get_height() * self.scale_y)
                    sprite = pygame.transform.scale(sprite, (new_width, new_height))
                    
                    # Adjust position to keep bottom-center anchored
                    pos = (
                        pos[0] - (new_width - self.width) // 2,
                        pos[1] - (new_height - self.height)
                    )
                
                screen.blit(sprite, pos)
                
                # Render "3X" hat ABOVE player
                if self.hat_alpha > 0:
                    self._render_hat(screen, pos)
                
                # Render magnet IN FRONT of player
                if self.magnet_alpha > 0:
                    self._render_magnet(screen, pos)
        else:
            # Fallback: draw colored rectangle with squash/stretch
            pos = self.get_render_position(camera)
            width = int(self.width * self.scale_x)
            height = int(self.height * self.scale_y)
            adjusted_pos = (
                pos[0] - (width - self.width) // 2,
                pos[1] - (height - self.height)
            )
            
            # Render speed lines BEHIND player first
            if self.cape_alpha > 0:
                self._render_cape(screen, adjusted_pos)
            
            pygame.draw.rect(screen, PLAYER_PRIMARY,
                (adjusted_pos[0], adjusted_pos[1], width, height))
            
            # Render "3X" hat ABOVE player
            if self.hat_alpha > 0:
                self._render_hat(screen, adjusted_pos)
            
            # Render magnet IN FRONT of player
            if self.magnet_alpha > 0:
                self._render_magnet(screen, adjusted_pos)
    
    def _render_hat(self, screen, player_pos):
        """
        Render the "3X" hat above the player.
        
        Args:
            screen: pygame.Surface to draw on
            player_pos: Player's current render position (x, y)
        """
        # Hat position (centered above player)
        hat_x = player_pos[0] + self.width // 2
        hat_y = player_pos[1] - 35  # Above the player (moved up for bigger hat)
        
        # Create hat surface with alpha (bigger size)
        hat_size = 60
        hat_surface = pygame.Surface((hat_size, hat_size), pygame.SRCALPHA)
        
        # Draw hat base (simple cap shape)
        hat_color = (50, 255, 50, int(self.hat_alpha))
        outline_color = (0, 0, 0, int(self.hat_alpha))
        
        # Hat brim (rectangle) - scaled up
        brim_rect = pygame.Rect(8, 40, 44, 12)
        pygame.draw.rect(hat_surface, hat_color, brim_rect, border_radius=3)
        pygame.draw.rect(hat_surface, outline_color, brim_rect, 2, border_radius=3)
        
        # Hat top (rounded rectangle) - scaled up
        top_rect = pygame.Rect(12, 12, 36, 30)
        pygame.draw.rect(hat_surface, hat_color, top_rect, border_radius=6)
        pygame.draw.rect(hat_surface, outline_color, top_rect, 2, border_radius=6)
        
        # Draw "3X" text on hat - larger font
        font = pygame.font.Font(None, 32)
        text_color = (255, 255, 255, int(self.hat_alpha))
        text_surface = font.render("3X", True, (255, 255, 255))
        
        # Apply alpha to text
        text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        text_with_alpha.fill((255, 255, 255, int(self.hat_alpha)))
        text_with_alpha.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Center text on hat
        text_rect = text_with_alpha.get_rect(center=(hat_size // 2, 27))
        hat_surface.blit(text_with_alpha, text_rect)
        
        # Blit hat to screen (centered above player)
        screen.blit(hat_surface, (hat_x - hat_size // 2, hat_y))
    
    def _render_magnet(self, screen, player_pos):
        """
        Render the magnet sprite in front of the player.
        
        Args:
            screen: pygame.Surface to draw on
            player_pos: Player's current render position (x, y)
        """
        # Magnet position (in front of player, at chest level)
        magnet_x = player_pos[0] + self.width + 5  # To the right of player
        magnet_y = player_pos[1] + self.height // 2 - 15  # Center vertically
        
        # Create magnet surface with alpha
        magnet_width = 30
        magnet_height = 35
        magnet_surface = pygame.Surface((magnet_width, magnet_height), pygame.SRCALPHA)
        
        # Magnet colors with alpha
        red_color = (255, 50, 50, int(self.magnet_alpha))
        blue_color = (50, 50, 255, int(self.magnet_alpha))
        gray_color = (150, 150, 150, int(self.magnet_alpha))
        outline_color = (0, 0, 0, int(self.magnet_alpha))
        
        # Draw horseshoe magnet shape
        # Left pole (red/north)
        left_pole = pygame.Rect(3, 5, 8, 25)
        pygame.draw.rect(magnet_surface, red_color, left_pole, border_radius=2)
        pygame.draw.rect(magnet_surface, outline_color, left_pole, 2, border_radius=2)
        
        # Right pole (blue/south)
        right_pole = pygame.Rect(19, 5, 8, 25)
        pygame.draw.rect(magnet_surface, blue_color, right_pole, border_radius=2)
        pygame.draw.rect(magnet_surface, outline_color, right_pole, 2, border_radius=2)
        
        # Connecting bar at top
        top_bar = pygame.Rect(3, 5, 24, 8)
        pygame.draw.rect(magnet_surface, gray_color, top_bar, border_radius=2)
        pygame.draw.rect(magnet_surface, outline_color, top_bar, 2, border_radius=2)
        
        # Add "N" and "S" labels
        font = pygame.font.Font(None, 16)
        
        # North label (on red side)
        n_text = font.render("N", True, (255, 255, 255))
        n_with_alpha = pygame.Surface(n_text.get_size(), pygame.SRCALPHA)
        n_with_alpha.fill((255, 255, 255, int(self.magnet_alpha)))
        n_with_alpha.blit(n_text, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        magnet_surface.blit(n_with_alpha, (5, 15))
        
        # South label (on blue side)
        s_text = font.render("S", True, (255, 255, 255))
        s_with_alpha = pygame.Surface(s_text.get_size(), pygame.SRCALPHA)
        s_with_alpha.fill((255, 255, 255, int(self.magnet_alpha)))
        s_with_alpha.blit(s_text, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        magnet_surface.blit(s_with_alpha, (21, 15))
        
        # Blit magnet to screen
        screen.blit(magnet_surface, (magnet_x, magnet_y))
    
    def _render_cape(self, screen, player_pos):
        """
        Render horizontal blue speed lines behind the player with glow effect.
        
        Args:
            screen: pygame.Surface to draw on
            player_pos: Player's current render position (x, y)
        """
        import math
        
        # Speed lines configuration
        num_lines = 4
        line_spacing = 12  # Vertical spacing between lines
        line_length_base = 40  # Base length of lines
        line_thickness = 6  # Thicker lines
        
        # Starting position (behind player, centered vertically)
        start_x = player_pos[0] - 10  # Behind the player
        start_y = player_pos[1] + self.height // 2 - (num_lines * line_spacing) // 2
        
        # Animate lines moving backward
        animation_offset = (self.cape_animation_time * 200) % 30  # Cycle every 30 pixels
        
        # Draw multiple horizontal lines
        for i in range(num_lines):
            # Calculate line position
            line_y = start_y + i * line_spacing
            
            # Vary line length slightly for visual interest
            length_variation = math.sin(self.cape_animation_time * 5 + i) * 5
            line_length = line_length_base + length_variation
            
            # Offset each line differently for staggered animation
            offset = (animation_offset + i * 10) % 30
            line_x = start_x - offset
            
            # Calculate alpha based on position (fade out as they move back)
            fade_factor = 1.0 - (offset / 30.0)
            line_alpha = int(self.cape_alpha * fade_factor)
            
            if line_alpha > 0:
                # Create line surface with extra space for glow
                glow_padding = 6
                line_surface = pygame.Surface(
                    (int(line_length) + glow_padding * 2, line_thickness + glow_padding * 2),
                    pygame.SRCALPHA
                )
                
                # Draw glow layers (multiple layers for stronger glow effect)
                glow_color_outer = (0, 150, 255, int(line_alpha * 0.3))
                glow_color_mid = (50, 180, 255, int(line_alpha * 0.5))
                glow_color_inner = (100, 210, 255, int(line_alpha * 0.7))
                
                # Outer glow (largest)
                pygame.draw.rect(line_surface, glow_color_outer,
                    (2, 2, int(line_length) + 8, line_thickness + 8), border_radius=3)
                
                # Mid glow
                pygame.draw.rect(line_surface, glow_color_mid,
                    (3, 3, int(line_length) + 6, line_thickness + 6), border_radius=2)
                
                # Inner glow
                pygame.draw.rect(line_surface, glow_color_inner,
                    (4, 4, int(line_length) + 4, line_thickness + 4), border_radius=2)
                
                # Black outline
                outline_color = (0, 0, 0, line_alpha)
                pygame.draw.rect(line_surface, outline_color,
                    (glow_padding - 1, glow_padding - 1, int(line_length) + 2, line_thickness + 2),
                    width=2, border_radius=2)
                
                # Main blue speed line (bright cyan/blue for speed)
                line_color = (0, 220, 255, line_alpha)
                pygame.draw.rect(line_surface, line_color,
                    (glow_padding, glow_padding, int(line_length), line_thickness),
                    border_radius=2)
                
                # Blit line to screen (adjust position for glow padding)
                screen.blit(line_surface, (int(line_x) - glow_padding, int(line_y) - glow_padding))