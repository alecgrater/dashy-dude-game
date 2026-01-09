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
import sys
import traceback


async def main():
    """Main entry point - async for web compatibility."""
    try:
        print("=" * 50)
        print("DASHY DUDE")
        print("=" * 50)
        print()
        print("Python version:", sys.version)
        print("Platform:", sys.platform)
        print()
        print("Controls:")
        print("  SPACE - Jump / Double Jump / Helicopter Glide")
        print("           (Hold SPACE after double jump to glide!)")
        print("  ESC   - Quit")
        print()
        print("Starting game...")
        print()

        # Import game here to catch import errors
        print("Importing game module...")
        from src.game import Game
        print("Game module imported successfully")

        print("Creating game instance...")
        game = Game()
        print("Game instance created")

        print("Running game loop...")
        await game.run()

        print()
        print("Thanks for playing!")

    except ImportError as e:
        print(f"FATAL ERROR - Failed to import required module:")
        print(f"  {e}")
        traceback.print_exc()
        print()
        print("The game cannot start. Please check that all dependencies are installed.")
    except Exception as e:
        print(f"FATAL ERROR - Unexpected error during game initialization:")
        print(f"  {e}")
        traceback.print_exc()
        print()
        print("The game has crashed. Please report this error.")


# Entry point
if __name__ == "__main__":
    asyncio.run(main())