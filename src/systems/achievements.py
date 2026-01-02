"""
Achievement tracking and management system.
"""
from enum import Enum
from typing import Dict, List, Callable
import json
import os
from datetime import datetime


class AchievementType(Enum):
    """Types of achievements."""
    FIRST_JUMP = "first_jump"
    DOUBLE_TROUBLE = "double_trouble"
    HELICOPTER_HERO = "helicopter_hero"
    MARATHON_RUNNER = "marathon_runner"
    PERFECT_LANDING = "perfect_landing"
    SPEED_DEMON = "speed_demon"
    COIN_COLLECTOR = "coin_collector"
    COMBO_MASTER = "combo_master"
    HIGH_FLYER = "high_flyer"
    PLATFORM_MASTER = "platform_master"


class Achievement:
    """Represents a single achievement."""
    
    def __init__(
        self,
        achievement_type: AchievementType,
        name: str,
        description: str,
        check_condition: Callable,
        icon_color: tuple = (255, 215, 0)
    ):
        """
        Initialize achievement.
        
        Args:
            achievement_type: Type of achievement
            name: Display name
            description: Description of how to unlock
            check_condition: Function that returns True if unlocked
            icon_color: RGB color for achievement icon
        """
        self.type = achievement_type
        self.name = name
        self.description = description
        self.check_condition = check_condition
        self.icon_color = icon_color
        self.unlocked = False
        self.unlock_date = None
        self.progress = 0  # For tracking progress towards achievement
    
    def check_unlock(self, stats: Dict) -> bool:
        """
        Check if achievement should be unlocked.
        
        Args:
            stats: Dictionary of game statistics
        
        Returns:
            True if achievement was just unlocked
        """
        if self.unlocked:
            return False
        
        if self.check_condition(stats):
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
            return True
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'unlocked': self.unlocked,
            'unlock_date': self.unlock_date,
            'progress': self.progress
        }
    
    @staticmethod
    def from_dict(data: Dict, check_condition: Callable, icon_color: tuple) -> 'Achievement':
        """Create achievement from dictionary."""
        achievement = Achievement(
            AchievementType(data['type']),
            data['name'],
            data['description'],
            check_condition,
            icon_color
        )
        achievement.unlocked = data.get('unlocked', False)
        achievement.unlock_date = data.get('unlock_date')
        achievement.progress = data.get('progress', 0)
        return achievement


