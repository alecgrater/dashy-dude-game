# Endless Lake Clone - Game Architecture Plan

## Project Overview
A polished, modern endless runner game inspired by Endless Lake, featuring smooth pixel art graphics, responsive controls, and engaging Rayman-style helicopter mechanics.

## Technical Stack
- **Engine**: Pygame-CE (Community Edition) - Modern, actively maintained fork
- **Python Version**: 3.13.1
- **Graphics**: High-resolution pixel art with smooth animations
- **Audio**: Procedural sound generation using pygame.mixer
- **Target Performance**: 60 FPS

## Project Structure

```
endless-lake-clone/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── game.py            # Main game class and loop
│   ├── states/
│   │   ├── __init__.py
│   │   ├── base_state.py  # Abstract state class
│   │   ├── title_state.py # Title screen
│   │   ├── play_state.py  # Main gameplay
│   │   └── gameover_state.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── player.py      # Player character
│   │   ├── platform.py    # Platform objects
│   │   └── particle.py    # Particle effects
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── physics.py     # Physics engine
│   │   ├── camera.py      # Camera system
│   │   ├── input.py       # Input handling
│   │   ├── animation.py   # Animation system
│   │   └── audio.py       # Procedural audio
│   ├── graphics/
│   │   ├── __init__.py
│   │   ├── sprite_generator.py  # Procedural sprite creation
│   │   ├── background.py        # Parallax backgrounds
│   │   └── ui.py                # UI rendering
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py   # Game constants
│   │   ├── math_utils.py  # Easing, interpolation
│   │   └── colors.py      # Color palette
│   └── world/
│       ├── __init__.py
│       ├── platform_generator.py
│       └── difficulty_manager.py
├── assets/                # Generated at runtime
│   └── sprites/          # Cached sprite surfaces
├── pyproject.toml
└── README.md
```

## Core Systems Architecture

### 1. Game State Manager
```
┌─────────────────────────────────────┐
│         Game State Manager          │
├─────────────────────────────────────┤
│  - Current State                    │
│  - State Stack                      │
│  - Transition System                │
└─────────────────────────────────────┘
           │
           ├──> Title State
           ├──> Play State
           └──> Game Over State
```

**State Interface**:
- `enter()` - Initialize state
- `exit()` - Cleanup state
- `update(dt)` - Update logic
- `render(screen)` - Draw state
- `handle_event(event)` - Process input

### 2. Physics Engine

**Components**:
- Gravity system (constant downward acceleration)
- Velocity integration (Euler method for simplicity, stable at 60 FPS)
- Collision detection (AABB for platforms, point-in-rect for player)
- Friction/air resistance (minimal for tight controls)

**Physics Constants**:
```python
GRAVITY = 2000.0  # pixels/second²
MAX_FALL_SPEED = 1000.0  # pixels/second
JUMP_VELOCITY = -600.0  # pixels/second
DOUBLE_JUMP_VELOCITY = -550.0
HELICOPTER_FALL_SPEED = 100.0  # Slow fall during glide
HELICOPTER_DURATION = 1.5  # seconds
```

**Collision System**:
- Player has collision box (smaller than sprite for better feel)
- Platforms have collision rectangles
- One-way platforms (can jump through from below)
- Water collision (instant death)

### 3. Player Character System

**State Machine**:
```
IDLE ──> RUNNING ──> JUMPING ──> DOUBLE_JUMPING ──> HELICOPTER
  ↑         ↑           ↑              ↑                 ↓
  └─────────┴───────────┴──────────────┴─────────────────┘
                    (Landing on platform)
```

**Animation States**:
- **Idle**: 4 frames, 8 FPS (breathing animation)
- **Running**: 6 frames, 12 FPS (smooth run cycle)
- **Jumping**: 3 frames (anticipation, peak, fall)
- **Double Jump**: 4 frames (spin animation)
- **Helicopter**: 4 frames, 16 FPS (rotor spinning)

**Jump Mechanics**:
1. **Single Jump**: Press space while grounded
2. **Double Jump**: Press space while airborne (once)
3. **Helicopter Glide**: Hold space after double jump
   - Reduces fall speed dramatically
   - Limited duration (1.5 seconds)
   - Visual feedback (rotor animation, particle trail)
   - Cannot be reactivated until landing

**Advanced Mechanics**:
- **Coyote Time**: 0.1s grace period after leaving platform
- **Jump Buffering**: 0.15s input buffer before landing
- **Variable Jump Height**: Release space early for shorter jump

### 4. Platform Generation System

