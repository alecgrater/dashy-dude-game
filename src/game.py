"""
Main game class with game loop and state management.
"""
import pygame
import time
from src.utils.constants import *
from src.systems.input import InputHandler
from src.systems.customization import CustomizationSystem
from src.systems.save_system import SaveSystem
from src.systems.achievements import AchievementSystem
from src.systems.audio import AudioManager
from src.graphics.sprite_generator import SpriteGenerator
from src.graphics.ui import UIRenderer
from src.states.title_state import TitleState


class Game:
    """
    Main game class that manages the game loop and states.
    """
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Create window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dashy Dude")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Performance tracking
        self.fps_font = pygame.font.Font(None, 24)
        self.frame_times = []
        self.max_frame_samples = 60
        
        # Fixed timestep
        self.dt = FIXED_DT
        
        # Input handler
        self.input_handler = InputHandler()
        
        # Initialize save system, achievements, and customization
        print("Loading save data...")
        self.save_system = SaveSystem()
        self.achievement_system = AchievementSystem()
        self.customization = CustomizationSystem()
        
        # Load settings
        self.settings = self.save_system.get_settings()
        if not self.settings:
            self.settings = {
                'show_fps': False,
                'vsync': True,
            }
        
        # Load saved customization preferences
        saved_customization = self.save_system.get_customization()
        if saved_customization:
            self.customization.from_dict(saved_customization)
        
        # Set high score for unlock checking
        self.customization.set_high_score(self.save_system.get_high_score())
        
        # Get colors from customization
        player_colors = self.customization.get_player_colors()
        platform_colors = self.customization.get_platform_colors()
        
        # Generate sprites with custom colors
        print("Generating sprites...")
        self.sprite_generator = SpriteGenerator(player_colors, platform_colors)
        self.sprites = self.sprite_generator.generate_all_sprites()
        print("Sprites generated!")
        
        # UI renderer
        self.ui_renderer = UIRenderer()
        
        # Global audio manager for menu music
        self.audio_manager = AudioManager()
        
        # Game state
        self.current_state = None
        self.play_state = None
        
        # Initialize title state
        self.title_state = TitleState(self)
        self.current_state = self.title_state
        self.current_state.enter()
    
    def run(self):
        """
        Main game loop with fixed timestep.
        """
        accumulator = 0.0
        current_time = time.time()
        
        print("Game loop starting...")
        print("Controls: SPACE to jump/double jump/helicopter glide")
        print("Hold SPACE after double jump to activate helicopter!")
        
        while self.running:
            # Calculate frame time
            new_time = time.time()
            frame_time = new_time - current_time
            current_time = new_time
            
            # Cap frame time to prevent spiral of death
            if frame_time > 0.25:
                frame_time = 0.25
            
            accumulator += frame_time
            
            # Handle events
            self.handle_events()
            
            # Update input
            self.input_handler.update()
            
            # Fixed timestep updates
            while accumulator >= self.dt:
                self.update(self.dt)
                accumulator -= self.dt
            
            # Render
            self.render()
            
            # Cap frame rate with optional VSync
            if self.settings.get('vsync', True):
                self.clock.tick(FPS)
            else:
                self.clock.tick()
            
            # Track frame time for FPS counter
            if self.settings.get('show_fps', False):
                self.frame_times.append(frame_time)
                if len(self.frame_times) > self.max_frame_samples:
                    self.frame_times.pop(0)
        
        # Cleanup
        pygame.quit()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass event to current state
            if self.current_state:
                self.current_state.handle_event(event)
    
    def update(self, dt):
        """
        Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.current_state:
            self.current_state.update(dt)
    
    def change_state(self, state_name):
        """
        Change to a different game state.
        
        Args:
            state_name: Name of the state to change to ('title', 'play', 'customize', 'achievements')
        """
        # Exit current state
        if self.current_state:
            self.current_state.exit()
        
        # Change to new state
        if state_name == 'title':
            if not hasattr(self, 'title_state'):
                self.title_state = TitleState(self)
            self.current_state = self.title_state
        elif state_name == 'play':
            from src.states.play_state import PlayState
            self.play_state = PlayState(self)
            self.current_state = self.play_state
        elif state_name == 'customize':
            from src.states.customization_state import CustomizationState
            if not hasattr(self, 'customization_state'):
                self.customization_state = CustomizationState(self)
            self.current_state = self.customization_state
        elif state_name == 'achievements':
            from src.states.achievements_state import AchievementsState
            if not hasattr(self, 'achievements_state'):
                self.achievements_state = AchievementsState(self)
            self.current_state = self.achievements_state
        elif state_name == 'settings':
            from src.states.settings_state import SettingsState
            if not hasattr(self, 'settings_state'):
                self.settings_state = SettingsState(self)
            self.current_state = self.settings_state
        
        # Enter new state
        if self.current_state:
            self.current_state.enter()
    
    def render(self):
        """Render game visuals."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current state
        if self.current_state:
            self.current_state.render(self.screen)
        
        # Render FPS counter if enabled
        if self.settings.get('show_fps', False):
            self._render_fps_counter()
        
        # Update display
        pygame.display.flip()
    
    def _render_fps_counter(self):
        """Render FPS counter with min and max values."""
        if not self.frame_times:
            return
        
        # Calculate average FPS
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Calculate min/max FPS
        if len(self.frame_times) > 1:
            max_frame_time = max(self.frame_times)
            min_frame_time = min(self.frame_times)
            min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0
            max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
        else:
            min_fps = max_fps = fps
        
        # Render FPS text on single line
        fps_text = f"FPS: {fps:.1f} (min: {min_fps:.1f}, max: {max_fps:.1f})"
        fps_surface = self.fps_font.render(fps_text, True, (255, 255, 0))
        
        # Draw background for better visibility
        bg_rect = fps_surface.get_rect(topleft=(10, 10))
        bg_rect.inflate_ip(10, 4)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        
        # Draw FPS text
        self.screen.blit(fps_surface, (10, 10))