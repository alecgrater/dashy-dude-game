"""
UI rendering system with animated elements.
"""
import pygame
import math
import random
import colorsys
from src.utils.constants import *


class ComboIndicator:
    """Modern combo indicator UI with timer bar, progress capsules, and multiplier circle."""
    
    def __init__(self, x, y):
        """
        Initialize combo indicator.
        
        Args:
            x, y: Top-right corner position of the indicator
        """
        self.x = x
        self.y = y
        self.width = COMBO_INDICATOR_WIDTH
        self.height = COMBO_INDICATOR_HEIGHT
        
        # Animation states
        self.capsule_fill_progress = [0.0] * PLATFORMS_PER_COMBO_LEVEL
        self.capsule_pulse = [0.0] * PLATFORMS_PER_COMBO_LEVEL
        self.level_up_animation = 0.0
        self.platform_increase_animation = 0.0  # New animation for platform increase
        self.circle_pulse = 0.0
        self.timer_pulse = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.scale_pulse = 1.0  # Overall scale pulse for excitement
        
        # Epic level up effects
        self.epic_scale = 1.0  # Big scale animation
        self.epic_rotation = 0.0  # Rotation wobble
        self.epic_glow = 0.0  # Extra glow intensity
        self.epic_bounce_y = 0.0  # Bounce effect
        
        # Particle effects for level up
        self.particles = []
    
    def update(self, dt, combo_count, combo_level, combo_timer):
        """
        Update animations.
        
        Args:
            dt: Delta time
            combo_count: Current platform count
            combo_level: Current combo multiplier level
            combo_timer: Time remaining in combo
        """
        # Calculate which capsules should be filled
        platforms_in_level = combo_count % PLATFORMS_PER_COMBO_LEVEL
        if platforms_in_level == 0 and combo_count > 0:
            platforms_in_level = PLATFORMS_PER_COMBO_LEVEL
        
        # Animate capsule fills
        for i in range(PLATFORMS_PER_COMBO_LEVEL):
            target_fill = 1.0 if i < platforms_in_level else 0.0
            
            # Smooth fill animation
            if self.capsule_fill_progress[i] < target_fill:
                self.capsule_fill_progress[i] = min(1.0, self.capsule_fill_progress[i] + dt * 8.0)
            elif self.capsule_fill_progress[i] > target_fill:
                self.capsule_fill_progress[i] = max(0.0, self.capsule_fill_progress[i] - dt * 12.0)
            
            # Pulse effect for active capsule
            if i == platforms_in_level - 1 and combo_timer > 0:
                self.capsule_pulse[i] = math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5
            else:
                self.capsule_pulse[i] = 0.0
        
        # Level up animation
        if self.level_up_animation > 0:
            self.level_up_animation = max(0.0, self.level_up_animation - dt * 2.0)
        
        # Platform increase animation
        if self.platform_increase_animation > 0:
            self.platform_increase_animation = max(0.0, self.platform_increase_animation - dt * 4.0)
        
        # Epic level up effects
        if self.epic_scale > 1.0:
            # Elastic bounce back to normal
            self.epic_scale = 1.0 + (self.epic_scale - 1.0) * math.exp(-dt * 8.0)
            if self.epic_scale < 1.01:
                self.epic_scale = 1.0
        
        if abs(self.epic_rotation) > 0.1:
            # Damped oscillation
            self.epic_rotation *= math.exp(-dt * 6.0)
            self.epic_rotation += math.sin(pygame.time.get_ticks() * 0.03) * self.epic_rotation * 0.5
        
        if self.epic_glow > 0:
            self.epic_glow = max(0.0, self.epic_glow - dt * 3.0)
        
        if abs(self.epic_bounce_y) > 0.5:
            # Bounce decay
            self.epic_bounce_y *= math.exp(-dt * 5.0)
        
        # Scale pulse for excitement
        if self.level_up_animation > 0:
            # Big pulse on level up
            self.scale_pulse = 1.0 + self.level_up_animation * 0.15
        elif self.platform_increase_animation > 0:
            # Small pulse on platform increase
            self.scale_pulse = 1.0 + self.platform_increase_animation * 0.05
        else:
            self.scale_pulse = 1.0
        
        # Circle pulse based on combo level
        if combo_level > 0:
            pulse_speed = 3.0 + combo_level * 0.5
            self.circle_pulse = math.sin(pygame.time.get_ticks() * 0.001 * pulse_speed) * 0.15 + 1.0
        else:
            self.circle_pulse = 1.0
        
        # Timer urgency pulse
        if combo_timer > 0:
            if combo_timer < 0.5:
                # Urgent pulse
                self.timer_pulse = math.sin(pygame.time.get_ticks() * 0.02) * 0.3 + 1.0
                # Shake effect
                shake_intensity = (0.5 - combo_timer) * 10
                self.shake_offset_x = math.sin(pygame.time.get_ticks() * 0.05) * shake_intensity
                self.shake_offset_y = math.cos(pygame.time.get_ticks() * 0.05) * shake_intensity
            elif combo_timer < 1.0:
                # Warning pulse
                self.timer_pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.15 + 1.0
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
            else:
                self.timer_pulse = 1.0
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
        else:
            self.timer_pulse = 1.0
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
        
        # Update particles
        self.particles = [(px, py, pvx, pvy, plife - dt, pcolor)
                         for px, py, pvx, pvy, plife, pcolor in self.particles if plife > 0]
        
        # Move particles
        self.particles = [(px + pvx * dt, py + pvy * dt, pvx, pvy, plife, pcolor)
                         for px, py, pvx, pvy, plife, pcolor in self.particles]
    
    def trigger_level_up(self, new_level):
        """
        Trigger epic level up animation and effects.
        
        Args:
            new_level: The new combo level reached
        """
        self.level_up_animation = 1.0
        
        # Epic animation triggers - scale with combo level
        self.epic_scale = 1.3 + new_level * 0.05  # Bigger scale for higher levels
        self.epic_rotation = 8.0 + new_level * 2.0  # More wobble for higher levels
        self.epic_glow = 1.0 + new_level * 0.2  # More glow for higher levels
        self.epic_bounce_y = -15.0 - new_level * 3.0  # Bounce up effect
        
        # Create burst particles - more for higher levels
        color = COMBO_COLORS[min(new_level, len(COMBO_COLORS) - 1)]
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        particle_count = 30 + new_level * 10  # More particles for higher levels
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(150, 400 + new_level * 50)  # Faster for higher levels
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.5, 1.5)
            self.particles.append((center_x, center_y, vx, vy, life, color))
        
        # Add extra sparkle particles
        for _ in range(10 + new_level * 5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.8)
            sparkle_color = (255, 255, 255)  # White sparkles
            self.particles.append((center_x, center_y, vx, vy, life, sparkle_color))
    
    def trigger_platform_increase(self):
        """Trigger animation when a platform is landed on."""
        self.platform_increase_animation = 1.0
    
    def render(self, screen, combo_count, combo_level, combo_timer):
        """
        Render the combo indicator.
        
        Args:
            screen: pygame.Surface to draw on
            combo_count: Current platform count
            combo_level: Current combo multiplier level
            combo_timer: Time remaining in combo
        """
        # Apply shake offset and epic bounce
        draw_x = self.x + self.shake_offset_x
        draw_y = self.y + self.shake_offset_y + self.epic_bounce_y
        
        # Calculate scaled dimensions for epic effect
        scaled_width = int(self.width * self.epic_scale)
        scaled_height = int(self.height * self.epic_scale)
        
        # Adjust position to keep centered during scale
        scale_offset_x = (scaled_width - self.width) // 2
        scale_offset_y = (scaled_height - self.height) // 2
        
        # Background panel with modern gradient (positioned from top-left now)
        panel_rect = pygame.Rect(
            draw_x - scale_offset_x,
            draw_y - scale_offset_y,
            scaled_width,
            scaled_height
        )
        
        # Create gradient background
        for i in range(self.height):
            alpha = int(200 - (i / self.height) * 50)
            color_top = (20, 20, 30)
            color_bottom = (40, 40, 60)
            ratio = i / self.height
            color = tuple(int(color_top[j] + (color_bottom[j] - color_top[j]) * ratio) for j in range(3))
            
            line_rect = pygame.Rect(panel_rect.x, panel_rect.y + i, panel_rect.width, 1)
            pygame.draw.rect(screen, color, line_rect)
        
        # Border with glow effect (enhanced during epic animation)
        border_color = COMBO_COLORS[min(combo_level, len(COMBO_COLORS) - 1)]
        glow_layers = 3
        if self.epic_glow > 0:
            glow_layers = int(3 + self.epic_glow * 5)  # More glow layers during epic
        
        if combo_level > 0 or self.epic_glow > 0:
            # Outer glow - more intense during epic animation
            for offset in range(glow_layers, 0, -1):
                glow_rect = panel_rect.inflate(offset * 3, offset * 3)
                base_alpha = 50 if self.epic_glow <= 0 else int(50 + self.epic_glow * 100)
                glow_alpha = base_alpha // offset
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*border_color, min(255, glow_alpha)), glow_surface.get_rect(), border_radius=10)
                screen.blit(glow_surface, glow_rect.topleft)
        
        pygame.draw.rect(screen, border_color, panel_rect, 3, border_radius=10)
        
        # Cool gamer-style "COMBO" title
        self._render_combo_title(screen, panel_rect, combo_level)
        
        # Timer bar
        self._render_timer_bar(screen, panel_rect, combo_timer)
        
        # Platform progress capsules
        self._render_capsules(screen, panel_rect, combo_count, combo_level)
        
        # Multiplier circle
        self._render_multiplier_circle(screen, panel_rect, combo_level)
        
        # Render particles
        self._render_particles(screen)
        
        # Level up flash effect - more epic
        if self.level_up_animation > 0 or self.epic_glow > 0:
            flash_intensity = max(self.level_up_animation, self.epic_glow)
            flash_alpha = int(flash_intensity * 200)
            
            # Create larger flash for epic effect
            flash_scale = self.scale_pulse * (1.0 + self.epic_glow * 0.3)
            flash_surface = pygame.Surface((int(panel_rect.width * flash_scale),
                                          int(panel_rect.height * flash_scale)), pygame.SRCALPHA)
            flash_color = COMBO_COLORS[min(combo_level, len(COMBO_COLORS) - 1)]
            pygame.draw.rect(flash_surface, (*flash_color, min(255, flash_alpha)), flash_surface.get_rect(), border_radius=10)
            
            # Center the flash
            flash_x = panel_rect.x - (flash_surface.get_width() - panel_rect.width) // 2
            flash_y = panel_rect.y - (flash_surface.get_height() - panel_rect.height) // 2
            screen.blit(flash_surface, (flash_x, flash_y))
            
            # Add white flash overlay for extra impact
            if self.epic_glow > 0.5:
                white_alpha = int((self.epic_glow - 0.5) * 200)
                white_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(white_surface, (255, 255, 255, min(255, white_alpha)), white_surface.get_rect(), border_radius=10)
                screen.blit(white_surface, panel_rect.topleft)
    
    def _render_combo_title(self, screen, panel_rect, combo_level):
        """Render cool gamer-style COMBO title at the top."""
        color = COMBO_COLORS[min(combo_level, len(COMBO_COLORS) - 1)]
        
        # Create stylized "COMBO" text
        font_size = 28
        font = pygame.font.Font(None, font_size)
        text = "COMBO"
        
        text_x = panel_rect.centerx
        text_y = panel_rect.y + 18
        
        # Animated glow intensity based on combo level
        glow_intensity = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
        
        # Outer glow effect (more intense for higher combos)
        if combo_level > 0:
            glow_layers = min(combo_level + 1, 4)
            for offset in range(glow_layers, 0, -1):
                glow_alpha = int((60 // offset) * glow_intensity)
                glow_surface = font.render(text, True, color)
                glow_surface.set_alpha(glow_alpha)
                glow_rect = glow_surface.get_rect(center=(text_x, text_y))
                for dx, dy in [(offset*2, 0), (-offset*2, 0), (0, offset*2), (0, -offset*2),
                              (offset, offset), (-offset, -offset), (offset, -offset), (-offset, offset)]:
                    screen.blit(glow_surface, (glow_rect.x + dx, glow_rect.y + dy))
        
        # Black outline for readability (thick stroke effect)
        outline_color = (0, 0, 0)
        outline_surface = font.render(text, True, outline_color)
        outline_rect = outline_surface.get_rect(center=(text_x, text_y))
        for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, -2), (2, -2), (-2, 2),
                      (1, 0), (-1, 0), (0, 1), (0, -1)]:
            screen.blit(outline_surface, (outline_rect.x + dx, outline_rect.y + dy))
        
        # Main text with combo color
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(text_x, text_y))
        screen.blit(text_surface, text_rect)
        
        # Add subtle shine/highlight on top half
        if combo_level > 0:
            highlight_color = tuple(min(255, c + 80) for c in color)
            highlight_font = pygame.font.Font(None, font_size)
            highlight_surface = highlight_font.render(text, True, highlight_color)
            highlight_surface.set_alpha(int(100 * glow_intensity))
            highlight_rect = highlight_surface.get_rect(center=(text_x, text_y - 1))
            screen.blit(highlight_surface, highlight_rect)
    
    def _render_timer_bar(self, screen, panel_rect, combo_timer):
        """Render the timer bar at the top."""
        bar_x = panel_rect.x + COMBO_INDICATOR_PADDING
        bar_y = panel_rect.y + 35  # Reduced space after COMBO title
        bar_width = panel_rect.width - COMBO_INDICATOR_PADDING * 2
        bar_height = COMBO_TIMER_BAR_HEIGHT
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (30, 30, 40), bg_rect, border_radius=5)
        
        # Fill based on timer
        if combo_timer > 0:
            fill_ratio = combo_timer / COMBO_TIMEOUT
            fill_width = int(bar_width * fill_ratio)
            
            # Color based on urgency
            if combo_timer < 0.5:
                fill_color = (255, 50, 50)  # Red
            elif combo_timer < 1.0:
                fill_color = (255, 165, 0)  # Orange
            else:
                fill_color = (100, 255, 100)  # Green
            
            # Apply pulse to fill
            pulse_height = int(bar_height * self.timer_pulse)
            pulse_y_offset = (bar_height - pulse_height) // 2
            
            fill_rect = pygame.Rect(bar_x, bar_y + pulse_y_offset, fill_width, pulse_height)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=5)
            
            # Glow effect for urgent timer
            if combo_timer < 0.5:
                glow_surface = pygame.Surface((fill_width + 10, bar_height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*fill_color, 100), glow_surface.get_rect(), border_radius=5)
                screen.blit(glow_surface, (bar_x - 5, bar_y - 5))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2, border_radius=5)
        
        # Timer text
        font = pygame.font.Font(None, 20)
        timer_text = f"{combo_timer:.1f}s" if combo_timer > 0 else "0.0s"
        text_surface = font.render(timer_text, True, (255, 255, 255))
        text_x = bar_x + (bar_width - text_surface.get_width()) // 2
        text_y = bar_y + (bar_height - text_surface.get_height()) // 2
        
        # Text shadow
        shadow_surface = font.render(timer_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (text_x + 1, text_y + 1))
        screen.blit(text_surface, (text_x, text_y))
    
    def _render_capsules(self, screen, panel_rect, combo_count, combo_level):
        """Render the platform progress capsules."""
        platforms_in_level = combo_count % PLATFORMS_PER_COMBO_LEVEL
        if platforms_in_level == 0 and combo_count > 0:
            platforms_in_level = PLATFORMS_PER_COMBO_LEVEL
        
        # Calculate total width needed
        total_capsule_width = (COMBO_CAPSULE_WIDTH * PLATFORMS_PER_COMBO_LEVEL +
                              COMBO_CAPSULE_SPACING * (PLATFORMS_PER_COMBO_LEVEL - 1))
        start_x = panel_rect.centerx - total_capsule_width // 2
        start_y = panel_rect.y + 65  # Closer to timer bar
        
        current_color = COMBO_COLORS[min(combo_level, len(COMBO_COLORS) - 1)]
        next_color = COMBO_COLORS[min(combo_level + 1, len(COMBO_COLORS) - 1)]
        
        for i in range(PLATFORMS_PER_COMBO_LEVEL):
            capsule_x = start_x + i * (COMBO_CAPSULE_WIDTH + COMBO_CAPSULE_SPACING)
            capsule_y = start_y
            
            # Apply pulse to active capsule
            pulse_scale = 1.0 + self.capsule_pulse[i] * 0.2
            capsule_width = int(COMBO_CAPSULE_WIDTH * pulse_scale)
            capsule_height = int(COMBO_CAPSULE_HEIGHT * pulse_scale)
            capsule_x -= (capsule_width - COMBO_CAPSULE_WIDTH) // 2
            capsule_y -= (capsule_height - COMBO_CAPSULE_HEIGHT) // 2
            
            # Background (empty state)
            bg_rect = pygame.Rect(capsule_x, capsule_y, capsule_width, capsule_height)
            pygame.draw.rect(screen, (20, 20, 20), bg_rect, border_radius=8)
            
            # Fill progress
            if self.capsule_fill_progress[i] > 0:
                fill_height = int(capsule_height * self.capsule_fill_progress[i])
                fill_y = capsule_y + capsule_height - fill_height
                fill_rect = pygame.Rect(capsule_x, fill_y, capsule_width, fill_height)
                
                # Use next level color if at max
                fill_color = next_color if platforms_in_level == PLATFORMS_PER_COMBO_LEVEL else current_color
                pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)
                
                # Shine effect on top
                if self.capsule_fill_progress[i] > 0.9:
                    shine_surface = pygame.Surface((capsule_width, 5), pygame.SRCALPHA)
                    pygame.draw.rect(shine_surface, (255, 255, 255, 150), shine_surface.get_rect())
                    screen.blit(shine_surface, (capsule_x, fill_y))
            
            # Border
            border_color = current_color if i < platforms_in_level else (80, 80, 90)
            pygame.draw.rect(screen, border_color, bg_rect, 2, border_radius=8)
            
            # Glow for filled capsules
            if i < platforms_in_level:
                glow_surface = pygame.Surface((capsule_width + 6, capsule_height + 6), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*current_color, 80), glow_surface.get_rect(), border_radius=8)
                screen.blit(glow_surface, (capsule_x - 3, capsule_y - 3))
    
    def _render_multiplier_circle(self, screen, panel_rect, combo_level):
        """Render the multiplier circle at the bottom."""
        center_x = panel_rect.centerx
        # Calculate center position: capsules end at ~95, panel height is 200
        # Available space: 200 - 95 = 105 pixels
        # Center the circle in this space: 95 + (105 / 2) = 147.5
        capsules_bottom = 65 + COMBO_CAPSULE_HEIGHT  # ~95
        available_space = self.height - capsules_bottom
        center_y = panel_rect.y + capsules_bottom + (available_space // 2)
        
        radius = int(COMBO_CIRCLE_RADIUS * self.circle_pulse)
        color = COMBO_COLORS[min(combo_level, len(COMBO_COLORS) - 1)]
        
        # Outer glow rings
        if combo_level > 0:
            for i in range(3):
                glow_radius = radius + (i + 1) * 8
                glow_alpha = 60 - i * 15
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, glow_alpha),
                                 (glow_radius + 5, glow_radius + 5), glow_radius)
                screen.blit(glow_surface, (center_x - glow_radius - 5, center_y - glow_radius - 5))
        
        # Main circle background
        pygame.draw.circle(screen, (30, 30, 40), (center_x, center_y), radius)
        
        # Gradient fill
        for r in range(radius, 0, -2):
            alpha = int(255 * (r / radius))
            gradient_color = tuple(int(c * (r / radius)) for c in color)
            pygame.draw.circle(screen, gradient_color, (center_x, center_y), r)
        
        # Border
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 4)
        
        # Multiplier text
        multiplier = combo_level + 1
        font_size = 48 if combo_level < 3 else 56
        font = pygame.font.Font(None, font_size)
        text = f"{multiplier}x"
        text_surface = font.render(text, True, (255, 255, 255))
        text_x = center_x - text_surface.get_width() // 2
        text_y = center_y - text_surface.get_height() // 2
        
        # Text shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        screen.blit(shadow_surface, (text_x + 2, text_y + 2))
        screen.blit(text_surface, (text_x, text_y))
        
        # Rotating ring animation for high combos
        if combo_level >= 3:
            ring_radius = radius + 10
            num_dots = 8
            rotation = pygame.time.get_ticks() * 0.002
            for i in range(num_dots):
                angle = (i / num_dots) * math.pi * 2 + rotation
                dot_x = center_x + math.cos(angle) * ring_radius
                dot_y = center_y + math.sin(angle) * ring_radius
                pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), 4)
    
    def _render_particles(self, screen):
        """Render particle effects."""
        for px, py, _, _, plife, pcolor in self.particles:
            if plife <= 0:
                continue
            
            alpha = max(0, min(255, int(255 * plife)))
            size = max(1, int(4 * plife))
            
            if size > 0 and alpha > 0:
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                # Ensure all color values are valid integers in range [0, 255]
                r = max(0, min(255, int(pcolor[0])))
                g = max(0, min(255, int(pcolor[1])))
                b = max(0, min(255, int(pcolor[2])))
                color_with_alpha = (r, g, b, alpha)
                pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
                screen.blit(particle_surface, (int(px) - size, int(py) - size))