**Generation Algorithm**:
```python
class PlatformGenerator:
    - spawn_distance: Distance ahead to spawn platforms
    - min_gap: Minimum horizontal gap
    - max_gap: Maximum horizontal gap (increases with difficulty)
    - platform_pool: Object pool for performance
    
    def generate_platform():
        - Calculate next position based on last platform
        - Randomize platform type (static, moving, small, large)
        - Ensure gap is jumpable (with double jump + helicopter)
        - Add variation in height
```

**Platform Types**:
1. **Static**: Standard platform, various widths (80-200px)
2. **Moving**: Horizontal oscillation, slower speed
3. **Small**: Narrow platforms (60px), higher score multiplier
4. **Crumbling**: Disappears after landing (visual warning)

**Difficulty Progression**:
- Game speed increases every 10 seconds (max 2x base speed)
- Platform gaps widen gradually
- More moving/small platforms spawn
- Crumbling platforms appear after 30 seconds

### 5. Camera System

**Smooth Following**:
```python
class Camera:
    - target: Player position
    - offset: Camera offset from player
    - smoothing: Lerp factor (0.1 for smooth follow)
    - shake: Screen shake effect
    
    def update(dt):
        # Smooth follow with lerp
        desired_x = target.x - SCREEN_WIDTH * 0.3
        camera.x = lerp(camera.x, desired_x, smoothing)
        
        # Keep player in view vertically
        if target.y < camera.y + 200:
            camera.y = lerp(camera.y, target.y - 200, smoothing)
```

**Parallax Layers**:
1. **Sky**: Static gradient background
2. **Far Clouds**: 0.2x scroll speed
3. **Mid Clouds**: 0.5x scroll speed
4. **Water Surface**: 1.0x scroll speed (with wave animation)
5. **Foreground**: 1.2x scroll speed (optional decorative elements)

### 6. UI System

**Title Screen**:
```
┌─────────────────────────────────────┐
│                                     │
│         ENDLESS LAKE                │
│         ════════════                │
│                                     │
│         ┌─────────────┐            │
│         │    PLAY     │            │
│         └─────────────┘            │
│                                     │
│    [Animated water background]     │
└─────────────────────────────────────┘
```

**In-Game HUD**:
```
Score: 1234        Combo: x3
[Helicopter meter: ████░░░░]
```

**Game Over Screen**:
```
┌─────────────────────────────────────┐
│         GAME OVER                   │
│                                     │
│    Final Score: 1234                │
│    Best Score: 2000                 │
│                                     │
│    ┌─────────────┐                 │
│    │   RESTART   │                 │
│    └─────────────┘                 │
│    ┌─────────────┐                 │
│    │    MENU     │                 │
│    └─────────────┘                 │
└─────────────────────────────────────┘
```

### 7. Audio System (Procedural)

**Sound Generation**:
```python
class AudioManager:
    def generate_jump_sound():
        # Rising tone, 0.1s duration
        # Frequency: 200Hz -> 400Hz
        
    def generate_double_jump_sound():
        # Higher pitch, 0.15s duration
        # Frequency: 400Hz -> 600Hz
        
    def generate_helicopter_sound():
        # Continuous whirring, looped
        # Frequency: 150Hz with vibrato
        
    def generate_landing_sound():
        # Short thud, 0.05s duration
        # Frequency: 100Hz
        
    def generate_death_sound():
        # Descending tone, 0.3s duration
        # Frequency: 400Hz -> 100Hz
```

**Background Music**:
- Simple procedural loop using sine waves
- Upbeat tempo (120 BPM)
- Major key for positive feel
- Layers added as score increases

## Visual Design Specifications

### Color Palette (Modern Pixel Art)
```python
# Sky gradient
SKY_TOP = (135, 206, 235)      # Light blue
SKY_BOTTOM = (255, 228, 181)   # Peach

# Water
WATER_DARK = (41, 128, 185)    # Deep blue
WATER_LIGHT = (52, 152, 219)   # Light blue
WATER_FOAM = (236, 240, 241)   # White foam

# Platforms
PLATFORM_BASE = (52, 73, 94)   # Dark gray
PLATFORM_HIGHLIGHT = (127, 140, 141)  # Light gray
PLATFORM_GRASS = (46, 204, 113)  # Green top

# Player
PLAYER_PRIMARY = (231, 76, 60)   # Red
PLAYER_SECONDARY = (192, 57, 43) # Dark red
PLAYER_ACCENT = (255, 255, 255)  # White

# UI
UI_PRIMARY = (44, 62, 80)      # Dark blue-gray
UI_ACCENT = (52, 152, 219)     # Bright blue
UI_TEXT = (236, 240, 241)      # Off-white
```

