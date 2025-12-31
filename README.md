# Endless Lake Clone

A polished, modern endless runner game inspired by Endless Lake by Vivid Games S.A., featuring Rayman-style helicopter mechanics.

## Features

### Core Gameplay
- **Single Jump**: Press SPACE to jump
- **Double Jump**: Press SPACE again while airborne
- **Helicopter Glide**: Hold SPACE after double jump to activate a 1.5-second slow-fall glide
- **Advanced Mechanics**:
  - Coyote time (0.1s grace period after leaving platform)
  - Jump buffering (0.15s input buffer before landing)
  - Variable jump height (release SPACE early for shorter jumps)

### Visual Features
- Modern high-resolution pixel art style
- Smooth 60 FPS gameplay
- Parallax scrolling background
- Screen shake effects on landing and death
- Animated water surface with waves
- Multiple platform types with unique visuals

### Platform Types
- **Static Platforms**: Standard platforms of various widths
- **Moving Platforms**: Oscillate horizontally (purple tint)
- **Small Platforms**: Narrow platforms for extra challenge (yellow tint)
- **Crumbling Platforms**: Disappear after landing (red tint, appear after 30 seconds)

### Difficulty Progression
- Game speed increases every 10 seconds
- Platform gaps widen over time
- More challenging platform types spawn as difficulty increases
- Maximum difficulty reached at 3 minutes

## Installation

### Requirements
- Python 3.13.1 or higher
- uv (Python package manager)

### Setup

1. Clone or download this repository

2. Install dependencies using uv:
```bash
uv sync
```

## Running the Game

Run the game using uv:
```bash
uv run python run_game.py
```

Or alternatively:
```bash
uv run python -m src.game
```

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Jump / Double Jump / Helicopter Glide |
| **ESC** | Quit game |

### How to Play

1. Press SPACE to jump over gaps
2. Press SPACE again while in the air to double jump
3. After double jumping, **hold SPACE** to activate the helicopter glide
4. The helicopter glide lasts 1.5 seconds and slows your fall
5. Land on platforms to reset your jumps
6. Avoid falling into the water!
7. Survive as long as possible and rack up points

## Game Architecture

The game is built with a clean, modular architecture:

```
src/
├── entities/       # Player and platform entities
├── systems/        # Physics, camera, input, animation
├── graphics/       # Sprite generation, UI, background
├── world/          # Platform generation, difficulty
├── states/         # Game state management
└── utils/          # Constants, math utilities
```

### Key Systems

- **Physics Engine**: Gravity-based motion with AABB collision detection
- **Camera System**: Smooth following with lerp interpolation and screen shake
- **Animation System**: Frame-based sprite animation with state machine
- **Platform Generator**: Procedural generation with object pooling
- **Difficulty Manager**: Progressive difficulty scaling over time

## Technical Details

- **Engine**: Pygame-CE (Community Edition)
- **Graphics**: Procedurally generated pixel art (no external assets)
- **Frame Rate**: Locked 60 FPS with fixed timestep physics
- **Resolution**: 1280x720
- **Performance**: Optimized with object pooling and culling

## Development

### Project Structure

```
endless-lake-clone/
├── main.py                 # Entry point
├── src/
│   ├── game.py            # Main game loop
│   ├── entities/          # Game entities
│   ├── systems/           # Core systems
│   ├── graphics/          # Rendering
│   ├── world/             # World generation
│   ├── states/            # Game states
│   └── utils/             # Utilities
├── plans/                 # Architecture documentation
├── pyproject.toml         # Dependencies
└── README.md              # This file
```

### Architecture Documentation

See the `plans/` directory for detailed architecture documentation:
- `game_architecture.md` - Complete system design
- `system_diagram.md` - Visual architecture diagrams
- `implementation_guide.md` - Implementation details
- `quick_reference.md` - Quick reference guide

## Credits

- Inspired by **Endless Lake** by Vivid Games S.A.
- Helicopter mechanics inspired by **Rayman** series
- Built with **Pygame-CE** (Community Edition)

## License

This is a learning project created for educational purposes.

## Future Enhancements

Potential features for future versions:
- Procedural audio generation for sound effects
- Particle effects system
- Title screen and menu system
- High score persistence
- More platform types and obstacles
- Power-ups and collectibles
- Multiple character skins

---

**Enjoy the game!** 🎮