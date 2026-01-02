"""
Dashy Dude - Main entry point.

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
import asyncio
from src.game import Game


async def main():
    """Main entry point."""
    print("=" * 50)
    print("DASHY DUDE")
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
    await game.run()
    
    print()
    print("Thanks for playing!")


if __name__ == "__main__":
    asyncio.run(main())