### Sprite Specifications

**Player Character** (32x32 base, scaled 2x for 64x64 display):
- Pixel art style with clean outlines
- Smooth animation frames
- Rotor blades for helicopter mode
- Expressive poses

**Platforms** (Variable width x 16 height, scaled 2x):
- Textured top surface (grass/wood)
- Side detail for depth
- Shadow underneath
- Animated moving platforms

**Particles**:
- Jump dust (4x4 pixels)
- Landing impact (8x8 pixels)
- Helicopter trail (6x6 pixels)
- Water splash (16x16 pixels)

## Performance Optimization

### Rendering Optimization
1. **Dirty Rectangle System**: Only redraw changed areas
2. **Sprite Caching**: Pre-render sprites at startup
3. **Culling**: Don't render off-screen objects
4. **Object Pooling**: Reuse platform/particle objects

### Update Optimization
1. **Spatial Partitioning**: Grid-based collision detection
2. **Fixed Timestep**: Consistent physics at 60 FPS
3. **Lazy Evaluation**: Only update visible entities

### Memory Management
1. **Asset Preloading**: Load all sprites at startup
2. **Sound Caching**: Generate sounds once, reuse
3. **Platform Pool**: Max 20 platforms in memory

## Game Feel & Polish

### Juice Elements
1. **Screen Shake**: On landing, death
2. **Particle Effects**: Jump, land, helicopter trail
3. **Squash & Stretch**: Player sprite on jump/land
4. **Easing Functions**: Smooth UI transitions
5. **Visual Feedback**: Platform highlight on approach
6. **Combo System**: Score multiplier for consecutive platforms

### Timing & Feel
- **Jump Response**: Instant (0 frame delay)
- **Landing Feedback**: 3 frame squash animation
- **Helicopter Activation**: Smooth 0.2s transition
- **Death Animation**: 0.5s fall + splash
- **UI Transitions**: 0.3s fade in/out

## Testing Checklist

### Gameplay Testing
- [ ] Jump feels responsive and satisfying
- [ ] Double jump timing is intuitive
- [ ] Helicopter glide provides meaningful advantage
- [ ] Platform gaps are challenging but fair
- [ ] Difficulty progression feels natural
- [ ] Controls are tight and predictable

### Technical Testing
- [ ] Maintains 60 FPS on target hardware
- [ ] No memory leaks during extended play
- [ ] Collision detection is accurate
- [ ] Audio doesn't crackle or distort
- [ ] UI scales properly on different resolutions

### Edge Cases
- [ ] Rapid input mashing doesn't break mechanics
- [ ] Platform generation never creates impossible gaps
- [ ] Camera doesn't jitter or lose player
- [ ] Game state transitions are smooth
- [ ] Score persists correctly

## Implementation Priority

### Phase 1: Core Foundation
1. Project setup and dependencies
2. Game loop and state manager
3. Basic physics engine
4. Simple player movement

### Phase 2: Core Gameplay
5. Jump mechanics (single, double, helicopter)
6. Platform generation
7. Collision detection
8. Camera system

### Phase 3: Visual Polish
9. Sprite generation system
10. Animation system
11. Parallax backgrounds
12. Particle effects

### Phase 4: UI & Progression
13. Title screen
14. In-game HUD
15. Game over screen
16. Difficulty progression

### Phase 5: Audio & Polish
17. Procedural sound generation
18. Game feel improvements
19. Performance optimization
20. Final testing and documentation

## Success Metrics

The game will be considered complete when:
1. ✅ Runs smoothly at 60 FPS
2. ✅ All jump mechanics work as specified
3. ✅ Platforms generate procedurally without gaps
4. ✅ UI is functional and visually appealing
5. ✅ Audio provides satisfying feedback
6. ✅ Game feels polished and fun to play
7. ✅ Code is clean, documented, and maintainable
8. ✅ Can be run with a single command

## Technical Decisions & Rationale

### Why Pygame-CE?
- Active development and bug fixes
- Better performance than classic Pygame
- Modern Python compatibility
- Community support

### Why Procedural Graphics?
- No copyright concerns
- Consistent art style
- Easy to modify and iterate
- Smaller file size

### Why Fixed Timestep?
- Consistent physics across different hardware
- Predictable gameplay
- Easier to debug and balance

### Why Object Pooling?
- Reduces garbage collection pauses
- Maintains consistent frame rate
- Better memory usage patterns

## Next Steps

After reviewing this architecture plan, we'll proceed to implementation using Code mode. The implementation will follow the phase structure outlined above, building from core systems to polish features.