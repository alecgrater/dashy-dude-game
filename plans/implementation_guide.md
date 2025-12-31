# Implementation Guide - Endless Lake Clone

## Phase-by-Phase Implementation Details

This guide provides specific implementation details for each system, including code patterns, algorithms, and technical specifications.

---

## Phase 1: Core Foundation

### 1.1 Project Setup

**Dependencies to Add**:
```toml
[project]
dependencies = [
    "pygame-ce>=2.4.0",  # Modern pygame fork
    "numpy>=1.26.0",     # For audio generation
]
```

**Directory Structure Creation**:
```bash
src/
├── __init__.py
├── game.py
├── states/
├── entities/
├── systems/
├── graphics/
├── utils/
└── world/
```

### 1.2 Game Loop Architecture

**Main Game Class** (`src/game.py`):
```python
class Game:
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720
        self.fps = 60
        self.dt = 1.0 / self.fps
        
    def run(self):
        # Fixed timestep game loop
        accumulator = 0.0
        current_time = time.time()
        
        while running:
            new_time = time.time()
            frame_time = new_time - current_time
            current_time = new_time
            
            # Cap frame time to prevent spiral of death
            if frame_time > 0.25:
                frame_time = 0.25
                
            accumulator += frame_time
            
            # Handle events
            self.handle_events()
            
            # Fixed timestep updates
            while accumulator >= self.dt:
                self.update(self.dt)
                accumulator -= self.dt
                
            # Render with interpolation
            alpha = accumulator / self.dt
            self.render(alpha)
```

**State Manager Pattern**:
```python
class StateManager:
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.transition_alpha = 0.0
        
    def change_state(self, state_name, transition_time=0.3):
        # Fade out current state
        # Fade in new state
        # Call exit() on old, enter() on new
```

### 1.3 Constants and Configuration

**Constants File** (`src/utils/constants.py`):
```python
# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Physics
GRAVITY = 2000.0  # pixels/second²
MAX_FALL_SPEED = 1000.0
TERMINAL_VELOCITY = 1200.0

# Player
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_SCALE = 2
PLAYER_RUN_SPEED = 400.0
JUMP_VELOCITY = -600.0
DOUBLE_JUMP_VELOCITY = -550.0
HELICOPTER_FALL_SPEED = 100.0
HELICOPTER_DURATION = 1.5

# Advanced Mechanics
COYOTE_TIME = 0.1  # seconds
JUMP_BUFFER_TIME = 0.15  # seconds
VARIABLE_JUMP_MULTIPLIER = 0.5

# Platform
PLATFORM_HEIGHT = 16
PLATFORM_SCALE = 2
MIN_PLATFORM_WIDTH = 80
MAX_PLATFORM_WIDTH = 200
PLATFORM_SPAWN_DISTANCE = 1500

# Difficulty
BASE_GAME_SPEED = 300.0
MAX_GAME_SPEED = 600.0
SPEED_INCREASE_INTERVAL = 10.0
SPEED_INCREASE_AMOUNT = 20.0

# Camera
CAMERA_SMOOTHING = 0.1
CAMERA_PLAYER_OFFSET_X = 0.3  # Player at 30% of screen width
CAMERA_LOOK_AHEAD = 100

# Colors (RGB tuples)
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (255, 228, 181)
WATER_DARK = (41, 128, 185)
WATER_LIGHT = (52, 152, 219)
# ... etc
```

---

## Phase 2: Core Gameplay

### 2.1 Physics Engine

