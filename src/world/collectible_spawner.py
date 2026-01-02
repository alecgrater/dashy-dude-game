"""
Collectible spawning system.
"""
import random
from src.entities.collectible import Collectible, CollectibleType
from src.utils.math_utils import Vector2


class CollectibleSpawner:
    """
    Manages spawning of collectibles:
    - Spawns collectibles near platforms
    - Controls spawn rates based on difficulty
    - Manages collectible types and rarity
    """
    
    # Spawn chances (out of 100) for each type
    SPAWN_CHANCES = {
        CollectibleType.COIN: 60,  # Common
        CollectibleType.SPEED_BOOST: 10,  # Uncommon
        CollectibleType.SHIELD: 8,  # Uncommon
        CollectibleType.MAGNET: 8,  # Uncommon
        CollectibleType.DOUBLE_POINTS: 7,  # Rare
        CollectibleType.EXTRA_JUMP: 7,  # Rare
    }
    
    def __init__(self):
        """Initialize collectible spawner."""
        self.collectibles = []
        self.spawn_distance = 1500  # Distance ahead to spawn
        self.last_spawn_x = 0
        self.min_spawn_interval = 200  # Minimum pixels between spawns
        
        # Spawn rates (chance per platform) - REDUCED for performance
        self.coin_spawn_chance = 0.25  # Reduced from 0.4 (25% instead of 40%)
        self.powerup_spawn_chance = 0.10  # Reduced from 0.15 (10% instead of 15%)
        
        # Performance limits
        self.max_active_collectibles = 40  # Hard limit on active collectibles
        self.max_visible_collectibles = 30  # Limit visible on screen at once
        
        # Power-up limiting: only 1 non-coin power-up visible at a time
        self.active_powerup_type = None  # Currently active non-coin type
        self.has_active_powerup = False  # Whether a non-coin power-up exists
        
        # Difficulty scaling
        self.difficulty_multiplier = 1.0
    
    def update(self, dt, camera_x, platforms, player_pos, magnet_active):
        """
        Update collectibles and spawn new ones.
        
        Args:
            dt: Delta time in seconds
            camera_x: Camera X position
            platforms: List of platform objects
            player_pos: Player position Vector2
            magnet_active: Whether magnet power-up is active
        """
        # Update existing collectibles
        for collectible in self.collectibles[:]:
            collectible.update(dt, player_pos, magnet_active)
            
            # Remove collectibles that are too far behind camera
            if collectible.position.x < camera_x - 200:
                self.collectibles.remove(collectible)
            elif not collectible.alive:
                self.collectibles.remove(collectible)
        
        # Update power-up tracking
        self._update_powerup_tracking()
        
        # Check if we're at the collectible limit
        active_count = sum(1 for c in self.collectibles if not c.collected)
        if active_count >= self.max_active_collectibles:
            return  # Don't spawn more if at limit
        
        # Spawn new collectibles near platforms
        spawn_x = camera_x + self.spawn_distance
        
        for platform in platforms:
            # Check if platform is in spawn range and we haven't spawned here yet
            if (platform.position.x > self.last_spawn_x and
                platform.position.x < spawn_x and
                platform.position.x > camera_x):
                
                # Check limit again before spawning
                active_count = sum(1 for c in self.collectibles if not c.collected)
                if active_count >= self.max_active_collectibles:
                    break  # Stop spawning if at limit
                
                # Try to spawn collectible above this platform
                if random.random() < self.coin_spawn_chance * self.difficulty_multiplier:
                    self._spawn_collectible_above_platform(platform, prefer_coin=True)
                elif random.random() < self.powerup_spawn_chance * self.difficulty_multiplier:
                    # Only spawn power-up if we don't already have one active
                    if not self.has_active_powerup:
                        self._spawn_collectible_above_platform(platform, prefer_coin=False)
                
                self.last_spawn_x = platform.position.x
    
    def _update_powerup_tracking(self):
        """Update tracking of active non-coin power-ups."""
        # Check if any non-coin power-ups exist
        non_coin_collectibles = [c for c in self.collectibles
                                 if not c.collected and c.type != CollectibleType.COIN]
        
        if non_coin_collectibles:
            self.has_active_powerup = True
            self.active_powerup_type = non_coin_collectibles[0].type
        else:
            self.has_active_powerup = False
            self.active_powerup_type = None
    
    def _spawn_collectible_above_platform(self, platform, prefer_coin=True):
        """
        Spawn a collectible above a platform.
        
        Args:
            platform: Platform object to spawn above
            prefer_coin: If True, more likely to spawn coins
        """
        # Determine collectible type
        if prefer_coin:
            collectible_type = self._get_random_collectible_type(coin_bias=True)
        else:
            collectible_type = self._get_random_collectible_type(coin_bias=False)
            
            # If it's not a coin and we already have a power-up, don't spawn
            if collectible_type != CollectibleType.COIN and self.has_active_powerup:
                return
        
        # Position above platform center
        x = platform.position.x + platform.width / 2
        y = platform.position.y - 80  # Hover above platform
        
        # Add some randomness to position
        x += random.uniform(-platform.width / 4, platform.width / 4)
        y += random.uniform(-20, 20)
        
        # Create collectible
        collectible = Collectible(x, y, collectible_type)
        self.collectibles.append(collectible)
        
        # Update power-up tracking if this is a non-coin
        if collectible_type != CollectibleType.COIN:
            self.has_active_powerup = True
            self.active_powerup_type = collectible_type
    
    def _get_random_collectible_type(self, coin_bias=False):
        """
        Get a random collectible type based on spawn chances.
        
        Args:
            coin_bias: If True, heavily favor coins
            
        Returns:
            CollectibleType enum value
        """
        if coin_bias and random.random() < 0.7:  # 70% chance for coin when biased
            return CollectibleType.COIN
        
        # Weighted random selection
        total = sum(self.SPAWN_CHANCES.values())
        rand = random.uniform(0, total)
        
        current = 0
        for collectible_type, chance in self.SPAWN_CHANCES.items():
            current += chance
            if rand <= current:
                return collectible_type
        
        # Fallback to coin
        return CollectibleType.COIN
    
    def spawn_collectible(self, x, y, collectible_type):
        """
        Manually spawn a specific collectible.
        
        Args:
            x: X position
            y: Y position
            collectible_type: CollectibleType enum value
        """
        collectible = Collectible(x, y, collectible_type)
        self.collectibles.append(collectible)
    
    def check_collision(self, player_rect):
        """
        Check if player collides with any collectibles.
        
        Args:
            player_rect: Player collision rectangle
            
        Returns:
            List of collected collectibles
        """
        collected = []
        
        for collectible in self.collectibles[:]:
            if not collectible.collected:
                collectible_rect = collectible.get_collision_rect()
                if player_rect.colliderect(collectible_rect):
                    collectible.collect()
                    collected.append(collectible)
        
        return collected
    
    def set_difficulty(self, difficulty_level):
        """
        Adjust spawn rates based on difficulty.
        
        Args:
            difficulty_level: Difficulty multiplier (1.0 = normal)
        """
        self.difficulty_multiplier = difficulty_level
    
    def clear(self):
        """Clear all collectibles."""
        self.collectibles.clear()
        self.last_spawn_x = 0
    
    def render(self, screen, camera):
        """
        Render all collectibles with culling optimization and visible limit.
        
        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        # Calculate visible area with padding
        from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        cull_padding = 100  # Smaller padding for collectibles
        visible_left = camera.position.x - cull_padding
        visible_right = camera.position.x + SCREEN_WIDTH + cull_padding
        visible_top = camera.position.y - cull_padding
        visible_bottom = camera.position.y + SCREEN_HEIGHT + cull_padding
        
        # Only render collectibles within visible area, with a hard limit
        rendered_count = 0
        for collectible in self.collectibles:
            if not collectible.collected:
                # Stop rendering if we hit the visible limit
                if rendered_count >= self.max_visible_collectibles:
                    break
                
                # Cull collectibles outside visible area
                if (collectible.position.x >= visible_left and
                    collectible.position.x <= visible_right and
                    collectible.position.y >= visible_top and
                    collectible.position.y <= visible_bottom):
                    collectible.render(screen, camera)
                    rendered_count += 1
    
    def get_active_count(self):
        """Get the number of active (uncollected) collectibles."""
        return sum(1 for c in self.collectibles if not c.collected)