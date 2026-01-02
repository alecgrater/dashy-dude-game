#!/usr/bin/env python3
"""
Simple launcher script for Dashy Dude.
Run this file to start the game.
"""

if __name__ == "__main__":
    from src.game import Game
    
    game = Game()
    game.run()