**Physics System** (`src/systems/physics.py`):
```python
class PhysicsEngine:
    def __init__(self):
        self.gravity = GRAVITY
        
    def apply_gravity(self, entity, dt):
        """Apply gravity acceleration to entity"""
        entity.velocity.y += self.gravity * dt
        entity.velocity.y = min(entity.velocity.y, MAX_FALL_SPEED)
        
    def integrate_velocity(self, entity, dt):
        """Update position based on velocity"""
        entity.position.x += entity.velocity.x * dt
        entity.position.y += entity.velocity.y * dt
        
    def check_platform_collision(self, player, platforms):
        """AABB collision detection with one-way platforms"""
        player_rect = player.get_collision_rect()
        
        for platform in platforms:
            if not platform.active:
                continue
                
            platform_rect = platform.get_rect()
            
            # Check if player is falling and above platform
            if player.velocity.y > 0:
                # Check if player's bottom is near platform top
                if (player_rect.bottom >= platform_rect.top and
                    player_rect.bottom <= platform_rect.top + 10 and
                    player_rect.right > platform_rect.left and
                    player_rect.left < platform_rect.right):
                    
                    return platform
                    
        return None
        
    def resolve_collision(self, player, platform):
        """Place player on platform and reset vertical velocity"""
        platform_rect = platform.get_rect()
        player.position.y = platform_rect.top - player.height
        player.velocity.y = 0
        player.on_ground = True
        player.current_platform = platform
```

### 2.2 Player Character System

**Player Class** (`src/entities/player.py`):
```python
class Player:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.width = PLAYER_WIDTH * PLAYER_SCALE
        self.height = PLAYER_HEIGHT * PLAYER_SCALE
        
        # State
        self.state = PlayerState.IDLE
        self.on_ground = False
        self.jump_count = 0
        self.max_jumps = 2
        
        # Helicopter
        self.helicopter_active = False
        self.helicopter_time = 0.0
        self.helicopter_max_time = HELICOPTER_DURATION
        
        # Advanced mechanics
        self.coyote_time = 0.0
        self.jump_buffer = 0.0
        
        # Animation
        self.animation_frame = 0
        self.animation_time = 0.0
        
    def update(self, dt, input_handler):
        # Update timers
        if not self.on_ground:
            self.coyote_time -= dt
        else:
            self.coyote_time = COYOTE_TIME
            
        if self.jump_buffer > 0:
            self.jump_buffer -= dt
            
        # Handle input
        if input_handler.jump_pressed:
            self.jump_buffer = JUMP_BUFFER_TIME
            
        # Process buffered jump
        if self.jump_buffer > 0 and self.can_jump():
            self.jump()
            self.jump_buffer = 0
            
        # Helicopter logic
        if self.helicopter_active:
            self.helicopter_time += dt
            if self.helicopter_time >= self.helicopter_max_time:
                self.deactivate_helicopter()
                
        # Update animation
        self.update_animation(dt)
        
    def jump(self):
        """Execute jump based on current state"""
        if self.jump_count == 0:
            # First jump
            self.velocity.y = JUMP_VELOCITY
            self.state = PlayerState.JUMPING
            self.on_ground = False
            self.jump_count = 1
            # Play jump sound
            
        elif self.jump_count == 1:
            # Double jump
            self.velocity.y = DOUBLE_JUMP_VELOCITY
            self.state = PlayerState.DOUBLE_JUMPING
            self.jump_count = 2
            # Play double jump sound
            
    def activate_helicopter(self):
        """Start helicopter glide"""
        if self.jump_count >= 2 and not self.helicopter_active:
            self.helicopter_active = True
            self.helicopter_time = 0.0
            self.state = PlayerState.HELICOPTER
            # Play helicopter sound
            
    def can_jump(self):
        """Check if player can jump (includes coyote time)"""
        return (self.on_ground or self.coyote_time > 0) and self.jump_count < self.max_jumps
        
    def land_on_platform(self, platform):
        """Reset jump state when landing"""
        self.on_ground = True
        self.jump_count = 0
        self.helicopter_active = False
        self.helicopter_time = 0.0
        self.state = PlayerState.RUNNING
        # Play landing sound
        # Create landing particles
```

### 2.3 Jump Mechanics Implementation

