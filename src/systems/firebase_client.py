"""
Firebase integration for web deployment.
This module provides Firebase database access when running in browser via Pygbag.
"""
import sys
import json
import asyncio
from typing import Dict, List, Optional


def is_web_platform() -> bool:
    """Check if running in web browser via Pygbag."""
    return sys.platform == "emscripten"


class FirebaseClient:
    """
    Firebase Realtime Database client for web deployment.
    Calls JavaScript Firebase SDK via Pygbag's platform bridge.
    """

    def __init__(self):
        """Initialize Firebase client."""
        self.initialized = False
        self.window = None

        if is_web_platform():
            try:
                import platform
                if hasattr(platform, 'window'):
                    self.window = platform.window
                    # Check if our Firebase helper is available
                    if hasattr(self.window, 'dashyDude'):
                        self.initialized = True
                        print("Firebase client initialized")
                    else:
                        print("Firebase helpers not found in window.dashyDude")
                else:
                    print("Platform.window not available")
            except Exception as e:
                print(f"Failed to initialize Firebase client: {e}")

    def is_available(self) -> bool:
        """Check if Firebase is available and configured."""
        if not self.initialized or not self.window:
            return False

        try:
            # Call JavaScript function to check Firebase availability
            return bool(self.window.dashyDude.isFirebaseAvailable())
        except Exception as e:
            print(f"Error checking Firebase availability: {e}")
            return False

    async def save_high_score(self, score_entry: Dict) -> bool:
        """
        Save a high score to Firebase global leaderboard.

        Args:
            score_entry: Dictionary containing score data (score, name, date, stats)

        Returns:
            True if successful, False otherwise
        """
        if not self.initialized or not self.window:
            return False

        try:
            # Convert dict to JavaScript object
            score_data = {
                'score': score_entry.get('score', 0),
                'name': score_entry.get('name', 'Player'),
                'date': score_entry.get('date', ''),
                'stats': score_entry.get('stats', {})
            }

            # Call JavaScript Firebase function
            result = await self.window.dashyDude.saveHighScore(score_data)
            return bool(result)
        except Exception as e:
            print(f"Error saving high score to Firebase: {e}")
            return False

    async def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve top scores from Firebase global leaderboard.

        Args:
            limit: Maximum number of scores to retrieve

        Returns:
            List of score dictionaries sorted by score descending
        """
        if not self.initialized or not self.window:
            return []

        try:
            # Call JavaScript Firebase function
            scores = await self.window.dashyDude.getTopScores(limit)

            # Convert JavaScript array to Python list
            result = []
            if scores:
                for score in scores:
                    result.append({
                        'score': score.get('score', 0),
                        'name': score.get('name', 'Player'),
                        'date': score.get('date', ''),
                        'stats': score.get('stats', {})
                    })

            return result
        except Exception as e:
            print(f"Error retrieving top scores from Firebase: {e}")
            return []

    async def cleanup_old_scores(self) -> None:
        """
        Clean up old scores from Firebase (keeps top 100).
        Should be called periodically to manage database size.
        """
        if not self.initialized or not self.window:
            return

        try:
            await self.window.dashyDude.cleanupOldScores()
        except Exception as e:
            print(f"Error cleaning up old scores: {e}")


# Global Firebase client instance
_firebase_client: Optional[FirebaseClient] = None


def get_firebase_client() -> Optional[FirebaseClient]:
    """Get or create the global Firebase client instance."""
    global _firebase_client

    if _firebase_client is None and is_web_platform():
        _firebase_client = FirebaseClient()

    return _firebase_client
