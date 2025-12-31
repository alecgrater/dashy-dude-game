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
from src.world.platform_generator import PlatformGenerator
from src.world.difficulty_manager import DifficultyManager
from src.graphics.background import Background
from src.graphics.particles import ParticleSystem
from src.utils.constants import *
from src.utils.math_utils import Vector2


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
        self.difficulty_manager = DifficultyManager()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.audio = AudioManager()
        self.particles = ParticleSystem()
        
        # Entities
        self.player = None
        
        # Game state
        self.score = 0
        self.game_over = False
    
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
        self.score = 0
        self.game_over = False
        
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
        
        if self.game_over:
            return
        
        # Update difficulty
        self.difficulty_manager.update(dt)
        
        # Update background
        self.background.update(dt)
        
        # Update particles
        self.particles.update(dt)
        
        # Track helicopter state before update
        was_helicopter_active = self.player.helicopter_active
        was_on_ground = self.player.on_ground
        
        # Update player and handle sound events
        sound_event = self.player.update(dt, self.game.input_handler, self.physics)
        if sound_event:
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
        
        # Check platform collision
        platforms = self.platform_generator.get_platforms()
        collision_platform = self.physics.check_platform_collision(
            self.player, platforms
        )
        
        if collision_platform and not self.player.on_ground:
            # Player landed on platform
            self.physics.resolve_platform_collision(self.player, collision_platform)
            sound_event = self.player.land_on_platform(collision_platform)
            collision_platform.on_player_land()
            
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
            
            # Play landing sound
            if sound_event:
                self.audio.play_sound(sound_event)
            
            # Update combo
            self.game.ui_renderer.add_combo()
            combo_multiplier = self.game.ui_renderer.get_combo_multiplier()
            
            # Update score with combo multiplier
            score_gain = int(SCORE_PER_PLATFORM * combo_multiplier)
            self.score += score_gain
            
            # Add score popup
            self.game.ui_renderer.add_score_popup(
                self.player.position.x + self.player.width / 2,
                self.player.position.y,
                score_gain,
                combo_multiplier
            )
            
            # Screen shake on landing (more intense for higher falls)
            shake_intensity = min(SHAKE_LANDING_AMOUNT * (1 + intensity * 0.5), SHAKE_LANDING_AMOUNT * 2)
            self.camera.apply_shake(shake_intensity, SHAKE_LANDING_DURATION)
        
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
            else:
                # Player walked off platform edge
                self.player.on_ground = False
                self.player.current_platform = None
        
        # Check water collision (death)
        if self.physics.check_water_collision(self.player, WATER_LEVEL):
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
            
            # Enhanced death shake with zoom out
            self.camera.apply_shake(SHAKE_DEATH_AMOUNT, SHAKE_DEATH_DURATION, zoom_out=True)
            
            # Reset combo on death
            self.game.ui_renderer.combo_count = 0
            self.game.ui_renderer.combo_timer = 0.0
            
            print(f"Game Over! Final Score: {self.score}")
        
        # Update camera
        self.camera.update(dt, self.player)
        
        # Update platform generation
        self.platform_generator.update(
            self.camera.position.x,
            self.difficulty_manager.get_difficulty_level()
        )
    
    def render(self, screen):
        """Render game visuals."""
        # Render background
        self.background.render(screen, self.camera)
        
        # Render platforms
        platforms = self.platform_generator.get_platforms()
        platform_sprites = self.game.sprites.get('platforms', {})
        for platform in platforms:
            platform.render(screen, self.camera, platform_sprites)
        
        # Render particles (behind player)
        self.particles.draw(screen, self.camera.position.x, self.camera.position.y)
        
        # Render player
        self.player.render(screen, self.camera)
        
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
        self.game.ui_renderer.render_score(screen, self.score)
        self.game.ui_renderer.render_combo(screen)
        
        # Game over message
        if self.game_over:
            self.game.ui_renderer.render_title(screen, "GAME OVER")
            self.game.ui_renderer.render_text(screen,
                "Press SPACE to restart",
                SCREEN_WIDTH // 2 - 150,
                SCREEN_HEIGHT // 2 + 50,
                "small")
        
        # Render fade overlay
        self.game.ui_renderer.render_fade(screen)
    
    def handle_event(self, event):
        """Handle events."""
        if self.game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Restart game
                self.enter()