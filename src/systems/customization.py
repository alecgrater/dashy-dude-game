"""
Customization system for player appearance, platforms, and backgrounds.
Includes unlock system based on high scores.
"""
from enum import Enum
from typing import Dict, Tuple


class PlayerTheme(Enum):
    """Available player color schemes."""
    CLASSIC = "classic"  # Red (default)
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    GOLD = "gold"
    RAINBOW = "rainbow"


class PlatformTheme(Enum):
    """Available platform themes."""
    GRASS = "grass"  # Default
    WOOD = "wood"
    METAL = "metal"
    CRYSTAL = "crystal"
    LAVA = "lava"
    ICE = "ice"


class BackgroundTheme(Enum):
    """Available background themes."""
    OCEAN = "ocean"  # Default
    DESERT = "desert"
    SPACE = "space"
    SUNSET = "sunset"
    NIGHT = "night"
    FOREST = "forest"


class ThemeColors:
    """
    Color definitions for all themes.
    Each theme returns a dictionary of color names to RGB tuples.
    """
    
    # Player color schemes
    PLAYER_THEMES = {
        PlayerTheme.CLASSIC: {
            'primary': (231, 76, 60),      # Red
            'secondary': (192, 57, 43),    # Dark red
            'accent': (255, 255, 255),     # White
            'outline': (0, 0, 0),          # Black
        },
        PlayerTheme.BLUE: {
            'primary': (52, 152, 219),     # Blue
            'secondary': (41, 128, 185),   # Dark blue
            'accent': (255, 255, 255),     # White
            'outline': (0, 0, 0),          # Black
        },
        PlayerTheme.GREEN: {
            'primary': (46, 204, 113),     # Green
            'secondary': (39, 174, 96),    # Dark green
            'accent': (255, 255, 255),     # White
            'outline': (0, 0, 0),          # Black
        },
        PlayerTheme.PURPLE: {
            'primary': (155, 89, 182),     # Purple
            'secondary': (142, 68, 173),   # Dark purple
            'accent': (255, 255, 255),     # White
            'outline': (0, 0, 0),          # Black
        },
        PlayerTheme.GOLD: {
            'primary': (241, 196, 15),     # Gold
            'secondary': (243, 156, 18),   # Orange
            'accent': (255, 255, 255),     # White
            'outline': (0, 0, 0),          # Black
        },
        PlayerTheme.RAINBOW: {
            'primary': (255, 105, 180),    # Hot pink
            'secondary': (138, 43, 226),   # Blue violet
            'accent': (255, 255, 0),       # Yellow
            'outline': (0, 0, 0),          # Black
        },
    }
    
    # Platform themes
    PLATFORM_THEMES = {
        PlatformTheme.GRASS: {
            'base': (52, 73, 94),          # Dark gray
            'highlight': (127, 140, 141),  # Light gray
            'top': (46, 204, 113),         # Green
            'moving': (155, 89, 182),      # Purple
            'small': (241, 196, 15),       # Yellow
            'crumbling': (231, 76, 60),    # Red
        },
        PlatformTheme.WOOD: {
            'base': (101, 67, 33),         # Brown
            'highlight': (139, 90, 43),    # Light brown
            'top': (160, 82, 45),          # Sienna
            'moving': (139, 69, 19),       # Saddle brown
            'small': (210, 105, 30),       # Chocolate
            'crumbling': (139, 0, 0),      # Dark red
        },
        PlatformTheme.METAL: {
            'base': (96, 96, 96),          # Dark gray
            'highlight': (192, 192, 192),  # Silver
            'top': (169, 169, 169),        # Dark gray
            'moving': (128, 128, 128),     # Gray
            'small': (255, 215, 0),        # Gold
            'crumbling': (178, 34, 34),    # Firebrick
        },
        PlatformTheme.CRYSTAL: {
            'base': (147, 112, 219),       # Medium purple
            'highlight': (216, 191, 216),  # Thistle
            'top': (186, 85, 211),         # Medium orchid
            'moving': (138, 43, 226),      # Blue violet
            'small': (218, 112, 214),      # Orchid
            'crumbling': (199, 21, 133),   # Medium violet red
        },
        PlatformTheme.LAVA: {
            'base': (64, 0, 0),            # Dark red
            'highlight': (255, 69, 0),     # Orange red
            'top': (255, 140, 0),          # Dark orange
            'moving': (255, 0, 0),         # Red
            'small': (255, 215, 0),        # Gold
            'crumbling': (139, 0, 0),      # Dark red
        },
        PlatformTheme.ICE: {
            'base': (176, 224, 230),       # Powder blue
            'highlight': (240, 248, 255),  # Alice blue
            'top': (135, 206, 250),        # Light sky blue
            'moving': (100, 149, 237),     # Cornflower blue
            'small': (173, 216, 230),      # Light blue
            'crumbling': (70, 130, 180),   # Steel blue
        },
    }
    
    # Background themes
    BACKGROUND_THEMES = {
        BackgroundTheme.OCEAN: {
            'sky_top': (135, 206, 235),    # Light blue
            'sky_bottom': (255, 228, 181), # Peach
            'water_dark': (41, 128, 185),  # Deep blue
            'water_light': (52, 152, 219), # Light blue
        },
        BackgroundTheme.DESERT: {
            'sky_top': (255, 218, 185),    # Peach puff
            'sky_bottom': (255, 160, 122), # Light salmon
            'water_dark': (210, 180, 140), # Tan (sand)
            'water_light': (244, 164, 96), # Sandy brown
        },
        BackgroundTheme.SPACE: {
            'sky_top': (25, 25, 112),      # Midnight blue
            'sky_bottom': (72, 61, 139),   # Dark slate blue
            'water_dark': (0, 0, 0),       # Black
            'water_light': (75, 0, 130),   # Indigo
        },
        BackgroundTheme.SUNSET: {
            'sky_top': (255, 140, 0),      # Dark orange
            'sky_bottom': (255, 20, 147),  # Deep pink
            'water_dark': (138, 43, 226),  # Blue violet
            'water_light': (186, 85, 211), # Medium orchid
        },
        BackgroundTheme.NIGHT: {
            'sky_top': (25, 25, 112),      # Midnight blue
            'sky_bottom': (72, 61, 139),   # Dark slate blue
            'water_dark': (0, 0, 139),     # Dark blue
            'water_light': (65, 105, 225), # Royal blue
        },
        BackgroundTheme.FOREST: {
            'sky_top': (135, 206, 235),    # Sky blue
            'sky_bottom': (144, 238, 144), # Light green
            'water_dark': (34, 139, 34),   # Forest green
            'water_light': (50, 205, 50),  # Lime green
        },
    }


