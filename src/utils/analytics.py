"""
Analytics and statistics utilities for tracking and visualizing game data.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class StatCategory(Enum):
    """Categories for organizing statistics."""
    GENERAL = "general"
    PLATFORMS = "platforms"
    COLLECTIBLES = "collectibles"
    JUMPS = "jumps"
    POWERUPS = "powerups"
    PERFORMANCE = "performance"


class RunStatistics:
    """
    Comprehensive statistics for a single game run.
    Tracks all detailed metrics for display and persistence.
    """
    
    def __init__(self):
        """Initialize run statistics with all tracking fields."""
        # General stats
        self.score = 0
        self.play_time = 0.0
        self.distance_traveled = 0
        self.max_difficulty_reached = 0.0
        
        # Jump stats
        self.total_jumps = 0
        self.single_jumps = 0
        self.double_jumps = 0
        self.triple_jumps = 0
        self.helicopter_uses = 0
        self.helicopter_time = 0.0
        
        # Platform stats by type
        self.platforms_landed = {
            'static': 0,
            'moving': 0,
            'small': 0,
            'crumbling': 0,
            'bouncy': 0,
            'ice': 0,
            'conveyor': 0,
            'disappearing': 0,
            'spring': 0
        }
        self.total_platforms_landed = 0
        
        # Collectible stats by type
        self.collectibles_gathered = {
            'coin': 0,
            'speed_boost': 0,
            'shield': 0,
            'magnet': 0,
            'double_points': 0,
            'extra_jump': 0
        }
        self.total_collectibles = 0
        self.coins_collected = 0
        self.powerups_collected = 0
        
        # Combo stats
        self.max_combo = 0
        self.max_multiplier = 1
        self.total_combo_points = 0
        
        # Power-up usage stats
        self.shields_used = 0
        self.speed_boost_time = 0.0
        self.magnet_time = 0.0
        self.double_points_time = 0.0
        
        # Timestamp
        self.timestamp = datetime.now().isoformat()
    
    def record_jump(self, jump_type: str):
        """
        Record a jump event.
        
        Args:
            jump_type: 'single', 'double', 'triple', or 'helicopter'
        """
        self.total_jumps += 1
        if jump_type == 'single':
            self.single_jumps += 1
        elif jump_type == 'double':
            self.double_jumps += 1
        elif jump_type == 'triple':
            self.triple_jumps += 1
        elif jump_type == 'helicopter':
            self.helicopter_uses += 1
    
    def record_platform_landing(self, platform_type: str):
        """
        Record landing on a platform.
        
        Args:
            platform_type: The type of platform landed on
        """
        self.total_platforms_landed += 1
        if platform_type in self.platforms_landed:
            self.platforms_landed[platform_type] += 1
    
    def record_collectible(self, collectible_type: str):
        """
        Record collecting an item.
        
        Args:
            collectible_type: The type of collectible gathered
        """
        self.total_collectibles += 1
        if collectible_type in self.collectibles_gathered:
            self.collectibles_gathered[collectible_type] += 1
        
        if collectible_type == 'coin':
            self.coins_collected += 1
        else:
            self.powerups_collected += 1
    
    def update_combo(self, combo_count: int, multiplier: int):
        """
        Update combo statistics.
        
        Args:
            combo_count: Current combo count
            multiplier: Current score multiplier
        """
        if combo_count > self.max_combo:
            self.max_combo = combo_count
        if multiplier > self.max_multiplier:
            self.max_multiplier = multiplier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary for serialization."""
        return {
            'score': self.score,
            'play_time': self.play_time,
            'distance_traveled': self.distance_traveled,
            'max_difficulty_reached': self.max_difficulty_reached,
            'total_jumps': self.total_jumps,
            'single_jumps': self.single_jumps,
            'double_jumps': self.double_jumps,
            'triple_jumps': self.triple_jumps,
            'helicopter_uses': self.helicopter_uses,
            'helicopter_time': self.helicopter_time,
            'platforms_landed': self.platforms_landed.copy(),
            'total_platforms_landed': self.total_platforms_landed,
            'collectibles_gathered': self.collectibles_gathered.copy(),
            'total_collectibles': self.total_collectibles,
            'coins_collected': self.coins_collected,
            'powerups_collected': self.powerups_collected,
            'max_combo': self.max_combo,
            'max_multiplier': self.max_multiplier,
            'total_combo_points': self.total_combo_points,
            'shields_used': self.shields_used,
            'speed_boost_time': self.speed_boost_time,
            'magnet_time': self.magnet_time,
            'double_points_time': self.double_points_time,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RunStatistics':
        """Create RunStatistics from dictionary."""
        stats = RunStatistics()
        stats.score = data.get('score', 0)
        stats.play_time = data.get('play_time', 0.0)
        stats.distance_traveled = data.get('distance_traveled', 0)
        stats.max_difficulty_reached = data.get('max_difficulty_reached', 0.0)
        stats.total_jumps = data.get('total_jumps', 0)
        stats.single_jumps = data.get('single_jumps', 0)
        stats.double_jumps = data.get('double_jumps', 0)
        stats.triple_jumps = data.get('triple_jumps', 0)
        stats.helicopter_uses = data.get('helicopter_uses', 0)
        stats.helicopter_time = data.get('helicopter_time', 0.0)
        stats.platforms_landed = data.get('platforms_landed', stats.platforms_landed)
        stats.total_platforms_landed = data.get('total_platforms_landed', 0)
        stats.collectibles_gathered = data.get('collectibles_gathered', stats.collectibles_gathered)
        stats.total_collectibles = data.get('total_collectibles', 0)
        stats.coins_collected = data.get('coins_collected', 0)
        stats.powerups_collected = data.get('powerups_collected', 0)
        stats.max_combo = data.get('max_combo', 0)
        stats.max_multiplier = data.get('max_multiplier', 1)
        stats.total_combo_points = data.get('total_combo_points', 0)
        stats.shields_used = data.get('shields_used', 0)
        stats.speed_boost_time = data.get('speed_boost_time', 0.0)
        stats.magnet_time = data.get('magnet_time', 0.0)
        stats.double_points_time = data.get('double_points_time', 0.0)
        stats.timestamp = data.get('timestamp', datetime.now().isoformat())
        return stats


class AllTimeStatistics:
    """
    Aggregated all-time statistics across all game runs.
    """
    
    def __init__(self):
        """Initialize all-time statistics."""
        # General totals
        self.total_runs = 0
        self.total_score = 0
        self.total_play_time = 0.0
        self.total_distance = 0
        
        # Best records
        self.best_score = 0
        self.best_combo = 0
        self.best_multiplier = 1
        self.longest_run_time = 0.0
        self.furthest_distance = 0
        
        # Jump totals
        self.total_jumps = 0
        self.total_single_jumps = 0
        self.total_double_jumps = 0
        self.total_triple_jumps = 0
        self.total_helicopter_uses = 0
        self.total_helicopter_time = 0.0
        
        # Platform totals by type
        self.total_platforms_by_type = {
            'static': 0,
            'moving': 0,
            'small': 0,
            'crumbling': 0,
            'bouncy': 0,
            'ice': 0,
            'conveyor': 0,
            'disappearing': 0,
            'spring': 0
        }
        self.total_platforms_landed = 0
        
        # Collectible totals by type
        self.total_collectibles_by_type = {
            'coin': 0,
            'speed_boost': 0,
            'shield': 0,
            'magnet': 0,
            'double_points': 0,
            'extra_jump': 0
        }
        self.total_collectibles = 0
        self.total_coins = 0
        self.total_powerups = 0
        
        # Power-up usage totals
        self.total_shields_used = 0
        
        # Averages (calculated)
        self.avg_score = 0.0
        self.avg_play_time = 0.0
        self.avg_platforms_per_run = 0.0
        self.avg_collectibles_per_run = 0.0
    
    def add_run(self, run_stats: RunStatistics):
        """
        Add a run's statistics to all-time totals.
        
        Args:
            run_stats: The run statistics to add
        """
        self.total_runs += 1
        self.total_score += run_stats.score
        self.total_play_time += run_stats.play_time
        self.total_distance += run_stats.distance_traveled
        
        # Update bests
        if run_stats.score > self.best_score:
            self.best_score = run_stats.score
        if run_stats.max_combo > self.best_combo:
            self.best_combo = run_stats.max_combo
        if run_stats.max_multiplier > self.best_multiplier:
            self.best_multiplier = run_stats.max_multiplier
        if run_stats.play_time > self.longest_run_time:
            self.longest_run_time = run_stats.play_time
        if run_stats.distance_traveled > self.furthest_distance:
            self.furthest_distance = run_stats.distance_traveled
        
        # Add jump totals
        self.total_jumps += run_stats.total_jumps
        self.total_single_jumps += run_stats.single_jumps
        self.total_double_jumps += run_stats.double_jumps
        self.total_triple_jumps += run_stats.triple_jumps
        self.total_helicopter_uses += run_stats.helicopter_uses
        self.total_helicopter_time += run_stats.helicopter_time
        
        # Add platform totals
        self.total_platforms_landed += run_stats.total_platforms_landed
        for ptype, count in run_stats.platforms_landed.items():
            if ptype in self.total_platforms_by_type:
                self.total_platforms_by_type[ptype] += count
        
        # Add collectible totals
        self.total_collectibles += run_stats.total_collectibles
        self.total_coins += run_stats.coins_collected
        self.total_powerups += run_stats.powerups_collected
        for ctype, count in run_stats.collectibles_gathered.items():
            if ctype in self.total_collectibles_by_type:
                self.total_collectibles_by_type[ctype] += count
        
        # Add power-up usage
        self.total_shields_used += run_stats.shields_used
        
        # Recalculate averages
        self._calculate_averages()
    
    def _calculate_averages(self):
        """Calculate average statistics."""
        if self.total_runs > 0:
            self.avg_score = self.total_score / self.total_runs
            self.avg_play_time = self.total_play_time / self.total_runs
            self.avg_platforms_per_run = self.total_platforms_landed / self.total_runs
            self.avg_collectibles_per_run = self.total_collectibles / self.total_runs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'total_runs': self.total_runs,
            'total_score': self.total_score,
            'total_play_time': self.total_play_time,
            'total_distance': self.total_distance,
            'best_score': self.best_score,
            'best_combo': self.best_combo,
            'best_multiplier': self.best_multiplier,
            'longest_run_time': self.longest_run_time,
            'furthest_distance': self.furthest_distance,
            'total_jumps': self.total_jumps,
            'total_single_jumps': self.total_single_jumps,
            'total_double_jumps': self.total_double_jumps,
            'total_triple_jumps': self.total_triple_jumps,
            'total_helicopter_uses': self.total_helicopter_uses,
            'total_helicopter_time': self.total_helicopter_time,
            'total_platforms_by_type': self.total_platforms_by_type.copy(),
            'total_platforms_landed': self.total_platforms_landed,
            'total_collectibles_by_type': self.total_collectibles_by_type.copy(),
            'total_collectibles': self.total_collectibles,
            'total_coins': self.total_coins,
            'total_powerups': self.total_powerups,
            'total_shields_used': self.total_shields_used,
            'avg_score': self.avg_score,
            'avg_play_time': self.avg_play_time,
            'avg_platforms_per_run': self.avg_platforms_per_run,
            'avg_collectibles_per_run': self.avg_collectibles_per_run
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AllTimeStatistics':
        """Create AllTimeStatistics from dictionary."""
        stats = AllTimeStatistics()
        stats.total_runs = data.get('total_runs', 0)
        stats.total_score = data.get('total_score', 0)
        stats.total_play_time = data.get('total_play_time', 0.0)
        stats.total_distance = data.get('total_distance', 0)
        stats.best_score = data.get('best_score', 0)
        stats.best_combo = data.get('best_combo', 0)
        stats.best_multiplier = data.get('best_multiplier', 1)
        stats.longest_run_time = data.get('longest_run_time', 0.0)
        stats.furthest_distance = data.get('furthest_distance', 0)
        stats.total_jumps = data.get('total_jumps', 0)
        stats.total_single_jumps = data.get('total_single_jumps', 0)
        stats.total_double_jumps = data.get('total_double_jumps', 0)
        stats.total_triple_jumps = data.get('total_triple_jumps', 0)
        stats.total_helicopter_uses = data.get('total_helicopter_uses', 0)
        stats.total_helicopter_time = data.get('total_helicopter_time', 0.0)
        stats.total_platforms_by_type = data.get('total_platforms_by_type', stats.total_platforms_by_type)
        stats.total_platforms_landed = data.get('total_platforms_landed', 0)
        stats.total_collectibles_by_type = data.get('total_collectibles_by_type', stats.total_collectibles_by_type)
        stats.total_collectibles = data.get('total_collectibles', 0)
        stats.total_coins = data.get('total_coins', 0)
        stats.total_powerups = data.get('total_powerups', 0)
        stats.total_shields_used = data.get('total_shields_used', 0)
        stats.avg_score = data.get('avg_score', 0.0)
        stats.avg_play_time = data.get('avg_play_time', 0.0)
        stats.avg_platforms_per_run = data.get('avg_platforms_per_run', 0.0)
        stats.avg_collectibles_per_run = data.get('avg_collectibles_per_run', 0.0)
        return stats


def format_time(seconds: float) -> str:
    """
    Format seconds into a readable time string.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted string like "1m 23s" or "45s"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_number(num: int) -> str:
    """
    Format large numbers with commas.
    
    Args:
        num: Number to format
    
    Returns:
        Formatted string like "1,234,567"
    """
    return f"{num:,}"


def format_distance(pixels: int) -> str:
    """
    Format distance in a readable way.
    
    Args:
        pixels: Distance in pixels
    
    Returns:
        Formatted string like "1.2km" or "500m"
    """
    # Assume 100 pixels = 1 meter for game purposes
    meters = pixels / 100
    if meters < 1000:
        return f"{int(meters)}m"
    else:
        km = meters / 1000
        return f"{km:.1f}km"


def get_platform_display_name(platform_type: str) -> str:
    """
    Get display name for a platform type.
    
    Args:
        platform_type: Internal platform type name
    
    Returns:
        Human-readable display name
    """
    names = {
        'static': 'Normal',
        'moving': 'Moving',
        'small': 'Small',
        'crumbling': 'Crumbling',
        'bouncy': 'Bouncy',
        'ice': 'Ice',
        'conveyor': 'Conveyor',
        'disappearing': 'Disappearing',
        'spring': 'Spring'
    }
    return names.get(platform_type, platform_type.title())


def get_collectible_display_name(collectible_type: str) -> str:
    """
    Get display name for a collectible type.
    
    Args:
        collectible_type: Internal collectible type name
    
    Returns:
        Human-readable display name
    """
    names = {
        'coin': 'Coins',
        'speed_boost': 'Speed Boost',
        'shield': 'Shield',
        'magnet': 'Magnet',
        'double_points': 'Double Points',
        'extra_jump': 'Extra Jump'
    }
    return names.get(collectible_type, collectible_type.replace('_', ' ').title())


def get_platform_color(platform_type: str) -> tuple:
    """
    Get display color for a platform type.
    
    Args:
        platform_type: Internal platform type name
    
    Returns:
        RGB color tuple
    """
    colors = {
        'static': (100, 180, 100),  # Green
        'moving': (100, 100, 200),  # Blue
        'small': (200, 100, 100),   # Red
        'crumbling': (150, 100, 50),  # Brown
        'bouncy': (255, 165, 0),    # Orange
        'ice': (173, 216, 230),     # Light blue
        'conveyor': (139, 69, 19),  # Brown
        'disappearing': (200, 200, 200),  # Gray
        'spring': (50, 205, 50)     # Lime green
    }
    return colors.get(platform_type, (150, 150, 150))


def get_collectible_color(collectible_type: str) -> tuple:
    """
    Get display color for a collectible type.
    
    Args:
        collectible_type: Internal collectible type name
    
    Returns:
        RGB color tuple
    """
    colors = {
        'coin': (255, 215, 0),      # Gold
        'speed_boost': (0, 255, 255),  # Cyan
        'shield': (100, 200, 255),  # Light blue
        'magnet': (255, 0, 255),    # Magenta
        'double_points': (255, 165, 0),  # Orange
        'extra_jump': (50, 255, 50)  # Bright green
    }
    return colors.get(collectible_type, (200, 200, 200))