class ScorePopup:
    """Animated score popup with AAA-game-quality effects."""
    
    def __init__(self, x, y, score, combo=1, is_text=False):
        self.x = x
        self.y = y
        self.initial_y = y
        self.score = score
        self.combo = combo
        self.is_text = is_text  # If True, score is a text string
        self.lifetime = 0.0
        self.max_lifetime = 2.0 if is_text else 1.5  # Longer for better visibility
        self.velocity_y = -120 if is_text else -150  # Faster upward movement
        self.alpha = 255
        
        # Enhanced animation properties
        self.scale = 0.0  # Start from 0 for pop-in effect
        self.rotation = 0.0
        self.glow_intensity = 1.0
        self.shake_x = 0.0
        self.shake_y = 0.0
        
        # Particle-like trail effect
        self.trail_positions = []
        self.trail_max = 5
    
    def update(self, dt):
        """Update popup animation with advanced effects."""
        self.lifetime += dt
        progress = self.lifetime / self.max_lifetime
        
        # Store trail positions for motion blur effect
        if len(self.trail_positions) >= self.trail_max:
            self.trail_positions.pop(0)
        self.trail_positions.append((self.x, self.y, self.alpha * 0.3))
        
        # Movement with easing
        if self.lifetime < 0.3:
            # Quick pop-up phase with overshoot
            ease_progress = self.lifetime / 0.3
            ease_factor = 1.0 - (1.0 - ease_progress) ** 3  # Cubic ease-out
            self.y = self.initial_y + self.velocity_y * ease_factor * 0.3
        else:
            # Slower float upward
            self.y += self.velocity_y * dt * 0.5
        
        # Elastic pop-in scale animation
        if self.lifetime < 0.2:
            # Overshoot scale for impact
            t = self.lifetime / 0.2
            self.scale = 1.0 + 0.5 * math.sin(t * math.pi * 2) * (1.0 - t)
            self.scale = max(0.0, min(1.5, self.scale))
        elif self.lifetime < 0.4:
            # Settle to normal size
            t = (self.lifetime - 0.2) / 0.2
            self.scale = 1.5 - 0.5 * t
        else:
            # Slight pulse during display
            pulse = 1.0 + 0.05 * math.sin(self.lifetime * 10)
            self.scale = 1.0 * pulse
        
        # Rotation for combo/power-up text
        if self.is_text or self.combo > 1:
            self.rotation = math.sin(self.lifetime * 8) * 5  # Gentle wobble
        
        # Glow pulse effect
        self.glow_intensity = 0.5 + 0.5 * math.sin(self.lifetime * 12)
        
        # Micro shake for impact
        if self.lifetime < 0.15:
            shake_amount = (0.15 - self.lifetime) * 20
            self.shake_x = (math.sin(self.lifetime * 50) * shake_amount)
            self.shake_y = (math.cos(self.lifetime * 50) * shake_amount)
        else:
            self.shake_x = 0
            self.shake_y = 0
        
        # Fade out in last 40% of lifetime with smooth curve
        fade_start = self.max_lifetime * 0.6
        if self.lifetime > fade_start:
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            # Smooth fade curve
            fade_curve = 1.0 - fade_progress ** 2
            self.alpha = int(255 * fade_curve)
        
        return self.lifetime < self.max_lifetime
    
    def render(self, screen, font, camera_x, camera_y):
        """Render the popup with advanced visual effects."""
        screen_x = self.x - camera_x + self.shake_x
        screen_y = self.y - camera_y + self.shake_y
        
        # Determine text and colors based on type
        if self.is_text:
            # Power-up text with gradient effect
            text = str(self.score).upper()
            base_color = (0, 255, 255)  # Cyan
            glow_color = (255, 255, 0)  # Yellow glow
            font_size = 52  # Larger for power-ups
        elif self.combo > 1:
            text = f"+{self.score}"
            # Color based on combo level
            if self.combo >= 5:
                base_color = (255, 50, 255)  # Magenta for high combos
                glow_color = (255, 200, 0)  # Gold glow
            else:
                base_color = (255, 215, 0)  # Gold
                glow_color = (255, 100, 0)  # Orange glow
            font_size = 48 + min(self.combo * 2, 20)  # Larger for higher combos
        else:
            text = f"+{self.score}"
            base_color = (255, 255, 255)  # White
            glow_color = (200, 200, 255)  # Slight blue glow
            font_size = 44
        
        # Create larger font for better readability
        display_font = pygame.font.Font(None, int(font_size * self.scale))
        
        # Render glow layers for depth (multiple passes)
        glow_alpha = int(self.alpha * self.glow_intensity * 0.6)
        for glow_offset in [8, 6, 4, 2]:
            glow_surface = display_font.render(text, True, glow_color)
            glow_surface.set_alpha(glow_alpha // (glow_offset // 2))
            glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
            
            # Draw glow in all directions
            for dx, dy in [(glow_offset, 0), (-glow_offset, 0), (0, glow_offset), (0, -glow_offset),
                          (glow_offset, glow_offset), (-glow_offset, -glow_offset),
                          (glow_offset, -glow_offset), (-glow_offset, glow_offset)]:
                screen.blit(glow_surface, (glow_rect.x + dx, glow_rect.y + dy))
        
        # Render thick black outline for readability (stroke effect)
        outline_color = (0, 0, 0)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2), (3, 0), (-3, 0), (0, 3), (0, -3)]:
            outline_surface = display_font.render(text, True, outline_color)
            outline_surface.set_alpha(self.alpha)
            outline_rect = outline_surface.get_rect(center=(int(screen_x + offset[0]), int(screen_y + offset[1])))
            screen.blit(outline_surface, outline_rect)
        
        # Render main text with full alpha
        text_surface = display_font.render(text, True, base_color)
        text_surface.set_alpha(self.alpha)
        
        # Apply rotation if needed
        if abs(self.rotation) > 0.1:
            text_surface = pygame.transform.rotate(text_surface, self.rotation)
        
        # Center and draw main text
        text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(text_surface, text_rect)
        
        # Render motion trail for extra juice
        if len(self.trail_positions) > 1:
            for i, (tx, ty, trail_alpha) in enumerate(self.trail_positions[:-1]):
                trail_screen_x = tx - camera_x
                trail_screen_y = ty - camera_y
                trail_scale = self.scale * (0.5 + 0.5 * (i / len(self.trail_positions)))
                trail_font = pygame.font.Font(None, int(font_size * trail_scale))
                trail_surface = trail_font.render(text, True, base_color)
                trail_surface.set_alpha(int(trail_alpha))
                trail_rect = trail_surface.get_rect(center=(int(trail_screen_x), int(trail_screen_y)))
                screen.blit(trail_surface, trail_rect)


