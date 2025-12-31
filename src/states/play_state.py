"""
Main gameplay state.
"""
import pygame
from src.states.base_state import BaseState
from src.entities.player import Player
from src.systems.physics import PhysicsEngine
from src.systems.camera import Camera
from src.systems.animation import AnimationController
from src.systems.audio import AudioManager
from src.systems.save_system import SaveSystem
from src.world.platform_generator import PlatformGenerator
from src.world.difficulty_manager import DifficultyManager
from src.world.collectible_spawner import CollectibleSpawner
from src.graphics.background import Background
from src.graphics.particles import ParticleSystem
from src.utils.constants import *
from src.utils.math_utils import Vector2
from src.entities.collectible import CollectibleType


class PlayState(BaseState):
    """
    Main gameplay state with all game logic.
    """
    
    def __init__(self, game):
        super().__init__(game)
        
        # Core systems
        self.physics = PhysicsEngine()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.platform_generator = PlatformGenerator()
        self.collectible_spawner = CollectibleSpawner()
        self.difficulty_manager = DifficultyManager()
        # Get background colors from game's customization
        background_colors = game.customization.get_background_colors()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT, background_colors)
        self.audio = AudioManager()
        self.particles = ParticleSystem()
        self.save_system = game.save_system
        
        # Entities
        self.player = None
        
        # Game state
        self.score = 0
        self.game_over = False
        self.is_new_high_score = False
        self.paused = False
        self.resume_button_rect = None
        self.menu_button_rect = None
        
        # Statistics tracking
        self.stats = {
            'total_jumps': 0,
            'double_jumps': 0,
            'helicopter_uses': 0,
            'platforms_landed': 0,
            'collectibles_gathered': 0,
            'max_combo': 0,
            'distance_traveled': 0,
            'play_time': 0.0
        }
        
        # Power-up states
        self.active_powerups = {}  # {CollectibleType: time_remaining}
        self.shield_active = False
        self.magnet_active = False
        self.double_points_active = False
        self.extra_jump_active = False
        self.speed_boost_active = False
    
    def enter(self):
        """Initialize gameplay."""
        # Start with fade in
        self.game.ui_renderer.start_fade(fade_in=True)
        
        # Reset camera position
        self.camera.position.x = 0
        self.camera.position.y = 0
        self.camera.target_position.x = 0
        self.camera.target_position.y = 0
        self.camera.reset_zoom()
        
        # Reset platform generator state
        self.platform_generator.reset()
        
        # Generate initial platforms
        self.platform_generator.generate_initial_platforms()
        
        # Get the first platform
        platforms = self.platform_generator.get_platforms()
        if platforms:
            first_platform = platforms[0]
            # Place player on left edge of first platform
            player_x = first_platform.position.x + 20  # Small offset from edge
            player_y = first_platform.position.y - (PLAYER_HEIGHT * PLAYER_SCALE)
        else:
            # Fallback position
            player_x = 50
            player_y = SCREEN_HEIGHT - 300
        
        # Create player at calculated position
        self.player = Player(player_x, player_y)
        
        # Set player as grounded on first platform
        if platforms:
            self.player.on_ground = True
            self.player.current_platform = platforms[0]
            self.player.jump_count = 0
        
        # Set up player animation
        if hasattr(self.game, 'sprites') and 'player' in self.game.sprites:
            self.player.animation_controller = AnimationController(
                self.game.sprites['player']
            )
        
        # Reset systems
        self.difficulty_manager.reset()
        self.collectible_spawner.clear()
        self.score = 0
        self.game_over = False
        self.is_new_high_score = False
        
        # Reset statistics
        self.stats = {
            'total_jumps': 0,
            'double_jumps': 0,
            'helicopter_uses': 0,
            'platforms_landed': 0,
            'collectibles_gathered': 0,
            'max_combo': 0,
            'distance_traveled': 0,
            'play_time': 0.0
        }
        
        # Reset power-ups
        self.active_powerups.clear()
        self.shield_active = False
        self.magnet_active = False
        self.double_points_active = False
        self.extra_jump_active = False
        self.speed_boost_active = False
        
        # Start background music
        self.audio.play_music()
        
        print("Play state entered - Game started!")
    
    def exit(self):
        """Cleanup when leaving state."""
        # Stop background music
        self.audio.stop_music()
    
    def update(self, dt):
        """Update game logic."""
        # Update UI animations
        self.game.ui_renderer.update_fade(dt)
        self.game.ui_renderer.update_score_popups(dt)
        self.game.ui_renderer.update_combo(dt)
        
        if self.game_over or self.paused:
            return
        
        # Update statistics
        self.stats['play_time'] += dt
        self.stats['distance_traveled'] = int(self.camera.position.x)
        
        # Update difficulty
        self.difficulty_manager.update(dt)
        
        # Update background
        self.background.update(dt)
        
        # Update particles
        self.particles.update(dt)
        
        # Update power-ups
        self._update_powerups(dt)
        
        # Update collectibles
        self.collectible_spawner.update(
            dt,
            self.camera.position.x,
            self.platform_generator.get_platforms(),
            Vector2(self.player.position.x + self.player.width / 2,
                   self.player.position.y + self.player.height / 2),
            self.magnet_active
        )
        
        # Track helicopter state before update
        was_helicopter_active = self.player.helicopter_active
        was_on_ground = self.player.on_ground
        
        # Update player and handle sound events
        sound_event = self.player.update(dt, self.game.input_handler, self.physics)
        if sound_event:
            # Track statistics
            if sound_event == 'jump':
                self.stats['total_jumps'] += 1
            elif sound_event == 'double_jump':
                self.stats['double_jumps'] += 1
            elif sound_event == 'helicopter':
                self.stats['helicopter_uses'] += 1
            
            # Emit particles based on action
            player_center_x = self.player.position.x + self.player.width / 2
            player_bottom_y = self.player.position.y + self.player.height
            
            if sound_event == 'jump':
                # Emit dust particles on jump
                self.particles.emit_jump_dust(player_center_x, player_bottom_y)
            elif sound_event == 'double_jump':
                # Emit speed boost particles on double jump
                self.particles.emit_double_jump_boost(player_center_x, player_bottom_y)
            elif sound_event == 'helicopter':
                # Start looping helicopter sound
                self.audio.play_sound(sound_event, loop=True)
            
            # Play sound
            if sound_event == 'helicopter':
                self.audio.play_sound(sound_event, loop=True)
            else:
                self.audio.play_sound(sound_event)
        
        # Emit helicopter trail particles continuously while active
        if self.player.helicopter_active:
            player_center_x = self.player.position.x + self.player.width / 2
            player_center_y = self.player.position.y + self.player.height / 2
            self.particles.emit_helicopter_trail(player_center_x, player_center_y, dt)
        
        # Stop helicopter sound if it was deactivated
        if was_helicopter_active and not self.player.helicopter_active:
            self.audio.stop_sound('helicopter')
        
        # Check platform collision (filter out invisible disappearing platforms)
        from src.entities.platform import PlatformType
        platforms = self.platform_generator.get_platforms()
        visible_platforms = [p for p in platforms
                           if p.platform_type != PlatformType.DISAPPEARING or p.is_visible]
        collision_platform = self.physics.check_platform_collision(
            self.player, visible_platforms
        )
        
        if collision_platform and not self.player.on_ground:
            # Handle special platform effects BEFORE physics resolution
            from src.entities.platform import PlatformType
            
            # Store if this is a bouncy/spring platform
            is_bouncy = collision_platform.platform_type == PlatformType.BOUNCY
            is_spring = collision_platform.platform_type == PlatformType.SPRING
            
            # Player landed on platform
            self.physics.resolve_platform_collision(self.player, collision_platform)
            
            # Normal landing - reset jump abilities
            sound_event = self.player.land_on_platform(collision_platform)
            collision_platform.on_player_land()
            
            # Apply bounce/spring effects AFTER physics resolution
            if is_bouncy:
                # Bouncy platform - launch player higher
                self.player.velocity.y = JUMP_VELOCITY * collision_platform.bounce_multiplier
                self.player.on_ground = False  # Make sure player leaves the platform
                # Set jump state: bouncy pad counts as first jump
                self.player.jump_count = 1
                self.player.can_helicopter = False  # Must double jump first
                self.audio.play_sound('jump')
                # Extra particles for bounce
                self.particles.emit_jump_dust(
                    self.player.position.x + self.player.width / 2,
                    self.player.position.y + self.player.height
                )
            
            elif is_spring:
                # Spring platform - auto-jump with extra force
                self.player.velocity.y = JUMP_VELOCITY * collision_platform.spring_force
                self.player.on_ground = False  # Make sure player leaves the platform
                # Set jump state: spring pad counts as first jump
                self.player.jump_count = 1
                self.player.can_helicopter = False  # Must double jump first
                self.audio.play_sound('double_jump')  # Higher pitch sound
                # Extra particles for spring
                self.particles.emit_double_jump_boost(
                    self.player.position.x + self.player.width / 2,
                    self.player.position.y + self.player.height
                )
            
            # Emit landing particles
            fall_speed = abs(self.player.velocity.y)
            intensity = min(fall_speed / 500.0, 2.0)  # Scale with fall speed
            self.particles.emit_landing_impact(
                self.player.position.x + self.player.width / 2,
                self.player.position.y + self.player.height,
                intensity
            )
            
            # Stop helicopter sound if it was playing
            if self.player.helicopter_active or was_helicopter_active:
                self.audio.stop_sound('helicopter')
            
            # Play landing sound (unless bouncy/spring already played sound)
            if sound_event and collision_platform.platform_type not in [PlatformType.BOUNCY, PlatformType.SPRING]:
                self.audio.play_sound(sound_event)
            
            # Track statistics
            self.stats['platforms_landed'] += 1
            
            # Update combo
            self.game.ui_renderer.add_combo()
            combo_multiplier = self.game.ui_renderer.get_combo_multiplier()
            
            # Track max combo
            if self.game.ui_renderer.combo_count > self.stats['max_combo']:
                self.stats['max_combo'] = self.game.ui_renderer.combo_count
            
            # Update score with combo multiplier and double points
            score_gain = int(SCORE_PER_PLATFORM * combo_multiplier)
            if self.double_points_active:
                score_gain *= 2
            self.score += score_gain
            
            # Add score popup
            self.game.ui_renderer.add_score_popup(
                self.player.position.x + self.player.width / 2,
                self.player.position.y,
                score_gain,
                combo_multiplier
            )
            
            # Screen shake on landing (intensity based on fall distance)
            fall_distance = self.camera.get_fall_distance()
            self.camera.apply_shake(
                SHAKE_LANDING_AMOUNT,
                SHAKE_LANDING_DURATION,
                fall_distance=fall_distance
            )
            self.camera.reset_fall_distance()
        
        # Keep player on current platform if they're on it
        if self.player.on_ground and self.player.current_platform:
            player_rect = self.player.get_collision_rect()
            platform_rect = self.player.current_platform.get_rect()
            
            # Check if player is still above the platform horizontally
            if (player_rect.right > platform_rect.left and
                player_rect.left < platform_rect.right):
                # Keep player on platform
                self.player.position.y = platform_rect.top - self.player.height
                self.player.velocity.y = 0
                
                # Apply special platform effects while standing on them
                from src.entities.platform import PlatformType
                
                if self.player.current_platform.platform_type == PlatformType.ICE:
                    # Ice platform - reduce friction (player slides more)
                    # This is handled by reducing the deceleration when not moving
                    # The player will maintain more momentum
                    pass  # Ice effect is passive, handled in player movement
                
                elif self.player.current_platform.platform_type == PlatformType.CONVEYOR:
                    # Conveyor platform - move player in direction
                    conveyor_push = self.player.current_platform.conveyor_speed * self.player.current_platform.conveyor_direction * dt
                    self.player.position.x += conveyor_push
            else:
                # Player walked off platform edge
                self.player.on_ground = False
                self.player.current_platform = None
        
        # Check collectible collision
        player_rect = self.player.get_collision_rect()
        collected = self.collectible_spawner.check_collision(player_rect)
        
        for collectible in collected:
            self.stats['collectibles_gathered'] += 1
            self._handle_collectible(collectible)
        
        # Check water collision (death)
        if self.physics.check_water_collision(self.player, WATER_LEVEL):
            # Check if shield is active
            if self.shield_active:
                # Shield saves the player - teleport back up
                self.shield_active = False
                self.player.position.y = SCREEN_HEIGHT - 400
                self.player.velocity.y = JUMP_VELOCITY  # Give them a jump
                
                # Set jump state: shield rescue counts as first jump
                self.player.on_ground = False
                self.player.current_platform = None
                self.player.jump_count = 1  # Count as first jump used, can still double jump
                self.player.can_helicopter = False  # Must double jump first
                
                # Visual feedback
                self.game.ui_renderer.add_score_popup(
                    self.player.position.x + self.player.width / 2,
                    self.player.position.y,
                    "Shield Used!",
                    1.0,
                    is_text=True
                )
                
                # Play sound
                self.audio.play_sound('helicopter')
                
                # Emit particles
                self.particles.emit_double_jump_boost(
                    self.player.position.x + self.player.width / 2,
                    self.player.position.y + self.player.height
                )
            else:
                # Emit water splash particles
                self.particles.emit_water_splash(
                    self.player.position.x + self.player.width / 2,
                    WATER_LEVEL
                )
                
                # Stop helicopter sound if playing
                self.audio.stop_sound('helicopter')
                
                sound_event = self.player.die()
                if sound_event:
                    self.audio.play_sound(sound_event)
                self.game_over = True
                
                # Enhanced death shake with zoom out and fall distance
                fall_distance = self.camera.get_fall_distance()
                self.camera.apply_shake(
                    SHAKE_DEATH_AMOUNT,
                    SHAKE_DEATH_DURATION,
                    zoom_out=True,
                    fall_distance=fall_distance
                )
                self.camera.reset_fall_distance()
                
                # Reset combo on death
                self.game.ui_renderer.combo_count = 0
                self.game.ui_renderer.combo_timer = 0.0
                
                # Check and save high score
                self._handle_game_over()
                
                print(f"Game Over! Final Score: {self.score}")
        
        # Update camera
        self.camera.update(dt, self.player)
        
        # Update platform generation
        self.platform_generator.update(
            self.camera.position.x,
            self.difficulty_manager.get_difficulty_level(),
            self.score
        )
    
    def _update_powerups(self, dt):
        """Update active power-up timers."""
        expired = []
        
        for powerup_type, time_remaining in self.active_powerups.items():
            time_remaining -= dt
            
            if time_remaining <= 0:
                expired.append(powerup_type)
                # Deactivate power-up
                if powerup_type == CollectibleType.MAGNET:
                    self.magnet_active = False
                elif powerup_type == CollectibleType.DOUBLE_POINTS:
                    self.double_points_active = False
                elif powerup_type == CollectibleType.EXTRA_JUMP:
                    self.extra_jump_active = False
                    self.player.max_jumps = 2  # Reset to normal
                elif powerup_type == CollectibleType.SPEED_BOOST:
                    self.speed_boost_active = False
                    self.player.base_speed = PLAYER_RUN_SPEED  # Reset to normal
            else:
                self.active_powerups[powerup_type] = time_remaining
        
        # Remove expired power-ups
        for powerup_type in expired:
            del self.active_powerups[powerup_type]
    
    def _handle_collectible(self, collectible):
        """Handle collecting a collectible."""
        # Add points for coins
        if collectible.type == CollectibleType.COIN:
            points = collectible.properties['points']
            if self.double_points_active:
                points *= 2
            self.score += points
            
            # Add score popup
            self.game.ui_renderer.add_score_popup(
                collectible.position.x,
                collectible.position.y,
                points,
                1.0
            )
            
            # Play coin sound (use landing sound as placeholder)
            self.audio.play_sound('landing')
            
            # Emit particles
            self.particles.emit_jump_dust(collectible.position.x, collectible.position.y)
        
        # Handle power-ups
        else:
            duration = collectible.properties['duration']
            
            if collectible.type == CollectibleType.SPEED_BOOST:
                self.speed_boost_active = True
                self.active_powerups[CollectibleType.SPEED_BOOST] = duration
                self.player.base_speed = PLAYER_RUN_SPEED + 150  # Boost speed
                if not self.player.speed_boost_active:  # If not already boosting from double jump
                    self.player.velocity.x = self.player.base_speed
            
            elif collectible.type == CollectibleType.SHIELD:
                self.shield_active = True
                # Shield doesn't expire with time, only when used
            
            elif collectible.type == CollectibleType.MAGNET:
                self.magnet_active = True
                self.active_powerups[CollectibleType.MAGNET] = duration
            
            elif collectible.type == CollectibleType.DOUBLE_POINTS:
                self.double_points_active = True
                self.active_powerups[CollectibleType.DOUBLE_POINTS] = duration
            
            elif collectible.type == CollectibleType.EXTRA_JUMP:
                self.extra_jump_active = True
                self.active_powerups[CollectibleType.EXTRA_JUMP] = duration
                self.player.max_jumps = 3  # Enable triple jump
            
            # Show power-up message
            self.game.ui_renderer.add_score_popup(
                collectible.position.x,
                collectible.position.y - 30,
                collectible.properties['description'],
                1.0,
                is_text=True
            )
            
            # Play power-up sound (use double jump sound as placeholder)
            self.audio.play_sound('double_jump')
            
            # Emit particles
            self.particles.emit_double_jump_boost(collectible.position.x, collectible.position.y)
    
    def _handle_game_over(self):
        """Handle game over - check for high score and save."""
        # Check if this is a new high score
        self.is_new_high_score = self.save_system.is_high_score(self.score)
        
        # Save the score
        if self.is_new_high_score:
            self.save_system.add_score(self.score, stats=self.stats)
            rank = self.save_system.get_rank(self.score)
            if rank:
                print(f"New High Score! Rank #{rank}")
    
    def _render_shield_effect(self, screen):
        """Render shield visual effect around player."""
        # Get player screen position
        screen_pos = self.camera.world_to_screen(self.player.position)
        center_x = int(screen_pos.x + self.player.width / 2)
        center_y = int(screen_pos.y + self.player.height / 2)
        
        # Draw pulsing shield circle
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
        radius = int((self.player.width * 0.8) * pulse)
        
        # Draw shield with transparency
        shield_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        shield_color = (100, 200, 255, int(100 * pulse))
        pygame.draw.circle(shield_surface, shield_color, (radius, radius), radius, 3)
        screen.blit(shield_surface, (center_x - radius, center_y - radius))
    
    def _render_powerup_indicators(self, screen):
        """Render active power-up indicators."""
        y_offset = 100
        x_pos = 20
        
        # Create a small font for power-up text
        font = pygame.font.Font(None, 24)
        
        # Shield (no timer)
        if self.shield_active:
            text = font.render("SHIELD", True, (100, 200, 255))
            screen.blit(text, (x_pos, y_offset))
            y_offset += 30
        
        # Timed power-ups
        for powerup_type, time_remaining in self.active_powerups.items():
            if powerup_type == CollectibleType.SPEED_BOOST:
                color = (0, 255, 255)
                label = "SPEED"
            elif powerup_type == CollectibleType.MAGNET:
                color = (255, 0, 255)
                label = "MAGNET"
            elif powerup_type == CollectibleType.DOUBLE_POINTS:
                color = (255, 165, 0)
                label = "2X PTS"
            elif powerup_type == CollectibleType.EXTRA_JUMP:
                color = (50, 255, 50)
                label = "3X JUMP"
            else:
                continue
            
            # Render label and timer
            text = font.render(f"{label}: {int(time_remaining)}s", True, color)
            screen.blit(text, (x_pos, y_offset))
            y_offset += 30
    
    def render(self, screen):
        """Render game visuals."""
        # Render background
        self.background.render(screen, self.camera)
        
        # Render platforms
        platforms = self.platform_generator.get_platforms()
        platform_sprites = self.game.sprites.get('platforms', {})
        for platform in platforms:
            platform.render(screen, self.camera, platform_sprites)
        
        # Render collectibles
        self.collectible_spawner.render(screen, self.camera)
        
        # Render particles (behind player)
        self.particles.draw(screen, self.camera.position.x, self.camera.position.y)
        
        # Render player
        self.player.render(screen, self.camera)
        
        # Render shield effect if active
        if self.shield_active:
            self._render_shield_effect(screen)
        
        # Render speed lines during double jump boost
        if self.player.speed_boost_active:
            boost_progress = 1.0 - (self.player.speed_boost_timer / DOUBLE_JUMP_BOOST_DURATION)
            intensity = 1.0 - boost_progress  # Fade out as boost ends
            self.game.ui_renderer.render_speed_lines(
                screen,
                self.player.position.x + self.player.width / 2,
                self.player.position.y + self.player.height / 2,
                self.camera.position.x,
                self.camera.position.y,
                intensity
            )
        
        # Render score popups
        self.game.ui_renderer.render_score_popups(screen, self.camera.position.x, self.camera.position.y)
        
        # Render UI
        high_score = self.save_system.get_high_score()
        self.game.ui_renderer.render_score(screen, self.score, high_score)
        self.game.ui_renderer.render_combo(screen)
        
        # Render active power-ups
        self._render_powerup_indicators(screen)
        
        # Game over message
        if self.game_over:
            if self.is_new_high_score:
                self.game.ui_renderer.render_title(screen, "NEW HIGH SCORE!")
            else:
                self.game.ui_renderer.render_title(screen, "GAME OVER")
            
            # Show final score
            self.game.ui_renderer.render_centered_text(
                screen,
                f"Final Score: {self.score}",
                SCREEN_HEIGHT // 2 + 20,
                "medium"
            )
            
            # Show rank if high score
            if self.is_new_high_score:
                rank = self.save_system.get_rank(self.score)
                if rank:
                    self.game.ui_renderer.render_centered_text(
                        screen,
                        f"Rank: #{rank}",
                        SCREEN_HEIGHT // 2 + 60,
                        "small",
                        UI_ACCENT
                    )
            
            self.game.ui_renderer.render_centered_text(
                screen,
                "Press SPACE to restart",
                SCREEN_HEIGHT // 2 + 100,
                "small"
            )
        
        # Pause menu
        if self.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))
            
            # Pause title
            self.game.ui_renderer.render_title(screen, "PAUSED")
            
            # Get mouse position for hover detection
            mouse_pos = pygame.mouse.get_pos()
            
            # Resume button
            button_width = 200
            button_height = 50
            resume_x = SCREEN_WIDTH // 2 - button_width // 2
            resume_y = SCREEN_HEIGHT // 2 + 20
            self.resume_button_rect = pygame.Rect(resume_x, resume_y, button_width, button_height)
            is_resume_hovered = self.resume_button_rect.collidepoint(mouse_pos)
            
            self.game.ui_renderer.render_button(
                screen, "RESUME",
                resume_x, resume_y, button_width, button_height,
                is_resume_hovered
            )
            
            # Main Menu button
            menu_x = SCREEN_WIDTH // 2 - button_width // 2
            menu_y = SCREEN_HEIGHT // 2 + 90
            self.menu_button_rect = pygame.Rect(menu_x, menu_y, button_width, button_height)
            is_menu_hovered = self.menu_button_rect.collidepoint(mouse_pos)
            
            self.game.ui_renderer.render_button(
                screen, "MAIN MENU",
                menu_x, menu_y, button_width, button_height,
                is_menu_hovered
            )
        
        # Render fade overlay
        self.game.ui_renderer.render_fade(screen)
    
    def handle_event(self, event):
        """Handle events."""
        if event.type == pygame.KEYDOWN:
            # Handle pause
            if event.key == pygame.K_ESCAPE and not self.game_over:
                self.paused = not self.paused
                if self.paused:
                    # Pause music
                    self.audio.pause_music()
                else:
                    # Resume music
                    self.audio.resume_music()
            
            # Handle game over
            if self.game_over:
                if event.key == pygame.K_SPACE:
                    # Restart game
                    self.enter()
        
        # Handle pause menu button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.paused:
                if self.resume_button_rect and self.resume_button_rect.collidepoint(event.pos):
                    # Resume game
                    self.paused = False
                    self.audio.resume_music()
                elif self.menu_button_rect and self.menu_button_rect.collidepoint(event.pos):
                    # Return to main menu
                    self.paused = False
                    self.game.change_state('title')