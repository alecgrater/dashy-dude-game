"""
Physics engine for gravity, velocity, and collision detection.
"""
from src.utils.constants import *
from src.utils.math_utils import rect_collision


class PhysicsEngine:
    """
    Handles physics simulation including:
    - Gravity application
    - Velocity integration
    - Collision detection (AABB)
    - One-way platform collision
    """
    
    def __init__(self):
        self.gravity = GRAVITY
    
    def apply_gravity(self, entity, dt):
        """
        Apply gravity acceleration to entity's velocity.
        
        Args:
            entity: Object with velocity.y attribute
            dt: Delta time in seconds
        """
        entity.velocity.y += self.gravity * dt
        
        # Clamp to max fall speed
        if entity.velocity.y > MAX_FALL_SPEED:
            entity.velocity.y = MAX_FALL_SPEED
    
    def integrate_velocity(self, entity, dt):
        """
        Update entity position based on velocity.
        
        Args:
            entity: Object with position and velocity attributes
            dt: Delta time in seconds
        """
        entity.position.x += entity.velocity.x * dt
        entity.position.y += entity.velocity.y * dt
    
    def check_platform_collision(self, player, platforms):
        """
        Check if player is colliding with any platform.
        Uses one-way collision (can jump through from below).
        
        Args:
            player: Player object with position, velocity, and collision box
            platforms: List of platform objects
        
        Returns:
            Platform object if collision detected, None otherwise
        """
        # Get player collision rectangle
        player_rect = player.get_collision_rect()
        
        # Only check collision if player is falling
        if player.velocity.y <= 0:
            return None
        
        # Add horizontal tolerance for helicopter mode to make landing more forgiving
        helicopter_tolerance = 12 if player.helicopter_active else 0
        
        for platform in platforms:
            if not platform.active:
                continue
            
            platform_rect = platform.get_rect()
            
            # Check horizontal overlap first (more efficient)
            # Expand player rect horizontally when in helicopter mode for more forgiving landing
            if not (player_rect.right + helicopter_tolerance > platform_rect.left and
                    player_rect.left - helicopter_tolerance < platform_rect.right):
                continue
            
            # Calculate where player was last frame (approximately)
            # This helps catch fast-moving collisions
            prev_bottom = player_rect.bottom - player.velocity.y * FIXED_DT
            
            # Check if player crossed through the platform this frame
            # Player was above platform top last frame, and is now at or below it
            if (prev_bottom <= platform_rect.top and
                player_rect.bottom >= platform_rect.top):
                return platform
        
        return None
    
    def resolve_platform_collision(self, player, platform):
        """
        Place player on top of platform and reset vertical velocity.
        
        Args:
            player: Player object
            platform: Platform object player landed on
        """
        platform_rect = platform.get_rect()
        
        # Place player exactly on platform
        player.position.y = platform_rect.top - player.height
        player.velocity.y = 0
        
        # Update player state
        player.on_ground = True
        player.current_platform = platform
    
    def check_water_collision(self, player, water_level):
        """
        Check if player has fallen into water.
        
        Args:
            player: Player object
            water_level: Y coordinate of water surface
        
        Returns:
            True if player is in water
        """
        return player.position.y + player.height >= water_level
    
    def check_point_in_rect(self, px, py, rect):
        """
        Check if point is inside rectangle.
        
        Args:
            px, py: Point coordinates
            rect: pygame.Rect object
        
        Returns:
            True if point is inside rectangle
        """
        return rect.collidepoint(px, py)
    
    def get_collision_rect(self, x, y, width, height):
        """
        Create a pygame.Rect for collision detection.
        
        Args:
            x, y: Top-left position
            width, height: Rectangle dimensions
        
        Returns:
            pygame.Rect object
        """
        import pygame
        return pygame.Rect(x, y, width, height)