class UIRenderer:
    """
    Renders UI elements like score, buttons, and text with animations.
    """
    
    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.font_medium = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.font_small = pygame.font.Font(None, BUTTON_FONT_SIZE)
        
        # Animated elements
        self.score_popups = []
        self.combo_count = 0  # Number of platforms landed on in current combo
        self.combo_level = 0  # Current combo multiplier level (0-5)
        self.combo_timer = 0.0
        self.fade_alpha = 0  # For state transitions
        self.fade_direction = 0  # 0=none, 1=fade in, -1=fade out
        
        # Combo indicator (positioned at top left, offset down to avoid FPS counter)
        self.combo_indicator = ComboIndicator(
            COMBO_INDICATOR_PADDING,
            COMBO_INDICATOR_PADDING + 25  # Offset down to avoid FPS counter
        )
        self.previous_combo_level = 0  # Track level changes for animations
    
    def render_score(self, screen, score, high_score=0):
        """
        Render score display with optional high score.
        
        Args:
            screen: pygame.Surface to draw on
            score: Current score value
            high_score: High score to display (optional)
        """
        score_text = self.font_medium.render(f"Score: {score}", True, UI_TEXT)
        score_shadow = self.font_medium.render(f"Score: {score}", True, UI_TEXT_SHADOW)
        
        # Position to the right of the combo indicator, offset down to avoid FPS counter
        x_offset = COMBO_INDICATOR_PADDING + COMBO_INDICATOR_WIDTH + 20
        y_offset_base = UI_PADDING + 25  # Offset down to avoid FPS counter
        
        # Draw shadow
        screen.blit(score_shadow, (x_offset + 2, y_offset_base + 2))
        # Draw text
        screen.blit(score_text, (x_offset, y_offset_base))
        
        # Draw high score below current score if available
        if high_score > 0:
            high_score_text = self.font_small.render(f"Best: {high_score}", True, UI_ACCENT)
            high_score_shadow = self.font_small.render(f"Best: {high_score}", True, UI_TEXT_SHADOW)
            
            y_offset = y_offset_base + 40
            screen.blit(high_score_shadow, (x_offset + 2, y_offset + 2))
            screen.blit(high_score_text, (x_offset, y_offset))
    
    def render_title(self, screen, title):
        """
        Render large title text.
        
        Args:
            screen: pygame.Surface to draw on
            title: Title string
        """
        text = self.font_large.render(title, True, UI_TEXT)
        shadow = self.font_large.render(title, True, UI_TEXT_SHADOW)
        
        # Center on screen
        x = (screen.get_width() - text.get_width()) // 2
        y = screen.get_height() // 4
        
        screen.blit(shadow, (x + 3, y + 3))
        screen.blit(text, (x, y))
    
    def render_button(self, screen, text, x, y, width, height, hovered=False):
        """
        Render a button.
        
        Args:
            screen: pygame.Surface to draw on
            text: Button text
            x, y: Button position
            width, height: Button dimensions
            hovered: Whether mouse is hovering over button
        
        Returns:
            pygame.Rect of button for collision detection
        """
        button_rect = pygame.Rect(x, y, width, height)
        
        # Button color
        color = UI_ACCENT if hovered else UI_PRIMARY
        
        # Draw button
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, UI_TEXT, button_rect, 3, border_radius=10)
        
        # Draw text
        text_surface = self.font_small.render(text, True, UI_TEXT)
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        return button_rect
    
    def render_text(self, screen, text, x, y, font_size="medium", color=UI_TEXT):
        """
        Render text at position.
        
        Args:
            screen: pygame.Surface to draw on
            text: Text string
            x, y: Position
            font_size: "large", "medium", or "small"
            color: Text color
        """
        if font_size == "large":
            font = self.font_large
        elif font_size == "small":
            font = self.font_small
        else:
            font = self.font_medium
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
    
    def render_centered_text(self, screen, text, y, font_size="medium", color=UI_TEXT, shadow=True):
        """
        Render text centered horizontally on screen.
        
        Args:
            screen: pygame.Surface to draw on
            text: Text string
            y: Vertical position
            font_size: "large", "medium", or "small"
            color: Text color
            shadow: Whether to render shadow
        
        Returns:
            pygame.Rect of rendered text
        """
        if font_size == "large":
            font = self.font_large
        elif font_size == "small":
            font = self.font_small
        else:
            font = self.font_medium
        
        text_surface = font.render(text, True, color)
        x = (screen.get_width() - text_surface.get_width()) // 2
        
        # Draw shadow if requested
        if shadow:
            shadow_surface = font.render(text, True, UI_TEXT_SHADOW)
            screen.blit(shadow_surface, (x + 2, y + 2))
        
        # Draw text
        screen.blit(text_surface, (x, y))
        
        return pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
    
    def render_animated_title(self, screen, text, y, scale=1.0, color=UI_ACCENT):
        """
        Render large animated title with effects.
        
        Args:
            screen: pygame.Surface to draw on
            text: Title text
            y: Vertical position
            scale: Scale factor for animation
            color: Text color
        """
        font_size = int(TITLE_FONT_SIZE * scale)
        font = pygame.font.Font(None, font_size)
        
        # Render shadow
        shadow = font.render(text, True, UI_TEXT_SHADOW)
        shadow_rect = shadow.get_rect(center=(screen.get_width() // 2 + 4, y + 4))
        screen.blit(shadow, shadow_rect)
        
        # Render main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y))
        screen.blit(text_surface, text_rect)
    
    def add_score_popup(self, x, y, score, combo=1, is_text=False):
        """
        Add an animated score popup.
        
        Args:
            x, y: World position for popup
            score: Score value to display (or text string if is_text=True)
            combo: Combo multiplier
            is_text: If True, score is treated as a text message
        """
        self.score_popups.append(ScorePopup(x, y, score, combo, is_text))
    
    def update_score_popups(self, dt):
        """Update all score popups."""
        self.score_popups = [popup for popup in self.score_popups if popup.update(dt)]
    
    def render_score_popups(self, screen, camera_x, camera_y):
        """Render all score popups."""
        for popup in self.score_popups:
            popup.render(screen, self.font_small, camera_x, camera_y)
    
    def update_combo(self, dt, audio_manager=None):
        """Update combo timer and combo indicator."""
        old_combo_level = self.combo_level
        
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Combo timed out - only play sound if we had an active multiplier (level > 0)
                # This means at least 5 platforms were landed on to reach 2x multiplier
                if old_combo_level > 0 and audio_manager:
                    audio_manager.play_sound('combo_timeout')
                self.combo_count = 0
                self.combo_level = 0
                self.previous_combo_level = 0
        
        # Update combo indicator animations
        self.combo_indicator.update(dt, self.combo_count, self.combo_level, self.combo_timer)
    
    def add_combo(self):
        """Increment combo counter and update level based on platforms per level."""
        old_level = self.combo_level
        self.combo_count += 1
        self.combo_timer = COMBO_TIMEOUT
        
        # Calculate combo level: every PLATFORMS_PER_COMBO_LEVEL platforms = 1 level
        # Level 0 = no combo (0-4 platforms)
        # Level 1 = 2x (5-9 platforms)
        # Level 2 = 3x (10-14 platforms)
        # etc., up to MAX_COMBO_LEVEL
        self.combo_level = min(self.combo_count // PLATFORMS_PER_COMBO_LEVEL, MAX_COMBO_LEVEL)
        
        # Trigger level up animation if level increased
        if self.combo_level > old_level:
            self.combo_indicator.trigger_level_up(self.combo_level)
            self.previous_combo_level = self.combo_level
        else:
            # Trigger platform increase animation
            self.combo_indicator.trigger_platform_increase()
    
    def get_combo_multiplier(self):
        """Get current combo multiplier based on combo level."""
        # Level 0 = 1x, Level 1 = 2x, Level 2 = 3x, etc.
        return self.combo_level + 1
    
    def render_combo(self, screen):
        """Render the modern combo indicator UI."""
        # Always render the combo indicator (it shows even when combo is 0)
        self.combo_indicator.render(screen, self.combo_count, self.combo_level, self.combo_timer)
        
        # Keep old text-based combo display for reference (can be removed later)
        if False and self.combo_count > 0:  # Disabled for now
            # Pulse effect based on timer (faster pulse for higher combos)
            pulse_speed = min(10 + self.combo_level * 2, 20)
            pulse = 1.0 + 0.1 * math.sin(self.combo_timer * pulse_speed)
            
            # Color based on combo level
            if self.combo_level >= 5:
                # Rainbow effect for max combo
                hue = (self.combo_timer * 100) % 360
                color = self._hsv_to_rgb(hue, 1.0, 1.0)
            elif self.combo_level >= 4:
                color = (255, 0, 255)  # Magenta for 5x
            elif self.combo_level >= 3:
                color = (255, 215, 0)  # Gold for 4x
            elif self.combo_level >= 2:
                color = (255, 165, 0)  # Orange for 3x
            elif self.combo_level >= 1:
                color = (100, 255, 100)  # Green for 2x
            else:
                color = (255, 255, 255)  # White for building combo
            
            multiplier = self.get_combo_multiplier()
            
            # Calculate platforms in current level
            platforms_in_level = self.combo_count % PLATFORMS_PER_COMBO_LEVEL
            if platforms_in_level == 0 and self.combo_count > 0:
                platforms_in_level = PLATFORMS_PER_COMBO_LEVEL
            
            # Show different text based on whether combo is active
            if self.combo_level > 0:
                # Active combo - show multiplier and progress to next level
                if self.combo_level < MAX_COMBO_LEVEL:
                    text = f"COMBO x{multiplier} ({platforms_in_level}/{PLATFORMS_PER_COMBO_LEVEL})"
                else:
                    # Max combo reached
                    text = f"MAX COMBO x{multiplier}!"
            else:
                # Building first combo
                text = f"Building Combo... ({platforms_in_level}/{PLATFORMS_PER_COMBO_LEVEL})"
            
            # Larger font for higher combos
            base_size = BUTTON_FONT_SIZE
            if self.combo_level >= 3:
                base_size = int(BUTTON_FONT_SIZE * 1.3)
            
            font_size = int(base_size * pulse)
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(text, True, color)
            
            # Position at top center
            x = (screen.get_width() - text_surface.get_width()) // 2
            y = UI_PADDING + 60
            
            # Shadow for combo text
            shadow = font.render(text, True, UI_TEXT_SHADOW)
            screen.blit(shadow, (x + 2, y + 2))
            screen.blit(text_surface, (x, y))
            
            # Render timer text with bigger font
            timer_text = f"{self.combo_timer:.1f}s"
            timer_font_size = int(base_size * 1.2 * pulse)  # Bigger timer text
            timer_font = pygame.font.Font(None, timer_font_size)
            
            # Timer color changes based on urgency
            if self.combo_timer < 0.5:
                timer_color = (255, 50, 50)  # Red - urgent!
            elif self.combo_timer < 1.0:
                timer_color = (255, 165, 0)  # Orange - warning
            else:
                timer_color = (100, 255, 100)  # Green - safe
            
            timer_surface = timer_font.render(timer_text, True, timer_color)
            
            # Position timer to the right of combo text with some spacing
            timer_x = x + text_surface.get_width() + 20
            timer_y = y + (text_surface.get_height() - timer_surface.get_height()) // 2
            
            # Calculate bubble dimensions to fit only the timer
            bubble_padding = 20
            bubble_width = timer_surface.get_width() + bubble_padding * 2
            bubble_height = timer_surface.get_height() + bubble_padding * 2
            bubble_x = timer_x - bubble_padding
            bubble_y = timer_y - bubble_padding
            
            # Draw comic-style speech bubble background behind timer only
            self._draw_comic_bubble(screen, bubble_x, bubble_y, bubble_width, bubble_height, pulse)
            
            # Shadow for timer
            timer_shadow = timer_font.render(timer_text, True, (0, 0, 0))
            screen.blit(timer_shadow, (timer_x + 2, timer_y + 2))
            screen.blit(timer_surface, (timer_x, timer_y))
    
    def _draw_comic_bubble(self, screen, x, y, width, height, pulse=1.0):
        """Draw a comic-style speech bubble background."""
        # Main bubble colors
        bubble_fill = (220, 50, 50)  # Red background
        bubble_outline = (0, 0, 0)  # Black outline
        
        # Create a surface for the bubble with alpha
        bubble_surface = pygame.Surface((int(width + 80), int(height + 80)), pygame.SRCALPHA)
        
        # Center point for drawing on the surface
        center_x = 40
        center_y = 40
        
        # Draw simple circle - slightly bigger
        radius = min(width, height) * 0.55 * pulse
        circle_center = (int(center_x + width / 2), int(center_y + height / 2))
        
        # Draw filled circle
        pygame.draw.circle(bubble_surface, bubble_fill, circle_center, int(radius))
        
        # Draw thick black outline
        pygame.draw.circle(bubble_surface, bubble_outline, circle_center, int(radius), 4)
        
        # Add halftone dots pattern for comic effect
        dot_spacing = 10
        dot_radius = 2
        for dx in range(0, int(width), dot_spacing):
            for dy in range(0, int(height), dot_spacing):
                dot_x = center_x + width * 0.25 + dx
                dot_y = center_y + height * 0.25 + dy
                # Check if point is inside the bubble
                dist_to_center = math.sqrt((dot_x - circle_center[0])**2 + (dot_y - circle_center[1])**2)
                if dist_to_center < radius * 0.7:
                    pygame.draw.circle(bubble_surface, (180, 30, 30), (int(dot_x), int(dot_y)), dot_radius)
        
        # Blit the bubble surface to the screen
        screen.blit(bubble_surface, (x - 40, y - 40))
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color to RGB tuple."""
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def render_speed_lines(self, screen, player_x, player_y, camera_x, camera_y, intensity=1.0):
        """
        Render speed lines effect during boost.
        
        Args:
            screen: pygame.Surface to draw on
            player_x, player_y: Player world position
            camera_x, camera_y: Camera position
            intensity: Line intensity (0-1)
        """
        if intensity <= 0:
            return
        
        # Convert to screen space
        screen_x = player_x - camera_x
        screen_y = player_y - camera_y
        
        # Draw horizontal speed lines
        num_lines = int(8 * intensity)
        for i in range(num_lines):
            # Random offset from player
            offset_y = (i - num_lines / 2) * 20
            line_y = screen_y + offset_y
            
            # Line length based on intensity
            line_length = int(100 * intensity)
            line_start_x = screen_x - 50
            line_end_x = line_start_x - line_length
            
            # Alpha based on intensity
            alpha = int(150 * intensity)
            color = (255, 255, 255, alpha)
            
            # Create surface with alpha
            line_surface = pygame.Surface((line_length, 3), pygame.SRCALPHA)
            pygame.draw.line(line_surface, color, (0, 1), (line_length, 1), 3)
            screen.blit(line_surface, (line_end_x, line_y))
    
    def start_fade(self, fade_in=True):
        """Start a fade transition."""
        if fade_in:
            self.fade_alpha = 255
            self.fade_direction = -1
        else:
            self.fade_alpha = 0
            self.fade_direction = 1
    
    def update_fade(self, dt):
        """Update fade transition."""
        if self.fade_direction != 0:
            fade_speed = 500  # Alpha units per second
            self.fade_alpha += self.fade_direction * fade_speed * dt
            
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_direction = 0
            elif self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_direction = 0
    
    def render_fade(self, screen):
        """Render fade overlay."""
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(fade_surface, (0, 0))
    
    def is_fading(self):
        """Check if currently fading."""
        return self.fade_direction != 0