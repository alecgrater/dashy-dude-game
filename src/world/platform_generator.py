"""
Procedural platform generation system.
"""
import random
from src.entities.platform import Platform, PlatformType
from src.utils.constants import *
from src.utils.math_utils import calculate_jump_distance


class PlatformGenerator:
    """
    Generates platforms procedurally with difficulty scaling.
    Uses object pooling for performance.
    """
    
    def __init__(self):
        self.platforms = []
        self.platform_pool = [Platform() for _ in range(20)]
        self.last_platform_x = 0
        self.last_platform_y = SCREEN_HEIGHT - 200
        self.difficulty = 1.0
        
        # Calculate maximum jumpable distance
        self.max_jump_distance = self._calculate_max_distance()
    
    def generate_initial_platforms(self):
        """Create starting platforms for game start."""
        self.platforms = []
        self.last_platform_x = 0
        self.last_platform_y = SCREEN_HEIGHT - 200
        
        # Create starting platform
        platform = self._get_platform_from_pool()
        platform.reset(0, self.last_platform_y, 200, PLATFORM_HEIGHT, PlatformType.STATIC)
        self.platforms.append(platform)
        self.last_platform_x = 200
        
        # Generate initial set of platforms
        for _ in range(10):
            self._generate_next_platform()
    
    def update(self, camera_x, difficulty):
        """
        Update platform generation based on camera position.
        
        Args:
            camera_x: Camera X position in world space
            difficulty: Current difficulty level (1.0 - 3.0)
        """
        self.difficulty = difficulty
        
        # Remove off-screen platforms (return to pool)
        self.platforms = [p for p in self.platforms
                         if p.position.x + p.width > camera_x - 200]
        
        # Generate new platforms ahead of camera
        while self.last_platform_x < camera_x + PLATFORM_SPAWN_DISTANCE:
            self._generate_next_platform()
        
        # Update platform behaviors
        for platform in self.platforms:
            platform.update(1.0 / FPS)
    
    def _generate_next_platform(self):
        """Generate the next platform in the sequence."""
        # Calculate gap based on difficulty
        # Make platforms reachable with single jump OR single jump + helicopter
        min_gap = MIN_GAP
        max_gap = MAX_GAP_BASE + (self.difficulty * GAP_INCREASE_PER_DIFFICULTY)
        
        # Calculate single jump distance (without double jump or helicopter)
        single_jump_distance = calculate_jump_distance(
            PLAYER_RUN_SPEED, JUMP_VELOCITY, GRAVITY
        )
        
        # Add helicopter distance for max reachable
        helicopter_distance = PLAYER_RUN_SPEED * HELICOPTER_DURATION
        max_reachable = single_jump_distance + helicopter_distance
        
        # Ensure gap is jumpable - use 70% of max reachable distance
        max_gap = min(max_gap, max_reachable * 0.70)
        
        # Create variety: 60% easy jumps, 40% need helicopter
        if random.random() < 0.6:
            # Easy jump - reachable with single jump only
            gap = random.uniform(min_gap, single_jump_distance * 0.75)
        else:
            # Harder jump - requires helicopter
            gap = random.uniform(single_jump_distance * 0.80, max_gap)
        
        # Choose platform type based on difficulty
        platform_type = self._choose_platform_type()
        
        # Determine platform width
        if platform_type == PlatformType.SMALL:
            width = SMALL_PLATFORM_WIDTH
        else:
            width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        
        # Height variation - keep platforms within reachable vertical range
        # Calculate max vertical reach with single jump + helicopter
        # Using physics: max_height = v²/(2g) where v is jump velocity
        max_jump_height = (JUMP_VELOCITY * JUMP_VELOCITY) / (2 * GRAVITY)
        
        # Allow platforms to be slightly higher or lower, but stay reachable
        # Positive height_diff = platform is lower (easier)
        # Negative height_diff = platform is higher (harder)
        height_diff = random.uniform(-max_jump_height * 0.3, max_jump_height * 0.5)
        y = self.last_platform_y + height_diff
        
        # Clamp Y position to keep platforms on screen and above water
        y = max(150, min(WATER_LEVEL - 150, y))
        
        # Create platform
        x = self.last_platform_x + gap
        platform = self._get_platform_from_pool()
        platform.reset(x, y, width, PLATFORM_HEIGHT, platform_type)
        
        self.platforms.append(platform)
        self.last_platform_x = x + (width * PLATFORM_SCALE)
        self.last_platform_y = y
    
    def _choose_platform_type(self):
        """
        Select platform type based on difficulty.
        
        Returns:
            PlatformType enum value
        """
        # Early game: only static platforms
        if self.difficulty < 1.5:
            return PlatformType.STATIC
        
        roll = random.random()
        
        # Difficulty 1.5-2.5: introduce moving and small
        if self.difficulty < 2.5:
            if roll < 0.75:
                return PlatformType.STATIC
            elif roll < 0.90:
                return PlatformType.MOVING
            else:
                return PlatformType.SMALL
        
        # Difficulty 2.5+: all types including crumbling
        if roll < 0.60:
            return PlatformType.STATIC
        elif roll < 0.75:
            return PlatformType.MOVING
        elif roll < 0.90:
            return PlatformType.SMALL
        else:
            return PlatformType.CRUMBLING
    
    def _get_platform_from_pool(self):
        """
        Get an inactive platform from the pool or create new one.
        
        Returns:
            Platform instance
        """
        for platform in self.platform_pool:
            if not platform.active:
                return platform
        
        # Pool exhausted, create new platform
        new_platform = Platform()
        self.platform_pool.append(new_platform)
        return new_platform
    
    def _calculate_max_distance(self):
        """
        Calculate maximum horizontal distance player can jump.
        Uses single jump + helicopter as the baseline for platform spacing.
        
        Returns:
            Maximum distance in pixels
        """
        # Single jump distance
        single_jump = calculate_jump_distance(
            PLAYER_RUN_SPEED, JUMP_VELOCITY, GRAVITY
        )
        
        # Helicopter adds extra distance
        helicopter_distance = PLAYER_RUN_SPEED * HELICOPTER_DURATION
        
        # Return single jump + helicopter as max
        # (Double jump is available but not required for platform spacing)
        return single_jump + helicopter_distance
    
    def get_platforms(self):
        """
        Get list of active platforms.
        
        Returns:
            List of Platform instances
        """
        return [p for p in self.platforms if p.active]
    
    def reset(self):
        """Reset generator for new game."""
        self.platforms = []
        self.last_platform_x = 0
        self.last_platform_y = SCREEN_HEIGHT - 200
        self.difficulty = 1.0