class AchievementSystem:
    """
    Manages achievement tracking and persistence.
    """
    
    def __init__(self, save_file: str = "data/achievements.json"):
        """
        Initialize achievement system.
        
        Args:
            save_file: Path to save file
        """
        self.save_file = save_file
        self.achievements: Dict[AchievementType, Achievement] = {}
        self.newly_unlocked: List[Achievement] = []  # Track newly unlocked for notifications
        
        # Define all achievements
        self._define_achievements()
        
        # Load saved progress
        self.load()
    
    def _define_achievements(self):
        """Define all achievements with their unlock conditions."""
        
        # First Jump - Complete first jump
        self.achievements[AchievementType.FIRST_JUMP] = Achievement(
            AchievementType.FIRST_JUMP,
            "First Jump",
            "Complete your first jump",
            lambda stats: stats.get('total_jumps', 0) >= 1,
            (100, 200, 255)
        )
        
        # Double Trouble - Use double jump 100 times
        self.achievements[AchievementType.DOUBLE_TROUBLE] = Achievement(
            AchievementType.DOUBLE_TROUBLE,
            "Double Trouble",
            "Use double jump 100 times",
            lambda stats: stats.get('double_jumps', 0) >= 100,
            (255, 100, 255)
        )
        
        # Helicopter Hero - Use helicopter 50 times
        self.achievements[AchievementType.HELICOPTER_HERO] = Achievement(
            AchievementType.HELICOPTER_HERO,
            "Helicopter Hero",
            "Use helicopter 50 times",
            lambda stats: stats.get('helicopter_uses', 0) >= 50,
            (255, 200, 50)
        )
        
        # Marathon Runner - Survive 5 minutes
        self.achievements[AchievementType.MARATHON_RUNNER] = Achievement(
            AchievementType.MARATHON_RUNNER,
            "Marathon Runner",
            "Survive for 5 minutes in a single run",
            lambda stats: stats.get('play_time', 0) >= 300,  # 5 minutes = 300 seconds
            (50, 255, 50)
        )
        
        # Perfect Landing - Land on 10 small platforms in a row
        self.achievements[AchievementType.PERFECT_LANDING] = Achievement(
            AchievementType.PERFECT_LANDING,
            "Perfect Landing",
            "Achieve a 10x combo",
            lambda stats: stats.get('max_combo', 0) >= 10,
            (255, 150, 50)
        )
        
        # Speed Demon - Reach max difficulty
        self.achievements[AchievementType.SPEED_DEMON] = Achievement(
            AchievementType.SPEED_DEMON,
            "Speed Demon",
            "Reach maximum difficulty level",
            lambda stats: stats.get('max_difficulty_reached', 0) >= 1.0,
            (255, 50, 50)
        )
        
        # Coin Collector - Collect 100 coins
        self.achievements[AchievementType.COIN_COLLECTOR] = Achievement(
            AchievementType.COIN_COLLECTOR,
            "Coin Collector",
            "Collect 100 collectibles",
            lambda stats: stats.get('collectibles_gathered', 0) >= 100,
            (255, 215, 0)
        )
        
        # Combo Master - Achieve a 20x combo
        self.achievements[AchievementType.COMBO_MASTER] = Achievement(
            AchievementType.COMBO_MASTER,
            "Combo Master",
            "Achieve a 20x combo",
            lambda stats: stats.get('max_combo', 0) >= 20,
            (255, 100, 200)
        )
        
        # High Flyer - Land on 100 platforms
        self.achievements[AchievementType.HIGH_FLYER] = Achievement(
            AchievementType.HIGH_FLYER,
            "High Flyer",
            "Land on 100 platforms in a single run",
            lambda stats: stats.get('platforms_landed', 0) >= 100,
            (100, 255, 255)
        )
        
        # Platform Master - Land on 500 platforms total (across all runs)
        self.achievements[AchievementType.PLATFORM_MASTER] = Achievement(
            AchievementType.PLATFORM_MASTER,
            "Platform Master",
            "Land on 500 platforms total",
            lambda stats: stats.get('total_platforms_landed', 0) >= 500,
            (200, 100, 255)
        )
    
    def load(self):
        """Load achievement progress from file."""
        if not os.path.exists(self.save_file):
            return
        
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                
                for achievement_data in data.get('achievements', []):
                    achievement_type = AchievementType(achievement_data['type'])
                    if achievement_type in self.achievements:
                        # Update existing achievement with saved data
                        saved_achievement = self.achievements[achievement_type]
                        saved_achievement.unlocked = achievement_data.get('unlocked', False)
                        saved_achievement.unlock_date = achievement_data.get('unlock_date')
                        saved_achievement.progress = achievement_data.get('progress', 0)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading achievements: {e}")
    
    def save(self):
        """Save achievement progress to file."""
        try:
            data = {
                'achievements': [
                    achievement.to_dict()
                    for achievement in self.achievements.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving achievements: {e}")
    
    def update(self, stats: Dict):
        """
        Update achievement progress and check for unlocks.
        
        Args:
            stats: Dictionary of current game statistics
        """
        self.newly_unlocked.clear()
        
        for achievement in self.achievements.values():
            if achievement.check_unlock(stats):
                self.newly_unlocked.append(achievement)
                print(f"Achievement Unlocked: {achievement.name}")
        
        # Save if any achievements were unlocked
        if self.newly_unlocked:
            self.save()
    
    def get_newly_unlocked(self) -> List[Achievement]:
        """Get list of newly unlocked achievements (for notifications)."""
        return self.newly_unlocked.copy()
    
    def clear_newly_unlocked(self):
        """Clear the newly unlocked list (after showing notifications)."""
        self.newly_unlocked.clear()
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements sorted by unlock status."""
        achievements = list(self.achievements.values())
        # Sort: unlocked first, then by name
        achievements.sort(key=lambda a: (not a.unlocked, a.name))
        return achievements
    
    def get_unlocked_count(self) -> int:
        """Get number of unlocked achievements."""
        return sum(1 for a in self.achievements.values() if a.unlocked)
    
    def get_total_count(self) -> int:
        """Get total number of achievements."""
        return len(self.achievements)
    
    def get_completion_percentage(self) -> float:
        """Get achievement completion percentage."""
        if not self.achievements:
            return 0.0
        return (self.get_unlocked_count() / self.get_total_count()) * 100
    
    def is_unlocked(self, achievement_type: AchievementType) -> bool:
        """Check if specific achievement is unlocked."""
        if achievement_type in self.achievements:
            return self.achievements[achievement_type].unlocked
        return False
    
    def get_achievement(self, achievement_type: AchievementType) -> Achievement:
        """Get specific achievement."""
        return self.achievements.get(achievement_type)
    
    def update_progress(self, achievement_type: AchievementType, progress: int):
        """
        Update progress for a specific achievement.
        
        Args:
            achievement_type: Type of achievement
            progress: Current progress value
        """
        if achievement_type in self.achievements:
            self.achievements[achievement_type].progress = progress
    
    def reset_all(self):
        """Reset all achievements (for testing)."""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_date = None
            achievement.progress = 0
        self.save()