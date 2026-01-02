"""
High score and statistics persistence system.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class HighScoreEntry:
    """Represents a single high score entry."""
    
    def __init__(self, score: int, name: str = "Player", date: str = None, stats: Dict = None):
        """
        Initialize high score entry.
        
        Args:
            score: Final score achieved
            name: Player name
            date: Date string (ISO format)
            stats: Dictionary of game statistics
        """
        self.score = score
        self.name = name
        self.date = date or datetime.now().isoformat()
        self.stats = stats or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'score': self.score,
            'name': self.name,
            'date': self.date,
            'stats': self.stats
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'HighScoreEntry':
        """Create entry from dictionary."""
        return HighScoreEntry(
            score=data.get('score', 0),
            name=data.get('name', 'Player'),
            date=data.get('date'),
            stats=data.get('stats', {})
        )


class SaveSystem:
    """
    Manages persistent storage of high scores and statistics.
    """
    
    def __init__(self, save_file: str = "data/high_scores.json"):
        """
        Initialize save system.
        
        Args:
            save_file: Path to save file
        """
        self.save_file = save_file
        self.high_scores: List[HighScoreEntry] = []
        self.max_scores = 10  # Keep top 10 scores
        self.customization: Dict = {}  # Store customization preferences
        self.settings: Dict = {}  # Store game settings
        self.load()
    
    def load(self):
        """Load high scores from file."""
        if not os.path.exists(self.save_file):
            self.high_scores = []
            return
        
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                self.high_scores = [
                    HighScoreEntry.from_dict(entry)
                    for entry in data.get('scores', [])
                ]
                # Sort by score descending
                self.high_scores.sort(key=lambda x: x.score, reverse=True)
                # Keep only top scores
                self.high_scores = self.high_scores[:self.max_scores]
                # Load customization preferences
                self.customization = data.get('customization', {})
                # Load settings
                self.settings = data.get('settings', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading high scores: {e}")
            self.high_scores = []
            self.customization = {}
            self.settings = {}
    
    def save(self):
        """Save high scores to file."""
        try:
            data = {
                'scores': [entry.to_dict() for entry in self.high_scores],
                'customization': self.customization,
                'settings': self.settings,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving high scores: {e}")
    
    def add_score(self, score: int, name: str = "Player", stats: Dict = None) -> bool:
        """
        Add a new score to the high score list.
        
        Args:
            score: Final score achieved
            name: Player name
            stats: Dictionary of game statistics
        
        Returns:
            True if score made it to the high score list
        """
        entry = HighScoreEntry(score, name, stats=stats)
        
        # Check if score qualifies
        if len(self.high_scores) < self.max_scores or score > self.high_scores[-1].score:
            self.high_scores.append(entry)
            self.high_scores.sort(key=lambda x: x.score, reverse=True)
            self.high_scores = self.high_scores[:self.max_scores]
            self.save()
            return True
        
        return False
    
    def get_high_score(self) -> int:
        """Get the highest score."""
        if self.high_scores:
            return self.high_scores[0].score
        return 0
    
    def get_rank(self, score: int) -> Optional[int]:
        """
        Get the rank a score would have (1-based).
        
        Args:
            score: Score to check
        
        Returns:
            Rank (1 = highest) or None if not in top scores
        """
        for i, entry in enumerate(self.high_scores):
            if score >= entry.score:
                return i + 1
        
        # Check if it would make the list
        if len(self.high_scores) < self.max_scores:
            return len(self.high_scores) + 1
        
        return None
    
    def is_high_score(self, score: int) -> bool:
        """
        Check if a score qualifies as a high score.
        
        Args:
            score: Score to check
        
        Returns:
            True if score would make the high score list
        """
        if len(self.high_scores) < self.max_scores:
            return True
        return score > self.high_scores[-1].score
    
    def get_scores(self) -> List[HighScoreEntry]:
        """Get all high scores."""
        return self.high_scores.copy()
    
    def save_customization(self, customization_dict: Dict):
        """
        Save customization preferences.
        
        Args:
            customization_dict: Dictionary from CustomizationSystem.to_dict()
        """
        self.customization = customization_dict
        self.save()
    
    def get_customization(self) -> Dict:
        """Get saved customization preferences."""
        return self.customization.copy()
    
    def save_settings(self, settings_dict: Dict):
        """
        Save game settings.
        
        Args:
            settings_dict: Dictionary of game settings
        """
        self.settings = settings_dict
        self.save()
    
    def get_settings(self) -> Dict:
        """Get saved game settings."""
        return self.settings.copy()
    
    def clear_scores(self):
        """Clear all high scores (for testing/reset)."""
        self.high_scores = []
        self.save()