"""
Particle effects system for visual feedback.
Handles dust, splash, helicopter trail, and other particle effects.
"""

import pygame
import random
import math
from typing import List, Tuple
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
    """Base particle class."""
    
    def __init__(
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
        
    def update(self, dt: float) -> bool:
        """Update particle. Returns False if particle should be removed."""
        self.lifetime -= dt
        if self.lifetime <= 0:
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
        if self.lifetime <= 0:
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
    """Manages all particle effects in the game."""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.helicopter_timer = 0.0
        
    def update(self, dt: float):
        """Update all particles and remove dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Limit particle count
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:]
        
        # Update helicopter timer
        if self.helicopter_timer > 0:
            self.helicopter_timer -= dt
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)
    
    def emit_jump_dust(self, x: float, y: float, direction: int = 1):
        """Emit dust particles when jumping."""
        for _ in range(JUMP_PARTICLE_COUNT):
            # Random spread
            angle = random.uniform(-math.pi / 4, math.pi / 4) - math.pi / 2
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed * direction
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(2, 4)
            
            # Create particle
            particle = Particle(
                x + random.uniform(-10, 10),
                y,
                vx,
                vy,
                PARTICLE_DUST,
                size,
                lifetime=random.uniform(0.3, 0.6),
                gravity_scale=0.5,
            )
            self.particles.append(particle)
    
    def emit_landing_impact(self, x: float, y: float, intensity: float = 1.0):
        """Emit impact particles when landing on platform."""
        count = int(LANDING_PARTICLE_COUNT * intensity)
        for _ in range(count):
            # Spread outward from landing point
            angle = random.uniform(-math.pi / 3, -2 * math.pi / 3)
            speed = random.uniform(100, 250) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(2, 5) * intensity
            
            # Create particle
            particle = Particle(
                x + random.uniform(-15, 15),
                y,
                vx,
                vy,
                PARTICLE_DUST,
                size,
                lifetime=random.uniform(0.4, 0.8),
                gravity_scale=0.8,
            )
            self.particles.append(particle)
    
    def emit_helicopter_trail(self, x: float, y: float, dt: float):
        """Emit continuous trail particles during helicopter mode."""
        self.helicopter_timer += dt
        
        if self.helicopter_timer >= HELICOPTER_PARTICLE_INTERVAL:
            self.helicopter_timer = 0.0
            
            # Create upward-moving particles
            for _ in range(2):
                # Random spread around player
                offset_x = random.uniform(-8, 8)
                offset_y = random.uniform(-5, 5)
                
                # Upward velocity with slight spread
                vx = random.uniform(-30, 30)
                vy = random.uniform(-80, -40)
                
                # Random size
                size = random.uniform(2, 4)
                
                # Create particle
                particle = Particle(
                    x + offset_x,
                    y + offset_y,
                    vx,
                    vy,
                    PARTICLE_HELICOPTER,
                    size,
                    lifetime=random.uniform(0.3, 0.5),
                    gravity_scale=0.0,  # No gravity for helicopter particles
                )
                self.particles.append(particle)
    
    def emit_double_jump_boost(self, x: float, y: float, direction: int = 1):
        """Emit speed boost trail particles during double jump."""
        for _ in range(8):
            # Backward trail effect
            angle = random.uniform(-math.pi / 6, math.pi / 6) + math.pi
            speed = random.uniform(100, 200)
            vx = math.cos(angle) * speed * direction
            vy = random.uniform(-50, 50)
            
            # Random size
            size = random.uniform(3, 6)
            
            # Create particle with bright color
            particle = Particle(
                x + random.uniform(-5, 5),
                y + random.uniform(-10, 10),
                vx,
                vy,
                (255, 200, 100),  # Bright yellow-orange for boost
                size,
                lifetime=random.uniform(0.2, 0.4),
                gravity_scale=0.0,
            )
            self.particles.append(particle)
    
    def emit_water_splash(self, x: float, y: float):
        """Emit splash particles when player hits water."""
        for _ in range(20):
            # Spread outward and upward
            angle = random.uniform(-2 * math.pi / 3, -math.pi / 3)
            speed = random.uniform(150, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(3, 7)
            
            # Create particle
            particle = Particle(
                x + random.uniform(-20, 20),
                y,
                vx,
                vy,
                PARTICLE_SPLASH,
                size,
                lifetime=random.uniform(0.5, 1.0),
                gravity_scale=1.2,
            )
            self.particles.append(particle)
    
    def emit_platform_crumble(self, x: float, y: float, width: float):
        """Emit particles when platform crumbles."""
        for _ in range(15):
            # Random position across platform
            px = x + random.uniform(0, width)
            
            # Random velocity
            vx = random.uniform(-100, 100)
            vy = random.uniform(-200, -50)
            
            # Random size
            size = random.uniform(2, 5)
            
            # Create particle with platform color
            particle = Particle(
                px,
                y,
                vx,
                vy,
                (231, 76, 60),  # Red for crumbling
                size,
                lifetime=random.uniform(0.6, 1.2),
                gravity_scale=1.0,
            )
            self.particles.append(particle)
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
        self.helicopter_timer = 0.0