**Input Handler** (`src/systems/input.py`):
```python
class InputHandler:
    def __init__(self):
        self.jump_pressed = False
        self.jump_held = False
        self.jump_released = False
        
        # Previous frame state
        self.prev_jump = False
        
    def update(self, events):
        keys = pygame.key.get_pressed()
        current_jump = keys[pygame.K_SPACE]
        
        # Detect press (edge detection)
        self.jump_pressed = current_jump and not self.prev_jump
        self.jump_held = current_jump
        self.jump_released = not current_jump and self.prev_jump
        
        self.prev_jump = current_jump
        
    def handle_variable_jump(self, player):
        """Allow shorter jumps by releasing space early"""
        if self.jump_released and player.velocity.y < 0:
            player.velocity.y *= VARIABLE_JUMP_MULTIPLIER
```

**Helicopter Mechanics**:
```python
def update_helicopter_physics(player, dt):
    """Modify physics when helicopter is active"""
    if player.helicopter_active:
        # Override gravity with slow fall
        player.velocity.y = HELICOPTER_FALL_SPEED
        
        # Visual feedback
        player.rotation += 360 * dt  # Spin animation
        
        # Particle trail
        if random.random() < 0.3:
            create_helicopter_particle(player.position)
```

### 2.4 Platform Generation

**Platform Generator** (`src/world/platform_generator.py`):
```python
class PlatformGenerator:
    def __init__(self):
        self.platforms = []
        self.last_platform_x = 0
        self.platform_pool = [Platform() for _ in range(20)]
        self.difficulty = 1.0
        
    def generate_initial_platforms(self):
        """Create starting platforms"""
        x = 0
        for i in range(10):
            platform = self.get_platform_from_pool()
            platform.reset(x, SCREEN_HEIGHT - 200, 150, PLATFORM_HEIGHT)
            self.platforms.append(platform)
            x += 200
            
        self.last_platform_x = x
        
    def update(self, camera_x):
        """Generate new platforms as camera moves"""
        # Remove off-screen platforms
        self.platforms = [p for p in self.platforms 
                         if p.position.x + p.width > camera_x - 100]
        
        # Generate new platforms ahead
        while self.last_platform_x < camera_x + PLATFORM_SPAWN_DISTANCE:
            self.generate_next_platform()
            
    def generate_next_platform(self):
        """Create next platform with difficulty scaling"""
        # Calculate gap based on difficulty
        min_gap = 100
        max_gap = 200 + (self.difficulty * 50)
        gap = random.uniform(min_gap, max_gap)
        
        # Ensure gap is jumpable
        max_jump_distance = calculate_max_jump_distance()
        gap = min(gap, max_jump_distance * 0.9)
        
        # Random platform type
        platform_type = self.choose_platform_type()
        
        # Random width
        width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        
        # Height variation
        last_platform = self.platforms[-1] if self.platforms else None
        if last_platform:
            height_diff = random.uniform(-100, 50)
            y = last_platform.position.y + height_diff
            y = max(200, min(SCREEN_HEIGHT - 150, y))
        else:
            y = SCREEN_HEIGHT - 200
            
        # Create platform
        x = self.last_platform_x + gap
        platform = self.get_platform_from_pool()
        platform.reset(x, y, width, PLATFORM_HEIGHT, platform_type)
        
        self.platforms.append(platform)
        self.last_platform_x = x + width
        
    def choose_platform_type(self):
        """Select platform type based on difficulty"""
        roll = random.random()
        
        if self.difficulty < 2.0:
            return PlatformType.STATIC
            
        if roll < 0.7:
            return PlatformType.STATIC
        elif roll < 0.85:
            return PlatformType.MOVING
        elif roll < 0.95:
            return PlatformType.SMALL
        else:
            return PlatformType.CRUMBLING
```

**Jump Distance Calculator**:
```python
def calculate_max_jump_distance():
    """Calculate maximum horizontal distance player can jump"""
    # Single jump arc
    jump_time = 2 * abs(JUMP_VELOCITY) / GRAVITY
    single_jump_distance = PLAYER_RUN_SPEED * jump_time
    
    # Double jump extends distance
    double_jump_time = 2 * abs(DOUBLE_JUMP_VELOCITY) / GRAVITY
    double_jump_distance = PLAYER_RUN_SPEED * double_jump_time
    
    # Helicopter adds extra distance
    helicopter_distance = PLAYER_RUN_SPEED * HELICOPTER_DURATION
    
    return single_jump_distance + double_jump_distance + helicopter_distance
```

