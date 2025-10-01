"""
Game constants and configuration
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Planet settings
PLANET_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
PLANET_RADIUS = 200

# Player settings
PLAYER_RADIUS = 25  # Made larger so ball can hit them easier
PLAYER_COLORS = [RED, GREEN, BLUE, YELLOW]
HIT_RANGE = 60  # pixels - how close ball must be to hit (adjusted for larger players)
SWING_DURATION = 0.3  # seconds - how long swing animation lasts
HIT_COOLDOWN = 0.5  # seconds - cooldown between hits to prevent spam

# Ball settings
BALL_RADIUS = 10  # Made slightly bigger
BALL_SPEED = 100  # pixels per second
BALL_ACCELERATION = 1.2  # speed multiplier when hit
INITIAL_BALL_SPEED = 100  # reset speed when player eliminated
BALL_SPAWN_DELAY = 3.0  # seconds to wait before ball starts moving