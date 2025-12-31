"""
Game constants and configuration values.
All measurements in pixels unless otherwise specified.
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FIXED_DT = 1.0 / FPS  # Fixed timestep for physics

# Physics constants
GRAVITY = 2000.0  # pixels/second²
MAX_FALL_SPEED = 1000.0  # pixels/second
TERMINAL_VELOCITY = 1200.0  # pixels/second

# Player settings
PLAYER_WIDTH = 32  # Base sprite size
PLAYER_HEIGHT = 32
PLAYER_SCALE = 2  # Display scale (64x64 on screen)
PLAYER_RUN_SPEED = 400.0  # pixels/second
PLAYER_COLLISION_WIDTH = 28  # Slightly smaller for better feel
PLAYER_COLLISION_HEIGHT = 30

# Jump mechanics
JUMP_VELOCITY = -600.0  # pixels/second (negative = up)
DOUBLE_JUMP_VELOCITY = -550.0
DOUBLE_JUMP_SPEED_BOOST = 200.0  # Extra forward speed on double jump
DOUBLE_JUMP_BOOST_DURATION = 0.5  # How long the boost lasts (seconds)
HELICOPTER_FALL_SPEED = 100.0  # Slow fall during glide
HELICOPTER_DURATION = 1.5  # seconds
VARIABLE_JUMP_MULTIPLIER = 0.5  # Velocity multiplier when releasing jump early

# Advanced mechanics
COYOTE_TIME = 0.1  # Grace period after leaving platform (seconds)
JUMP_BUFFER_TIME = 0.15  # Input buffer before landing (seconds)

# Platform settings
PLATFORM_HEIGHT = 16  # Base height
PLATFORM_SCALE = 2  # Display scale
MIN_PLATFORM_WIDTH = 65  # Balanced between original 80 and 50
MAX_PLATFORM_WIDTH = 150  # Balanced between original 200 and 120
SMALL_PLATFORM_WIDTH = 50  # Balanced between original 60 and 40
PLATFORM_SPAWN_DISTANCE = 1500  # Distance ahead to spawn platforms

# Platform generation
MIN_GAP = 120  # Increased from 100 for more challenge
MAX_GAP_BASE = 250  # Increased from 200 for more challenge
GAP_INCREASE_PER_DIFFICULTY = 60  # Increased from 50 for more challenge

# Difficulty progression
BASE_GAME_SPEED = 300.0  # pixels/second
MAX_GAME_SPEED = 600.0
SPEED_INCREASE_INTERVAL = 10.0  # seconds
SPEED_INCREASE_AMOUNT = 20.0  # pixels/second per interval
CRUMBLING_PLATFORM_START_TIME = 30.0  # seconds

# Camera settings
CAMERA_SMOOTHING = 0.1  # Lerp factor (0-1, lower = smoother)
CAMERA_PLAYER_OFFSET_X = 0.3  # Player position as ratio of screen width
CAMERA_LOOK_AHEAD = 100  # Extra pixels to look ahead
CAMERA_VERTICAL_DEADZONE = 200  # Vertical pixels before camera moves

# Screen shake
SHAKE_LANDING_AMOUNT = 5.0  # pixels
SHAKE_LANDING_DURATION = 0.1  # seconds
SHAKE_DEATH_AMOUNT = 10.0
SHAKE_DEATH_DURATION = 0.3

# Animation settings
IDLE_FPS = 8
RUN_FPS = 12
JUMP_FPS = 10
DOUBLE_JUMP_FPS = 15
HELICOPTER_FPS = 16

# Particle settings
PARTICLE_LIFETIME = 0.5  # seconds
MAX_PARTICLES = 50
JUMP_PARTICLE_COUNT = 5
LANDING_PARTICLE_COUNT = 8
HELICOPTER_PARTICLE_INTERVAL = 0.05  # seconds between particles

# UI settings
UI_PADDING = 20
SCORE_FONT_SIZE = 48
TITLE_FONT_SIZE = 72
BUTTON_FONT_SIZE = 36
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
BUTTON_HOVER_SCALE = 1.1

# Scoring
SCORE_PER_PLATFORM = 10
COMBO_MULTIPLIER = 1.5
COMBO_TIMEOUT = 2.0  # seconds without landing to reset combo

# Water settings
WATER_LEVEL = SCREEN_HEIGHT - 100  # Y position of water surface
WATER_WAVE_AMPLITUDE = 5  # pixels
WATER_WAVE_FREQUENCY = 2.0  # Hz

# Color palette (RGB tuples)
# Sky gradient
SKY_TOP = (135, 206, 235)  # Light blue
SKY_BOTTOM = (255, 228, 181)  # Peach

# Water
WATER_DARK = (41, 128, 185)  # Deep blue
WATER_LIGHT = (52, 152, 219)  # Light blue
WATER_FOAM = (236, 240, 241)  # White foam

# Platforms
PLATFORM_BASE = (52, 73, 94)  # Dark gray
PLATFORM_HIGHLIGHT = (127, 140, 141)  # Light gray
PLATFORM_GRASS = (46, 204, 113)  # Green top
PLATFORM_MOVING = (155, 89, 182)  # Purple tint
PLATFORM_SMALL = (241, 196, 15)  # Yellow tint
PLATFORM_CRUMBLING = (231, 76, 60)  # Red tint

# Player colors
PLAYER_PRIMARY = (231, 76, 60)  # Red
PLAYER_SECONDARY = (192, 57, 43)  # Dark red
PLAYER_ACCENT = (255, 255, 255)  # White
PLAYER_OUTLINE = (0, 0, 0)  # Black

# UI colors
UI_PRIMARY = (44, 62, 80)  # Dark blue-gray
UI_SECONDARY = (52, 73, 94)  # Medium blue-gray
UI_ACCENT = (52, 152, 219)  # Bright blue
UI_TEXT = (236, 240, 241)  # Off-white
UI_TEXT_SHADOW = (0, 0, 0)  # Black

# Particle colors
PARTICLE_DUST = (189, 195, 199)  # Light gray
PARTICLE_HELICOPTER = (52, 152, 219)  # Blue
PARTICLE_SPLASH = (52, 152, 219)  # Blue

# Cloud colors
CLOUD_COLOR = (255, 255, 255, 180)  # White with alpha

# Audio settings
AUDIO_SAMPLE_RATE = 22050
AUDIO_CHANNELS = 2
AUDIO_BUFFER_SIZE = 512
AUDIO_VOLUME = 0.7

# Sound frequencies (Hz)
JUMP_FREQ_START = 200
JUMP_FREQ_END = 400
DOUBLE_JUMP_FREQ_START = 400
DOUBLE_JUMP_FREQ_END = 600
HELICOPTER_FREQ = 150
LANDING_FREQ = 100
DEATH_FREQ_START = 400
DEATH_FREQ_END = 100

# Sound durations (seconds)
JUMP_SOUND_DURATION = 0.1
DOUBLE_JUMP_SOUND_DURATION = 0.15
LANDING_SOUND_DURATION = 0.05
DEATH_SOUND_DURATION = 0.3