---

## Phase 3: Visual Polish

### 3.1 Sprite Generation System

**Sprite Generator** (`src/graphics/sprite_generator.py`):
```python
class SpriteGenerator:
    def __init__(self):
        self.sprite_cache = {}
        
    def generate_player_sprites(self):
        """Generate all player animation frames"""
        sprites = {
            'idle': self.generate_idle_frames(),
            'run': self.generate_run_frames(),
            'jump': self.generate_jump_frames(),
            'double_jump': self.generate_double_jump_frames(),
            'helicopter': self.generate_helicopter_frames(),
        }
        return sprites
        
    def generate_idle_frames(self):
        """Create 4-frame idle animation"""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            surface.set_colorkey((0, 0, 0))
            
            # Draw character body
            # Frame 0-3: slight breathing motion
            offset_y = int(math.sin(i * math.pi / 2) * 2)
            
            # Body (red rectangle with rounded corners)
            body_rect = pygame.Rect(8, 8 + offset_y, 16, 20)
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            
            # Eyes (white dots)
            pygame.draw.circle(surface, (255, 255, 255), (13, 14 + offset_y), 2)
            pygame.draw.circle(surface, (255, 255, 255), (19, 14 + offset_y), 2)
            
            # Scale up
            scaled = pygame.transform.scale(surface, 
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
            
        return frames
        
    def generate_run_frames(self):
        """Create 6-frame run cycle"""
        frames = []
        for i in range(6):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            surface.set_colorkey((0, 0, 0))
            
            # Bobbing motion
            bob = int(math.sin(i * math.pi / 3) * 3)
            
            # Body
            body_rect = pygame.Rect(8, 6 + bob, 16, 20)
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            
            # Legs (alternating)
            leg_offset = 1 if i % 2 == 0 else -1
            pygame.draw.rect(surface, PLAYER_SECONDARY, 
                (11 + leg_offset, 24 + bob, 4, 6))
            pygame.draw.rect(surface, PLAYER_SECONDARY, 
                (17 - leg_offset, 24 + bob, 4, 6))
            
            # Eyes
            pygame.draw.circle(surface, (255, 255, 255), (13, 12 + bob), 2)
            pygame.draw.circle(surface, (255, 255, 255), (19, 12 + bob), 2)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, PLAYER_HEIGHT * PLAYER_SCALE))
            frames.append(scaled)
            
        return frames
        
    def generate_helicopter_frames(self):
        """Create 4-frame helicopter animation with rotor"""
        frames = []
        for i in range(4):
            surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT + 8))
            surface.set_colorkey((0, 0, 0))
            
            # Body (slightly tilted)
            body_rect = pygame.Rect(8, 12, 16, 18)
            pygame.draw.rect(surface, PLAYER_PRIMARY, body_rect, border_radius=4)
            
            # Rotor (spinning)
            rotor_angle = i * 90
            rotor_length = 12
            center_x, center_y = 16, 8
            
            # Draw rotor blades
            for angle in [rotor_angle, rotor_angle + 180]:
                rad = math.radians(angle)
                end_x = center_x + math.cos(rad) * rotor_length
                end_y = center_y + math.sin(rad) * rotor_length
                pygame.draw.line(surface, PLAYER_ACCENT,
                    (center_x, center_y), (end_x, end_y), 2)
            
            # Eyes (determined expression)
            pygame.draw.circle(surface, (255, 255, 255), (13, 18), 2)
            pygame.draw.circle(surface, (255, 255, 255), (19, 18), 2)
            
            scaled = pygame.transform.scale(surface,
                (PLAYER_WIDTH * PLAYER_SCALE, (PLAYER_HEIGHT + 8) * PLAYER_SCALE))
            frames.append(scaled)
            
        return frames
```

### 3.2 Animation System

