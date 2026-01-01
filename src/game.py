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
from src.graphics.sprite_generator import SpriteGenerator
from src.graphics.ui import UIRenderer
from src.states.title_state import TitleState
from src.states.play_state import PlayState


class Game:
    """
    Main game class that manages the game loop and states.
    """
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Create window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Endless Lake Clone")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fixed timestep
        self.dt = FIXED_DT
        
        # Input handler
        self.input_handler = InputHandler()
        
        # Initialize save system, achievements, and customization
        print("Loading save data...")
        self.save_system = SaveSystem()
        self.achievement_system = AchievementSystem()
        self.customization = CustomizationSystem()
        
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
            
            # Cap frame rate
            self.clock.tick(FPS)
        
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
        
        # Update display
        pygame.display.flip()