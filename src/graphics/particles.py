"""
Particle effects system for visual feedback.
Handles dust, splash, helicopter trail, and other particle effects.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from src.utils.constants import (
    PARTICLE_LIFETIME,
    MAX_PARTICLES,
    JUMP_PARTICLE_COUNT,
    LANDING_PARTICLE_COUNT,
    HELICOPTER_PARTICLE_INTERVAL,
    PARTICLE_DUST,
    PARTICLE_HELICOPTER,
    PARTICLE_SPLASH,
    GRAVITY,
)


class Particle:
    """Base particle class with object pooling support."""
    
    def __init__(self):
        """Initialize particle with default values."""
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.color = (255, 255, 255)
        self.size = 1.0
        self.max_lifetime = PARTICLE_LIFETIME
        self.lifetime = 0.0
        self.gravity_scale = 1.0
        self.fade = True
        self.initial_size = 1.0
        self.active = False
    
    def reset(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: float,
        lifetime: float = PARTICLE_LIFETIME,
        gravity_scale: float = 1.0,
        fade: bool = True,
    ):
        """Reset particle with new values for reuse."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.gravity_scale = gravity_scale
        self.fade = fade
        self.initial_size = size
        self.active = True
        
    def update(self, dt: float) -> bool:
        """Update particle. Returns False if particle should be deactivated."""
        if not self.active:
            return False
        
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return False
        
        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity
        if self.gravity_scale > 0:
            self.vy += GRAVITY * self.gravity_scale * dt
        
        # Apply air resistance
        self.vx *= 0.98
        self.vy *= 0.98
        
        return True
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Draw the particle."""
        if not self.active or self.lifetime <= 0:
            return
        
        # Calculate screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Calculate alpha based on lifetime if fading
        if self.fade:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            # Also shrink particle as it fades
            current_size = self.initial_size * (self.lifetime / self.max_lifetime)
        else:
            alpha = 255
            current_size = self.size
        
        # Create surface with alpha
        if current_size > 0:
            particle_surface = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (int(current_size), int(current_size)),
                int(current_size)
            )
            surface.blit(particle_surface, (screen_x - int(current_size), screen_y - int(current_size)))


class ParticleSystem:
    """Manages all particle effects in the game with object pooling."""
    
    def __init__(self, pool_size: int = MAX_PARTICLES):
        """
        Initialize particle system with object pool.
        
        Args:
            pool_size: Maximum number of particles in the pool
        """
        self.pool_size = pool_size
        self.particle_pool: List[Particle] = [Particle() for _ in range(pool_size)]
        self.active_particles: List[Particle] = []
        self.helicopter_timer = 0.0
    
    def _get_particle(self) -> Optional[Particle]:
        """Get an inactive particle from the pool."""
        # First, try to find an inactive particle in the pool
        for particle in self.particle_pool:
            if not particle.active:
                return particle
        
        # If all particles are active, reuse the oldest active particle
        if self.active_particles:
            oldest = self.active_particles[0]
            oldest.active = False
            return oldest
        
        return None
        
    def update(self, dt: float):
        """Update all active particles."""
        # Update all active particles and remove inactive ones
        self.active_particles = [p for p in self.active_particles if p.update(dt)]
        
        # Update helicopter timer
        if self.helicopter_timer > 0:
            self.helicopter_timer -= dt
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Draw all active particles."""
        for particle in self.active_particles:
            particle.draw(surface, camera_x, camera_y)
    
    def emit_jump_dust(self, x: float, y: float, direction: int = 1):
        """Emit dust particles when jumping."""
        for _ in range(JUMP_PARTICLE_COUNT):
            particle = self._get_particle()
            if not particle:
                break
            
            # Random spread
            angle = random.uniform(-math.pi / 4, math.pi / 4) - math.pi / 2
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed * direction
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(2, 4)
            
            # Reset particle with new values
            particle.reset(
                x + random.uniform(-10, 10),
                y,
                vx,
                vy,
                PARTICLE_DUST,
                size,
                lifetime=random.uniform(0.3, 0.6),
                gravity_scale=0.5,
            )
            self.active_particles.append(particle)
    
    def emit_landing_impact(self, x: float, y: float, intensity: float = 1.0):
        """Emit impact particles when landing on platform."""
        count = int(LANDING_PARTICLE_COUNT * intensity)
        for _ in range(count):
            particle = self._get_particle()
            if not particle:
                break
            
            # Spread outward from landing point
            angle = random.uniform(-math.pi / 3, -2 * math.pi / 3)
            speed = random.uniform(100, 250) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(2, 5) * intensity
            
            # Reset particle with new values
            particle.reset(
                x + random.uniform(-15, 15),
                y,
                vx,
                vy,
                PARTICLE_DUST,
                size,
                lifetime=random.uniform(0.4, 0.8),
                gravity_scale=0.8,
            )
            self.active_particles.append(particle)
    
    def emit_helicopter_trail(self, x: float, y: float, dt: float):
        """Emit continuous trail particles during helicopter mode."""
        self.helicopter_timer += dt
        
        if self.helicopter_timer >= HELICOPTER_PARTICLE_INTERVAL:
            self.helicopter_timer = 0.0
            
            # Create upward-moving particles
            for _ in range(2):
                particle = self._get_particle()
                if not particle:
                    break
                
                # Random spread around player
                offset_x = random.uniform(-8, 8)
                offset_y = random.uniform(-5, 5)
                
                # Upward velocity with slight spread
                vx = random.uniform(-30, 30)
                vy = random.uniform(-80, -40)
                
                # Random size
                size = random.uniform(2, 4)
                
                # Reset particle with new values
                particle.reset(
                    x + offset_x,
                    y + offset_y,
                    vx,
                    vy,
                    PARTICLE_HELICOPTER,
                    size,
                    lifetime=random.uniform(0.3, 0.5),
                    gravity_scale=0.0,  # No gravity for helicopter particles
                )
                self.active_particles.append(particle)
    
    def emit_double_jump_boost(self, x: float, y: float, direction: int = 1):
        """Emit speed boost trail particles during double jump."""
        for _ in range(8):
            particle = self._get_particle()
            if not particle:
                break
            
            # Backward trail effect
            angle = random.uniform(-math.pi / 6, math.pi / 6) + math.pi
            speed = random.uniform(100, 200)
            vx = math.cos(angle) * speed * direction
            vy = random.uniform(-50, 50)
            
            # Random size
            size = random.uniform(3, 6)
            
            # Reset particle with bright color
            particle.reset(
                x + random.uniform(-5, 5),
                y + random.uniform(-10, 10),
                vx,
                vy,
                (255, 200, 100),  # Bright yellow-orange for boost
                size,
                lifetime=random.uniform(0.2, 0.4),
                gravity_scale=0.0,
            )
            self.active_particles.append(particle)
    
    def emit_water_splash(self, x: float, y: float):
        """Emit splash particles when player hits water."""
        for _ in range(20):
            particle = self._get_particle()
            if not particle:
                break
            
            # Spread outward and upward
            angle = random.uniform(-2 * math.pi / 3, -math.pi / 3)
            speed = random.uniform(150, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(3, 7)
            
            # Reset particle
            particle.reset(
                x + random.uniform(-20, 20),
                y,
                vx,
                vy,
                PARTICLE_SPLASH,
                size,
                lifetime=random.uniform(0.5, 1.0),
                gravity_scale=1.2,
            )
            self.active_particles.append(particle)
    
    def emit_platform_crumble(self, x: float, y: float, width: float):
        """Emit particles when platform crumbles."""
        for _ in range(15):
            particle = self._get_particle()
            if not particle:
                break
            
            # Random position across platform
            px = x + random.uniform(0, width)
            
            # Random velocity
            vx = random.uniform(-100, 100)
            vy = random.uniform(-200, -50)
            
            # Random size
            size = random.uniform(2, 5)
            
            # Reset particle with platform color
            particle.reset(
                px,
                y,
                vx,
                vy,
                (231, 76, 60),  # Red for crumbling
                size,
                lifetime=random.uniform(0.6, 1.2),
                gravity_scale=1.0,
            )
            self.active_particles.append(particle)
    
    def clear(self):
        """Clear all active particles and reset pool."""
        for particle in self.active_particles:
            particle.active = False
        self.active_particles.clear()
        self.helicopter_timer = 0.0
    
    def get_active_count(self) -> int:
        """Get the number of currently active particles."""
        return len(self.active_particles)