class CustomizationSystem:
    """
    Manages player customization choices and unlock progression.
    """
    
    # Unlock requirements (high score needed)
    UNLOCK_REQUIREMENTS = {
        # Player themes
        PlayerTheme.CLASSIC: 0,      # Default, always unlocked
        PlayerTheme.BLUE: 100,
        PlayerTheme.GREEN: 250,
        PlayerTheme.PURPLE: 500,
        PlayerTheme.GOLD: 1000,
        PlayerTheme.RAINBOW: 2000,
        
        # Platform themes
        PlatformTheme.GRASS: 0,      # Default, always unlocked
        PlatformTheme.WOOD: 150,
        PlatformTheme.METAL: 300,
        PlatformTheme.CRYSTAL: 600,
        PlatformTheme.LAVA: 1200,
        PlatformTheme.ICE: 1500,
        
        # Background themes
        BackgroundTheme.OCEAN: 0,    # Default, always unlocked
        BackgroundTheme.DESERT: 200,
        BackgroundTheme.SPACE: 400,
        BackgroundTheme.SUNSET: 800,
        BackgroundTheme.NIGHT: 1000,
        BackgroundTheme.FOREST: 1800,
    }
    
    def __init__(self):
        """Initialize customization system with defaults."""
        self.player_theme = PlayerTheme.CLASSIC
        self.platform_theme = PlatformTheme.GRASS
        self.background_theme = BackgroundTheme.OCEAN
        self.high_score = 0
    
    def set_high_score(self, score: int):
        """Update high score for unlock checking."""
        self.high_score = score
    
    def is_unlocked(self, theme) -> bool:
        """
        Check if a theme is unlocked.
        
        Args:
            theme: PlayerTheme, PlatformTheme, or BackgroundTheme
        
        Returns:
            True if unlocked
        """
        required_score = self.UNLOCK_REQUIREMENTS.get(theme, 0)
        return self.high_score >= required_score
    
    def get_unlock_score(self, theme) -> int:
        """Get the score required to unlock a theme."""
        return self.UNLOCK_REQUIREMENTS.get(theme, 0)
    
    def set_player_theme(self, theme: PlayerTheme) -> bool:
        """
        Set player theme if unlocked.
        
        Returns:
            True if theme was set successfully
        """
        if self.is_unlocked(theme):
            self.player_theme = theme
            return True
        return False
    
    def set_platform_theme(self, theme: PlatformTheme) -> bool:
        """
        Set platform theme if unlocked.
        
        Returns:
            True if theme was set successfully
        """
        if self.is_unlocked(theme):
            self.platform_theme = theme
            return True
        return False
    
    def set_background_theme(self, theme: BackgroundTheme) -> bool:
        """
        Set background theme if unlocked.
        
        Returns:
            True if theme was set successfully
        """
        if self.is_unlocked(theme):
            self.background_theme = theme
            return True
        return False
    
    def get_player_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get current player color scheme."""
        return ThemeColors.PLAYER_THEMES[self.player_theme]
    
    def get_platform_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get current platform color scheme."""
        return ThemeColors.PLATFORM_THEMES[self.platform_theme]
    
    def get_background_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get current background color scheme."""
        return ThemeColors.BACKGROUND_THEMES[self.background_theme]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        return {
            'player_theme': self.player_theme.value,
            'platform_theme': self.platform_theme.value,
            'background_theme': self.background_theme.value,
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary."""
        try:
            self.player_theme = PlayerTheme(data.get('player_theme', 'classic'))
            self.platform_theme = PlatformTheme(data.get('platform_theme', 'grass'))
            self.background_theme = BackgroundTheme(data.get('background_theme', 'ocean'))
        except (ValueError, KeyError):
            # Reset to defaults if invalid data
            self.player_theme = PlayerTheme.CLASSIC
            self.platform_theme = PlatformTheme.GRASS
            self.background_theme = BackgroundTheme.OCEAN
    
    def get_all_unlocked_themes(self) -> Dict[str, list]:
        """
        Get all unlocked themes organized by category.
        
        Returns:
            Dictionary with 'player', 'platform', and 'background' lists
        """
        return {
            'player': [theme for theme in PlayerTheme if self.is_unlocked(theme)],
            'platform': [theme for theme in PlatformTheme if self.is_unlocked(theme)],
            'background': [theme for theme in BackgroundTheme if self.is_unlocked(theme)],
        }