# Endless Lake Clone

A polished endless runner game inspired by Endless Lake, featuring Rayman-style helicopter mechanics. Built with Python and Pygame-CE.

## Quick Start

### Requirements
- Python 3.13.1+
- uv (Python package manager)

### Installation & Run
```bash
# Install dependencies
uv sync

# Run the game
uv run python run_game.py
```

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Jump / Double Jump / Helicopter Glide (hold after double jump) |
| **ESC** | Quit game |

## Gameplay

### Core Mechanics
- **Single Jump**: Press SPACE to jump
- **Double Jump**: Press SPACE again while airborne
- **Helicopter Glide**: Hold SPACE after double jump for 1.5-second slow-fall
- **Advanced Features**:
  - Coyote time (0.1s grace period after leaving platform)
  - Jump buffering (0.15s input buffer before landing)
  - Variable jump height (release SPACE early for shorter jumps)

### Platform Types
- **Static** (green): Standard platforms of various widths
- **Moving** (purple): Oscillate horizontally
- **Small** (yellow): Narrow platforms for extra challenge
- **Crumbling** (red): Disappear after landing (appear after 30 seconds)

### Difficulty Progression
- Game speed increases every 10 seconds
- Platform gaps widen over time
- More challenging platform types spawn as difficulty increases
- Maximum difficulty reached at 3 minutes

## Features

### Visual
- Modern high-resolution pixel art (procedurally generated)
- Smooth 60 FPS gameplay with fixed timestep physics
- Parallax scrolling background with animated water
- Screen shake effects on landing and death
- Multiple animation states (idle, running, jumping, helicopter)

### Technical
- **Engine**: Pygame-CE (Community Edition)
- **Resolution**: 1280x720
- **Performance**: Optimized with object pooling and culling
- **Architecture**: Clean, modular design with state management

## Project Structure

```
src/
├── entities/       # Player and platform entities
├── systems/        # Physics, camera, input, animation
├── graphics/       # Sprite generation, UI, background
├── world/          # Platform generation, difficulty scaling
├── states/         # Game state management
└── utils/          # Constants, math utilities
```

### Key Systems
- **Physics Engine**: Gravity-based motion with AABB collision detection
- **Camera System**: Smooth following with lerp interpolation and screen shake
- **Animation System**: Frame-based sprite animation with state machine
- **Platform Generator**: Procedural generation with object pooling
- **Difficulty Manager**: Progressive difficulty scaling over time

## Documentation

See the [`plans/`](plans/) directory for detailed architecture documentation:
- [`game_architecture.md`](plans/game_architecture.md) - Complete system design
- [`system_diagram.md`](plans/system_diagram.md) - Visual architecture diagrams
- [`implementation_guide.md`](plans/implementation_guide.md) - Implementation details
- [`quick_reference.md`](plans/quick_reference.md) - Quick reference guide

## Credits

- Inspired by **Endless Lake** by Vivid Games S.A.
- Helicopter mechanics inspired by **Rayman** series
- Built with **Pygame-CE** (Community Edition)

## License

This is a learning project created for educational purposes.

---

**Enjoy the game!** 🎮