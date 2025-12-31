# Quick Reference Guide - Endless Lake Clone

## Project Summary

**Game Type**: Endless runner with Rayman-style helicopter mechanics  
**Engine**: Pygame-CE  
**Python**: 3.13.1  
**Visual Style**: Modern high-resolution pixel art  
**Audio**: Procedural sound generation  
**Target**: 60 FPS, smooth and polished gameplay

---

## Key Features Checklist

### Core Mechanics
- ✅ Single jump (Space)
- ✅ Double jump (Space while airborne)
- ✅ Helicopter glide (Hold Space after double jump, 1.5s duration)
- ✅ Coyote time (0.1s grace period)
- ✅ Jump buffering (0.15s input buffer)
- ✅ Variable jump height (release early for shorter jump)

### Platform Types
- ✅ Static platforms (various widths)
- ✅ Moving platforms (horizontal oscillation)
- ✅ Small platforms (narrow, higher score)
- ✅ Crumbling platforms (disappear after landing)

### Visual Features
- ✅ Parallax scrolling (4 layers)
- ✅ Smooth camera following
- ✅ Screen shake effects
- ✅ Particle systems (jump, land, helicopter trail)
- ✅ Smooth animations (idle, run, jump, double jump, helicopter)
- ✅ Water surface with waves

### UI Screens
- ✅ Title screen (animated background, play button)
- ✅ In-game HUD (score, combo, helicopter meter)
- ✅ Game over screen (final score, restart/menu buttons)

### Audio
- ✅ Jump sound
- ✅ Double jump sound
- ✅ Helicopter sound (looping)
- ✅ Landing sound
- ✅ Death sound
- ✅ Background music loop

### Difficulty Progression
- ✅ Speed increases every 10 seconds
- ✅ Platform gaps widen over time
- ✅ More challenging platform types spawn
- ✅ Crumbling platforms after 30 seconds

---

## File Structure

```
endless-lake-clone/
├── main.py                          # Entry point
├── src/
│   ├── game.py                      # Main game loop
│   ├── states/
│   │   ├── base_state.py           # Abstract state
│   │   ├── title_state.py          # Title screen
│   │   ├── play_state.py           # Gameplay
│   │   └── gameover_state.py       # Game over
│   ├── entities/
│   │   ├── player.py               # Player character
│   │   ├── platform.py             # Platform objects
│   │   └── particle.py             # Particle effects
│   ├── systems/
│   │   ├── physics.py              # Physics engine
│   │   ├── camera.py               # Camera system
│   │   ├── input.py                # Input handling
│   │   ├── animation.py            # Animation controller
│   │   └── audio.py                # Audio generation
│   ├── graphics/
│   │   ├── sprite_generator.py     # Sprite creation
│   │   ├── background.py           # Parallax layers
│   │   └── ui.py                   # UI rendering
│   ├── utils/
│   │   ├── constants.py            # Game constants
│   │   ├── math_utils.py           # Math helpers
│   │   └── colors.py               # Color palette
│   └── world/
│       ├── platform_generator.py   # Platform spawning
│       └── difficulty_manager.py   # Difficulty scaling
└── plans/                           # Documentation
```

---

## Key Constants

```python
# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Physics
GRAVITY = 2000.0
JUMP_VELOCITY = -600.0
DOUBLE_JUMP_VELOCITY = -550.0
HELICOPTER_FALL_SPEED = 100.0
HELICOPTER_DURATION = 1.5

# Mechanics
COYOTE_TIME = 0.1
JUMP_BUFFER_TIME = 0.15

# Difficulty
BASE_GAME_SPEED = 300.0
MAX_GAME_SPEED = 600.0
SPEED_INCREASE_INTERVAL = 10.0
```

---

## Implementation Phases

### Phase 1: Foundation (Core Systems)
1. Project setup with pygame-ce
2. Game loop with fixed timestep
3. State manager
4. Basic physics engine

### Phase 2: Core Gameplay
5. Player character with movement
6. Jump mechanics (single, double, helicopter)
7. Platform generation
8. Collision detection
9. Camera system

### Phase 3: Visual Polish
10. Sprite generation
11. Animation system
12. Parallax backgrounds
13. Particle effects

### Phase 4: UI & Progression
14. Title screen
15. In-game HUD
16. Game over screen
17. Difficulty progression

### Phase 5: Audio & Final Polish
18. Procedural audio
19. Game feel improvements
20. Performance optimization
21. Testing and documentation

---

## Running the Game

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

---

## Controls

- **Space**: Jump / Double Jump / Helicopter Glide
- **ESC**: Pause / Return to menu
- **Mouse**: Click UI buttons

---

## Performance Targets

- **Frame Rate**: Locked 60 FPS
- **Input Latency**: < 16ms (instant response)
- **Memory**: < 200MB
- **Startup Time**: < 2 seconds

---

## Testing Checklist

### Gameplay
- [ ] Jump feels responsive
- [ ] Double jump timing is intuitive
- [ ] Helicopter provides meaningful advantage
- [ ] Platform gaps are fair
- [ ] Difficulty progression feels natural

### Technical
- [ ] Maintains 60 FPS
- [ ] No memory leaks
- [ ] Accurate collision detection
- [ ] Clean audio playback
- [ ] Smooth UI transitions

### Edge Cases
- [ ] Rapid input doesn't break mechanics
- [ ] No impossible platform gaps
- [ ] Camera stays smooth
- [ ] State transitions work correctly
- [ ] Score persists properly

---

## Color Palette

```python
# Sky
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (255, 228, 181)

# Water
WATER_DARK = (41, 128, 185)
WATER_LIGHT = (52, 152, 219)

# Platforms
PLATFORM_BASE = (52, 73, 94)
PLATFORM_GRASS = (46, 204, 113)

# Player
PLAYER_PRIMARY = (231, 76, 60)
PLAYER_SECONDARY = (192, 57, 43)

# UI
UI_PRIMARY = (44, 62, 80)
UI_ACCENT = (52, 152, 219)
UI_TEXT = (236, 240, 241)
```

---

## Next Steps

1. Review this architectural plan
2. Confirm all requirements are covered
3. Switch to Code mode for implementation
4. Follow phase-by-phase implementation
5. Test and iterate on game feel
6. Polish and optimize
7. Create final documentation

---

## Success Criteria

The game is complete when:
1. ✅ Runs at 60 FPS consistently
2. ✅ All jump mechanics work perfectly
3. ✅ Platforms generate without impossible gaps
4. ✅ UI is functional and attractive
5. ✅ Audio provides satisfying feedback
6. ✅ Game feels polished and fun
7. ✅ Code is clean and documented
8. ✅ Single command to run