**Animation Controller** (`src/systems/animation.py`):
```python
class AnimationController:
    def __init__(self, sprite_sheets):
        self.sprite_sheets = sprite_sheets
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_time = 0.0
        self.frame_durations = {
            'idle': 1.0 / 8,   # 8 FPS
            'run': 1.0 / 12,   # 12 FPS
            'jump': 1.0 / 10,
            'double_jump': 1.0 / 15,
            'helicopter': 1.0 / 16,  # 16 FPS for fast rotor
        }
        
    def update(self, dt, player_state):
        # Change animation based on state
        new_animation = self.get_animation_for_state(player_state)
        if new_animation != self.current_animation:
            self.change_animation(new_animation)
            
        # Update frame
        self.animation_time += dt
        frame_duration = self.frame_durations[self.current_animation]
        
        if self.animation_time >= frame_duration:
            self.animation_time = 0.0
            self.current_frame += 1
            
            # Loop animation
            frames = self.sprite_sheets[self.current_animation]
            if self.current_frame >= len(frames):
                self.current_frame = 0
                
    def get_current_sprite(self):
        frames = self.sprite_sheets[self.current_animation]
        return frames[self.current_frame]
        
    def change_animation(self, animation_name):
        self.current_animation = animation_name
        self.current_frame = 0
        self.animation_time = 0.0
```

### 3.3 Camera System

**Camera** (`src/systems/camera.py`):
```python
class Camera:
    def __init__(self, width, height):
        self.position = Vector2(0, 0)
        self.target_position = Vector2(0, 0)
        self.width = width
        self.height = height
        self.smoothing = CAMERA_SMOOTHING
        
        # Screen shake
        self.shake_amount = 0.0
        self.shake_duration = 0.0
        self.shake_offset = Vector2(0, 0)
        
    def update(self, dt, player):
        # Calculate desired position
        self.target_position.x = player.position.x - self.width * CAMERA_PLAYER_OFFSET_X
        
        # Vertical: keep player in view but don't follow too closely
        if player.position.y < self.position.y + 200:
            self.target_position.y = player.position.y - 200
        elif player.position.y > self.position.y + 400:
            self.target_position.y = player.position.y - 400
            
        # Smooth follow with lerp
        self.position.x += (self.target_position.x - self.position.x) * self.smoothing
        self.position.y += (self.target_position.y - self.position.y) * self.smoothing
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0
            
    def apply_shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_duration = duration
        
    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        return Vector2(
            world_pos.x - self.position.x + self.shake_offset.x,
            world_pos.y - self.position.y + self.shake_offset.y
        )
```

### 3.4 Parallax Background

**Parallax System** (`src/graphics/background.py`):
```python
class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.layers = []
        self.create_layers(screen_width, screen_height)
        
    def create_layers(self, width, height):
        # Sky gradient (static)
        sky_layer = self.create_sky_gradient(width, height)
        self.layers.append({'surface': sky_layer, 'speed': 0.0, 'x': 0})
        
        # Far clouds
        far_clouds = self.create_cloud_layer(width, height, 3)
        self.layers.append({'surface': far_clouds, 'speed': 0.2, 'x': 0})
        
        # Mid clouds
        mid_clouds = self.create_cloud_layer(width, height, 5)
        self.layers.append({'surface': mid_clouds, 'speed': 0.5, 'x': 0})
        
        # Water surface
        water = self.create_water_layer(width, height)
        self.layers.append({'surface': water, 'speed': 1.0, 'x': 0})
        
    def create_sky_gradient(self, width, height):
        surface = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / height
            color = (
                int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * ratio),
                int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * ratio),
                int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * ratio),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))
        return surface
        
    def create_cloud_layer(self, width, height, num_clouds):
        # Create surface 2x width for seamless scrolling
        surface = pygame.Surface((width * 2, height))
        surface.set_colorkey((0, 0, 0))
        
        for i in range(num_clouds):
            x = random.randint(0, width * 2)
            y = random.randint(50, height // 3)
            self.draw_cloud(surface, x, y)
            
        return surface
        
    def draw_cloud(self, surface, x, y):
        # Simple cloud using circles
        cloud_color = (255, 255, 255, 128)
        pygame.draw.circle(surface, cloud_color, (x, y), 30)
        pygame.draw.circle(surface, cloud_color, (x + 25, y), 35)
        pygame.draw.circle(surface, cloud_color, (x + 50, y), 30)
        
    def update(self, dt, camera_x):
        for layer in self.layers[1:]:  # Skip static sky
            layer['x'] = -camera_x * layer['speed']
            
    def render(self, screen, camera):
        for layer in self.layers:
            if layer['speed'] == 0.0:
                # Static layer
                screen.blit(layer['surface'], (0, 0))
            else:
                # Scrolling layer
                x_offset = layer['x'] % layer['surface'].get_width()
                screen.blit(layer['surface'], (-x_offset, 0))
                # Draw second copy for seamless loop
                if x_offset > 0:
                    screen.blit(layer['surface'], 
                        (layer['surface'].get_width() - x_offset, 0))
```

