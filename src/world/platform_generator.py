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
        self.score = 0
        
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
        # Set last_platform_x to the end of the first platform (accounting for scale)
        self.last_platform_x = 200 * PLATFORM_SCALE
        
        # Generate initial set of platforms
        for _ in range(10):
            self._generate_next_platform()
    
    def update(self, camera_x, difficulty, score=0):
        """
        Update platform generation based on camera position.
        
        Args:
            camera_x: Camera X position in world space
            difficulty: Current difficulty level (1.0 - 3.0)
            score: Current player score
        """
        self.difficulty = difficulty
        self.score = score
        
        # Remove off-screen platforms (return to pool)
        new_platforms = []
        for p in self.platforms:
            if p.position.x + p.width > camera_x - 200:
                new_platforms.append(p)
            else:
                # Deactivate platform when removing it
                p.active = False
        self.platforms = new_platforms
        
        # Generate new platforms ahead of camera
        while self.last_platform_x < camera_x + PLATFORM_SPAWN_DISTANCE:
            self._generate_next_platform()
        
        # Update platform behaviors
        for platform in self.platforms:
            platform.update(1.0 / FPS)
    
    def _generate_next_platform(self):
        """Generate the next platform in the sequence."""
        # Calculate gap based on difficulty
        min_gap = MIN_GAP
        max_gap = MAX_GAP_BASE + (self.difficulty * GAP_INCREASE_PER_DIFFICULTY)
        
        # Calculate jump distances for different abilities
        single_jump_distance = calculate_jump_distance(
            PLAYER_RUN_SPEED, JUMP_VELOCITY, GRAVITY
        )
        
        # Double jump adds extra distance from speed boost
        double_jump_distance = calculate_jump_distance(
            PLAYER_RUN_SPEED + DOUBLE_JUMP_SPEED_BOOST, DOUBLE_JUMP_VELOCITY, GRAVITY
        )
        
        # Helicopter adds glide distance
        helicopter_distance = PLAYER_RUN_SPEED * HELICOPTER_DURATION
        max_reachable = single_jump_distance + helicopter_distance
        
        # Ensure max gap doesn't exceed what's possible with helicopter
        max_gap = min(max_gap, max_reachable * 0.85)
        
        # Create three distinct jump types with variety
        roll = random.random()
        
        if roll < 0.35:
            # Easy jump - single jump only (35% of platforms)
            gap = random.uniform(min_gap, single_jump_distance * 0.65)
        elif roll < 0.65:
            # Medium jump - requires double jump (30% of platforms)
            # Gap is beyond single jump but within double jump range
            gap = random.uniform(single_jump_distance * 0.70, double_jump_distance * 0.80)
        else:
            # Hard jump - requires helicopter (35% of platforms)
            # Gap is beyond double jump, needs helicopter glide
            gap = random.uniform(double_jump_distance * 0.85, max_gap)
        
        # Height variation - create dramatic vertical gameplay
        # Calculate max vertical reach with single jump + helicopter
        # Using physics: max_height = v²/(2g) where v is jump velocity
        max_jump_height = (JUMP_VELOCITY * JUMP_VELOCITY) / (2 * GRAVITY)
        
        # Create much more dramatic height variation
        # Positive height_diff = platform is lower (easier)
        # Negative height_diff = platform is higher (harder)
        # Increased range from 0.3/0.5 to 0.8/1.2 for more variety
        height_diff = random.uniform(-max_jump_height * 0.8, max_jump_height * 1.2)
        y = self.last_platform_y + height_diff
        
        # Clamp Y position to keep platforms on screen and above water
        # Expanded range: 100 (higher up) to WATER_LEVEL - 100 (lower down)
        y = max(100, min(WATER_LEVEL - 100, y))
        
        # Choose platform type based on difficulty AND height
        # Pass the Y position to influence platform type selection
        platform_type = self._choose_platform_type(y)
        
        # Determine platform width
        if platform_type == PlatformType.SMALL:
            width = SMALL_PLATFORM_WIDTH
        elif platform_type == PlatformType.CONVEYOR:
            # Conveyor platforms are always significantly larger
            width = MAX_PLATFORM_WIDTH + 80  # Extra wide conveyor belt
        else:
            width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        
        # Create platform
        x = self.last_platform_x + gap
        platform = self._get_platform_from_pool()
        platform.reset(x, y, width, PLATFORM_HEIGHT, platform_type)
        
        self.platforms.append(platform)
        self.last_platform_x = x + (width * PLATFORM_SCALE)
        self.last_platform_y = y
    
    def _choose_platform_type(self, y_position):
        """
        Select platform type based on score and height.
        Lower platforms have higher chance of being bouncy/spring to help recovery.
        
        Args:
            y_position: Y coordinate of the platform
        
        Returns:
            PlatformType enum value
        """
        # Calculate how low the platform is (0.0 = top, 1.0 = bottom)
        # Lower platforms (closer to water) get more bouncy platforms
        height_ratio = (y_position - 100) / (WATER_LEVEL - 200)
        height_ratio = max(0.0, min(1.0, height_ratio))
        
        # Early game (score < 200): only static, moving, small, and bouncy platforms
        if self.score < 200:
            roll = random.random()
            
            # Increase bouncy platform chance at lower heights
            bouncy_threshold = 0.70 + (height_ratio * 0.15)  # 70-85% based on height
            
            if roll < bouncy_threshold:
                return PlatformType.STATIC
            elif roll < 0.90:
                return PlatformType.MOVING
            elif roll < 0.95:
                return PlatformType.SMALL
            else:
                # More bouncy platforms at lower heights
                return PlatformType.BOUNCY
        
        # Score 200+: introduce all special platform types
        roll = random.random()
        
        # Dramatically increase bouncy/spring platform chance at lower heights
        # At bottom (height_ratio = 1.0): 50% chance of bouncy/spring
        # At top (height_ratio = 0.0): normal distribution
        bouncy_boost = height_ratio * 0.35  # Up to 35% boost for bouncy platforms
        
        # Adjust thresholds based on height
        static_threshold = 0.40 - bouncy_boost
        moving_threshold = static_threshold + 0.12
        small_threshold = moving_threshold + 0.10
        bouncy_threshold = small_threshold + 0.08 + (bouncy_boost * 0.5)
        spring_threshold = bouncy_threshold + 0.05 + (bouncy_boost * 0.5)
        ice_threshold = spring_threshold + 0.07
        conveyor_threshold = ice_threshold + 0.07
        crumbling_threshold = conveyor_threshold + 0.06
        disappearing_threshold = crumbling_threshold + 0.05
        
        if roll < static_threshold:
            return PlatformType.STATIC
        elif roll < moving_threshold:
            return PlatformType.MOVING
        elif roll < small_threshold:
            return PlatformType.SMALL
        elif roll < bouncy_threshold:
            return PlatformType.BOUNCY
        elif roll < spring_threshold:
            return PlatformType.SPRING
        elif roll < ice_threshold:
            return PlatformType.ICE
        elif roll < conveyor_threshold:
            return PlatformType.CONVEYOR
        elif roll < crumbling_threshold:
            return PlatformType.CRUMBLING
        elif roll < disappearing_threshold:
            return PlatformType.DISAPPEARING
        else:
            # Default to bouncy at very low heights
            if height_ratio > 0.7:
                return PlatformType.BOUNCY
            return PlatformType.SPRING
    
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
        # Deactivate all platforms in the pool
        for platform in self.platform_pool:
            platform.active = False
        
        self.platforms = []
        self.last_platform_x = 0
        self.last_platform_y = SCREEN_HEIGHT - 200
        self.difficulty = 1.0