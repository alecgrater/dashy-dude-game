"""
Mobile-specific constants and configuration.
These override or extend the base constants for mobile devices.
"""
import os
import sys

# Detect if running on iOS
IS_IOS = sys.platform == 'darwin' and hasattr(sys, 'getandroidapilevel') is False and os.environ.get('KIVY_BUILD', '') == 'ios'

# Mobile screen settings - will be set dynamically based on device
# These are defaults for iPhone 14
MOBILE_SCREEN_WIDTH = 390
MOBILE_SCREEN_HEIGHT = 844
MOBILE_SCALE_FACTOR = 1.0

# Portrait mode (default for mobile)
PORTRAIT_MODE = True

# If landscape mode is preferred for this game:
LANDSCAPE_MODE = True  # Endless runner works better in landscape

# Landscape dimensions (swapped)
if LANDSCAPE_MODE:
    MOBILE_SCREEN_WIDTH = 844
    MOBILE_SCREEN_HEIGHT = 390

# Touch control settings
TOUCH_TAP_THRESHOLD = 0.2  # seconds - taps shorter than this are "taps"
TOUCH_HOLD_THRESHOLD = 0.3  # seconds - holds longer than this activate helicopter
TOUCH_SWIPE_THRESHOLD = 50  # pixels - movement greater than this is a swipe

# Touch zones (as ratios of screen)
# For landscape mode:
TOUCH_ZONE_LEFT = 0.0  # Left edge
TOUCH_ZONE_RIGHT = 1.0  # Right edge
TOUCH_ZONE_JUMP = (0.0, 0.0, 1.0, 1.0)  # Full screen tap to jump

# UI scaling for mobile
MOBILE_UI_SCALE = 1.5  # Scale up UI elements for touch
MOBILE_BUTTON_MIN_SIZE = 44  # Minimum touch target size (Apple HIG)
MOBILE_PADDING = 16  # Safe area padding

# Performance settings for mobile
MOBILE_MAX_PARTICLES = 20  # Reduced particles for battery/performance
MOBILE_PARTICLE_QUALITY = 0.7  # Particle detail level
MOBILE_BACKGROUND_LAYERS = 2  # Reduced parallax layers

# Frame rate
MOBILE_TARGET_FPS = 60
MOBILE_LOW_POWER_FPS = 30  # For low power mode

# Safe area insets (will be set dynamically)
SAFE_AREA_TOP = 47  # iPhone notch area
SAFE_AREA_BOTTOM = 34  # iPhone home indicator
SAFE_AREA_LEFT = 0
SAFE_AREA_RIGHT = 0

# Device-specific configurations
DEVICE_CONFIGS = {
    'iphone_se': {
        'width': 667,
        'height': 375,
        'scale': 2.0,
        'safe_top': 20,
        'safe_bottom': 0,
    },
    'iphone_14': {
        'width': 844,
        'height': 390,
        'scale': 3.0,
        'safe_top': 47,
        'safe_bottom': 34,
    },
    'iphone_14_pro_max': {
        'width': 932,
        'height': 430,
        'scale': 3.0,
        'safe_top': 59,
        'safe_bottom': 34,
    },
    'ipad': {
        'width': 1024,
        'height': 768,
        'scale': 2.0,
        'safe_top': 20,
        'safe_bottom': 0,
    },
    'ipad_pro': {
        'width': 1366,
        'height': 1024,
        'scale': 2.0,
        'safe_top': 20,
        'safe_bottom': 0,
    },
}


def get_device_config(device_name='iphone_14'):
    """Get configuration for a specific device."""
    return DEVICE_CONFIGS.get(device_name, DEVICE_CONFIGS['iphone_14'])


def calculate_scale_factor(screen_width, screen_height, base_width=1280, base_height=720):
    """
    Calculate scale factor to fit base resolution to screen.
    
    Args:
        screen_width: Actual screen width
        screen_height: Actual screen height
        base_width: Base game width (default 1280)
        base_height: Base game height (default 720)
    
    Returns:
        Scale factor to apply to game elements
    """
    width_scale = screen_width / base_width
    height_scale = screen_height / base_height
    
    # Use the smaller scale to ensure everything fits
    return min(width_scale, height_scale)


def get_safe_area_rect(screen_width, screen_height):
    """
    Get the safe area rectangle accounting for notches and home indicators.
    
    Returns:
        Tuple of (x, y, width, height) for the safe area
    """
    x = SAFE_AREA_LEFT
    y = SAFE_AREA_TOP
    width = screen_width - SAFE_AREA_LEFT - SAFE_AREA_RIGHT
    height = screen_height - SAFE_AREA_TOP - SAFE_AREA_BOTTOM
    
    return (x, y, width, height)


# Haptic feedback settings (iOS)
HAPTIC_ENABLED = True
HAPTIC_JUMP = 'light'  # light, medium, heavy
HAPTIC_DOUBLE_JUMP = 'medium'
HAPTIC_LANDING = 'light'
HAPTIC_DEATH = 'heavy'
HAPTIC_ACHIEVEMENT = 'success'  # success, warning, error

# Audio settings for mobile
MOBILE_AUDIO_ENABLED = True
MOBILE_MUSIC_VOLUME = 0.5  # Lower default for mobile
MOBILE_SFX_VOLUME = 0.7

# Battery optimization
LOW_POWER_MODE_ENABLED = True
REDUCE_ANIMATIONS_IN_LOW_POWER = True