---

## Phase 4: UI & Progression

### 4.1 UI Rendering System

**UI Renderer** (`src/graphics/ui.py`):
```python
class UIRenderer:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
    def render_score(self, screen, score, combo):
        # Score
        score_text = self.font_medium.render(f"Score: {score}", True, UI_TEXT)
        score_shadow = self.font_medium.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_shadow, (22, 22))
        screen.blit(score_text, (20, 20))
        
        # Combo
        if combo > 1:
            combo_text = self.font_small.render(f"x{combo}", True, UI_ACCENT)
            screen.blit(combo_text, (20, 70))
            
    def render_helicopter_meter(self, screen, player):
        if player.helicopter_active:
            # Meter background
            meter_x, meter_y = 20, 120
            meter_width, meter_height = 200, 20
            
            pygame.draw.rect(screen, UI_PRIMARY,
                (meter_x, meter_y, meter_width, meter_height))
                
            # Fill based on remaining time
            fill_ratio = 1.0 - (player.helicopter_time / player.helicopter_max_time)
            fill_width = int(meter_width * fill_ratio)
            
            pygame.draw.rect(screen, UI_ACCENT,
                (meter_x, meter_y, fill_width, meter_height))
                
            # Border
            pygame.draw.rect(screen, UI_TEXT,
                (meter_x, meter_y, meter_width, meter_height), 2)
```

### 4.2 Difficulty Manager

**Difficulty System** (`src/world/difficulty_manager.py`):
```python
class DifficultyManager:
    def __init__(self):
        self.game_time = 0.0
        self.game_speed = BASE_GAME_SPEED
        self.difficulty_level = 1.0
        
    def update(self, dt):
        self.game_time += dt
        
        # Increase speed every interval
        speed_increases = int(self.game_time / SPEED_INCREASE_INTERVAL)
        self.game_speed = min(
            BASE_GAME_SPEED + (speed_increases * SPEED_INCREASE_AMOUNT),
            MAX_GAME_SPEED
        )
        
        # Calculate difficulty level (1.0 to 3.0)
        self.difficulty_level = 1.0 + (self.game_time / 60.0)
        self.difficulty_level = min(self.difficulty_level, 3.0)
        
    def get_platform_gap_range(self):
        """Return min/max gap based on difficulty"""
        base_min = 100
        base_max = 200
        
        max_gap = base_max + (self.difficulty_level * 50)
        return (base_min, max_gap)
        
    def should_spawn_moving_platform(self):
        if self.difficulty_level < 1.5:
            return False
        return random.random() < (0.1 * self.difficulty_level)
        
    def should_spawn_crumbling_platform(self):
        if self.game_time < 30:
            return False
        return random.random() < 0.1
```

---

## Phase 5: Audio & Polish

### 5.1 Procedural Audio Generation

**Audio Manager** (`src/systems/audio.py`):
```python
import numpy as np

class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.generate_all_sounds()
        
    def generate_all_sounds(self):
        self.sounds['jump'] = self.generate_jump_sound()
        self.sounds['double_jump'] = self.generate_double_jump_sound()
        self.sounds['helicopter'] = self.generate_helicopter_sound()
        self.sounds['