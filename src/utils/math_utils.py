"""
Mathematical utility functions for game calculations.
"""
import math
import random


def lerp(start, end, t):
    """
    Linear interpolation between start and end.
    
    Args:
        start: Starting value
        end: Ending value
        t: Interpolation factor (0-1)
    
    Returns:
        Interpolated value
    """
    return start + (end - start) * t


def clamp(value, min_val, max_val):
    """
    Clamp value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def ease_in_out_cubic(t):
    """
    Cubic easing function for smooth transitions.
    
    Args:
        t: Time value (0-1)
    
    Returns:
        Eased value (0-1)
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_quad(t):
    """
    Quadratic ease-out function.
    
    Args:
        t: Time value (0-1)
    
    Returns:
        Eased value (0-1)
    """
    return 1 - (1 - t) * (1 - t)


def ease_in_quad(t):
    """
    Quadratic ease-in function.
    
    Args:
        t: Time value (0-1)
    
    Returns:
        Eased value (0-1)
    """
    return t * t


def distance(x1, y1, x2, y2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
    
    Returns:
        Distance between points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def random_range(min_val, max_val):
    """
    Generate random float between min and max.
    
    Args:
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Random float in range
    """
    return random.uniform(min_val, max_val)


def random_int_range(min_val, max_val):
    """
    Generate random integer between min and max (inclusive).
    
    Args:
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Random integer in range
    """
    return random.randint(min_val, max_val)


def sign(value):
    """
    Get the sign of a value.
    
    Args:
        value: Input value
    
    Returns:
        1 if positive, -1 if negative, 0 if zero
    """
    if value > 0:
        return 1
    elif value < 0:
        return -1
    return 0


def approach(current, target, amount):
    """
    Move current value towards target by amount.
    
    Args:
        current: Current value
        target: Target value
        amount: Amount to move (positive)
    
    Returns:
        New value closer to target
    """
    if current < target:
        return min(current + amount, target)
    elif current > target:
        return max(current - amount, target)
    return target


def calculate_jump_distance(horizontal_speed, jump_velocity, gravity):
    """
    Calculate maximum horizontal distance for a jump arc.
    
    Args:
        horizontal_speed: Horizontal movement speed
        jump_velocity: Initial jump velocity (negative for up)
        gravity: Gravity acceleration
    
    Returns:
        Maximum horizontal distance
    """
    # Time to reach peak and fall back down
    time_to_peak = abs(jump_velocity) / gravity
    total_time = time_to_peak * 2
    
    return horizontal_speed * total_time


def point_in_rect(px, py, rx, ry, rw, rh):
    """
    Check if point is inside rectangle.
    
    Args:
        px, py: Point coordinates
        rx, ry: Rectangle top-left coordinates
        rw, rh: Rectangle width and height
    
    Returns:
        True if point is inside rectangle
    """
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def rect_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """
    Check if two rectangles collide (AABB collision).
    
    Args:
        x1, y1, w1, h1: First rectangle
        x2, y2, w2, h2: Second rectangle
    
    Returns:
        True if rectangles overlap
    """
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)


class Vector2:
    """Simple 2D vector class for position and velocity."""
    
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def length(self):
        """Calculate vector magnitude."""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        """Return normalized vector (length 1)."""
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)
    
    def copy(self):
        """Return a copy of this vector."""
        return Vector2(self.x, self.y)
    
    def __repr__(self):
        return f"Vector2({self.x:.2f}, {self.y:.2f})"