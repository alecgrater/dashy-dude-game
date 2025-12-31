"""
Endless Lake Clone - Main entry point.

A polished endless runner game with Rayman-style helicopter mechanics.

Controls:
- SPACE: Jump / Double Jump / Helicopter Glide (hold after double jump)
- ESC: Quit game

Features:
- Single jump, double jump, and helicopter glide mechanics
- Procedurally generated platforms with increasing difficulty
- Smooth camera following with screen shake
- Modern pixel art graphics
- Coyote time and jump buffering for responsive controls
"""
from src.game import Game


def main():
    """Main entry point."""
    print("=" * 50)
    print("ENDLESS LAKE CLONE")
    print("=" * 50)
    print()
    print("Controls:")
    print("  SPACE - Jump / Double Jump / Helicopter Glide")
    print("           (Hold SPACE after double jump to glide!)")
    print("  ESC   - Quit")
    print()
    print("Starting game...")
    print()
    
    game = Game()
    game.run()
    
    print()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()