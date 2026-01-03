"""
High score and statistics persistence system.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any


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
    Manages persistent storage of high scores, run history, statistics, settings, and customization.
    Uses separate files for scores/stats and settings/customization.
    """
    
    def __init__(self, save_file: str = "data/high_scores.json", settings_file: str = "data/settings.json"):
        """
        Initialize save system.
        
        Args:
            save_file: Path to high scores and statistics file
            settings_file: Path to settings and customization file
        """
        self.save_file = save_file
        self.settings_file = settings_file
        self.high_scores: List[HighScoreEntry] = []
        self.max_scores = 10  # Keep top 10 scores
        self.max_run_history = 50  # Keep last 50 runs
        self.customization: Dict = {}  # Store customization preferences
        self.settings: Dict = {}  # Store game settings
        self.run_history: List[Dict] = []  # Store detailed run history
        self.all_time_stats: Dict = {}  # Store aggregated all-time statistics
        self.load()
    
    def load(self):
        """Load all data from files."""
        self._load_scores()
        self._load_settings()
    
    def _load_scores(self):
        """Load high scores and statistics from file."""
        if not os.path.exists(self.save_file):
            self.high_scores = []
            self.run_history = []
            self.all_time_stats = {}
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
                # Load run history
                self.run_history = data.get('run_history', [])
                # Load all-time stats
                self.all_time_stats = data.get('all_time_stats', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading high scores: {e}")
            self.high_scores = []
            self.run_history = []
            self.all_time_stats = {}
    
    def _load_settings(self):
        """Load settings and customization from file."""
        if not os.path.exists(self.settings_file):
            self.customization = {}
            self.settings = {}
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.customization = data.get('customization', {})
                self.settings = data.get('settings', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")
            self.customization = {}
            self.settings = {}
    
    def save(self):
        """Save high scores and statistics to file."""
        self._save_scores()
    
    def _save_scores(self):
        """Save high scores and statistics to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            data = {
                'scores': [entry.to_dict() for entry in self.high_scores],
                'run_history': self.run_history,
                'all_time_stats': self.all_time_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving high scores: {e}")
    
    def _save_settings(self):
        """Save settings and customization to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            data = {
                'customization': self.customization,
                'settings': self.settings,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
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
    
    def add_run(self, run_stats: Dict) -> None:
        """
        Add a run to the history and update all-time stats.
        
        Args:
            run_stats: Dictionary of detailed run statistics
        """
        # Add to run history (most recent first)
        self.run_history.insert(0, run_stats)
        
        # Trim history to max size
        if len(self.run_history) > self.max_run_history:
            self.run_history = self.run_history[:self.max_run_history]
        
        # Update all-time stats
        self._update_all_time_stats(run_stats)
        
        # Save changes
        self.save()
    
    def _update_all_time_stats(self, run_stats: Dict) -> None:
        """
        Update all-time statistics with a new run.
        
        Args:
            run_stats: Dictionary of run statistics
        """
        # Initialize all-time stats if empty
        if not self.all_time_stats:
            self.all_time_stats = {
                'total_runs': 0,
                'total_score': 0,
                'total_play_time': 0.0,
                'total_distance': 0,
                'best_score': 0,
                'best_combo': 0,
                'best_multiplier': 1,
                'longest_run_time': 0.0,
                'furthest_distance': 0,
                'total_jumps': 0,
                'total_single_jumps': 0,
                'total_double_jumps': 0,
                'total_triple_jumps': 0,
                'total_helicopter_uses': 0,
                'total_helicopter_time': 0.0,
                'total_platforms_by_type': {
                    'static': 0, 'moving': 0, 'small': 0, 'crumbling': 0,
                    'bouncy': 0, 'ice': 0, 'conveyor': 0, 'disappearing': 0, 'spring': 0
                },
                'total_platforms_landed': 0,
                'total_collectibles_by_type': {
                    'coin': 0, 'speed_boost': 0, 'shield': 0,
                    'magnet': 0, 'double_points': 0, 'extra_jump': 0
                },
                'total_collectibles': 0,
                'total_coins': 0,
                'total_powerups': 0,
                'total_shields_used': 0,
                'avg_score': 0.0,
                'avg_play_time': 0.0,
                'avg_platforms_per_run': 0.0,
                'avg_collectibles_per_run': 0.0
            }
        
        stats = self.all_time_stats
        
        # Update totals
        stats['total_runs'] += 1
        stats['total_score'] += run_stats.get('score', 0)
        stats['total_play_time'] += run_stats.get('play_time', 0.0)
        stats['total_distance'] += run_stats.get('distance_traveled', 0)
        
        # Update bests
        if run_stats.get('score', 0) > stats['best_score']:
            stats['best_score'] = run_stats.get('score', 0)
        if run_stats.get('max_combo', 0) > stats['best_combo']:
            stats['best_combo'] = run_stats.get('max_combo', 0)
        if run_stats.get('max_multiplier', 1) > stats['best_multiplier']:
            stats['best_multiplier'] = run_stats.get('max_multiplier', 1)
        if run_stats.get('play_time', 0.0) > stats['longest_run_time']:
            stats['longest_run_time'] = run_stats.get('play_time', 0.0)
        if run_stats.get('distance_traveled', 0) > stats['furthest_distance']:
            stats['furthest_distance'] = run_stats.get('distance_traveled', 0)
        
        # Update jump totals
        stats['total_jumps'] += run_stats.get('total_jumps', 0)
        stats['total_single_jumps'] += run_stats.get('single_jumps', 0)
        stats['total_double_jumps'] += run_stats.get('double_jumps', 0)
        stats['total_triple_jumps'] += run_stats.get('triple_jumps', 0)
        stats['total_helicopter_uses'] += run_stats.get('helicopter_uses', 0)
        stats['total_helicopter_time'] += run_stats.get('helicopter_time', 0.0)
        
        # Update platform totals
        stats['total_platforms_landed'] += run_stats.get('total_platforms_landed', 0)
        platforms_landed = run_stats.get('platforms_landed', {})
        for ptype, count in platforms_landed.items():
            if ptype in stats['total_platforms_by_type']:
                stats['total_platforms_by_type'][ptype] += count
        
        # Update collectible totals
        stats['total_collectibles'] += run_stats.get('total_collectibles', 0)
        stats['total_coins'] += run_stats.get('coins_collected', 0)
        stats['total_powerups'] += run_stats.get('powerups_collected', 0)
        collectibles_gathered = run_stats.get('collectibles_gathered', {})
        for ctype, count in collectibles_gathered.items():
            if ctype in stats['total_collectibles_by_type']:
                stats['total_collectibles_by_type'][ctype] += count
        
        # Update power-up usage
        stats['total_shields_used'] += run_stats.get('shields_used', 0)
        
        # Recalculate averages
        if stats['total_runs'] > 0:
            stats['avg_score'] = stats['total_score'] / stats['total_runs']
            stats['avg_play_time'] = stats['total_play_time'] / stats['total_runs']
            stats['avg_platforms_per_run'] = stats['total_platforms_landed'] / stats['total_runs']
            stats['avg_collectibles_per_run'] = stats['total_collectibles'] / stats['total_runs']
    
    def get_run_history(self) -> List[Dict]:
        """
        Get the run history.
        
        Returns:
            List of run statistics dictionaries (most recent first)
        """
        return self.run_history.copy()
    
    def get_all_time_stats(self) -> Dict:
        """
        Get all-time statistics.
        
        Returns:
            Dictionary of all-time statistics
        """
        return self.all_time_stats.copy()
    
    def get_run_by_index(self, index: int) -> Optional[Dict]:
        """
        Get a specific run from history.
        
        Args:
            index: Index of the run (0 = most recent)
        
        Returns:
            Run statistics dictionary or None if not found
        """
        if 0 <= index < len(self.run_history):
            return self.run_history[index].copy()
        return None
    
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
        Save customization preferences to settings file.
        
        Args:
            customization_dict: Dictionary from CustomizationSystem.to_dict()
        """
        self.customization = customization_dict
        self._save_settings()
    
    def get_customization(self) -> Dict:
        """Get saved customization preferences."""
        return self.customization.copy()
    
    def save_settings(self, settings_dict: Dict):
        """
        Save game settings to settings file.
        
        Args:
            settings_dict: Dictionary of game settings
        """
        self.settings = settings_dict
        self._save_settings()
    
    def get_settings(self) -> Dict:
        """Get saved game settings."""
        return self.settings.copy()
    
    def clear_scores(self):
        """Clear all high scores (for testing/reset)."""
        self.high_scores = []
        self._save_scores()
    
    def clear_run_history(self):
        """Clear run history (for testing/reset)."""
        self.run_history = []
        self._save_scores()
    
    def clear_all_time_stats(self):
        """Clear all-time statistics (for testing/reset)."""
        self.all_time_stats = {}
        self._save_scores()
    
    def clear_settings(self):
        """Clear all settings and customization (for testing/reset)."""
        self.customization = {}
        self.settings = {}
        self._save_settings()
    
    def clear_all(self):
        """Clear all saved data (for testing/reset)."""
        self.high_scores = []
        self.run_history = []
        self.all_time_stats = {}
        self.customization = {}
        self.settings = {}
        self._save_scores()
        self._save_settings()