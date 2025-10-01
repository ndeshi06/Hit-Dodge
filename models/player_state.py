"""
Player state enumeration
"""
from enum import Enum

class PlayerState(Enum):
    STANDING = 1
    DODGING = 2
    SWINGING = 3
    ELIMINATED = 4
    FLYING_OFF = 5