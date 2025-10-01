"""
Ball model - represents the ball in the game
"""
import math
import random
import pygame
from config.constants import *

class Ball:
    def __init__(self):
        self.angle = 0  # Current angle around the planet
        self.speed = BALL_SPEED  # Speed in pixels per second
        self.radius_offset = 35  # Distance from planet surface (reduced so ball is closer to players)
        self.direction = 1  # 1 for clockwise, -1 for counterclockwise
        self.spawn_timer = BALL_SPAWN_DELAY  # Time before ball starts moving
        self.is_active = False  # Whether ball is moving
        self.spawn_between_players()
    
    def spawn_between_players(self):
        """Spawn ball at a random position between two players"""
        # Choose random pair of adjacent players (0-1, 1-2, 2-3, or 3-0)
        player_pair = random.randint(0, 3)
        
        # Calculate angle between the two players
        player1_angle = player_pair * (2 * math.pi / 4)
        player2_angle = ((player_pair + 1) % 4) * (2 * math.pi / 4)
        
        # Position ball exactly between the two players
        self.angle = (player1_angle + player2_angle) / 2
        
        # If we're between player 3 and 0, handle the angle wrap-around
        if player_pair == 3:
            self.angle = (player1_angle + (player2_angle + 2 * math.pi)) / 2
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
        
        # Choose random direction
        self.direction = random.choice([-1, 1])
        
        self.is_active = False
        self.spawn_timer = BALL_SPAWN_DELAY
        
    def get_position(self):
        """Get ball position"""
        radius = PLANET_RADIUS + self.radius_offset
        x = PLANET_CENTER[0] + radius * math.cos(self.angle)
        y = PLANET_CENTER[1] + radius * math.sin(self.angle)
        return (x, y)
    
    def reverse_direction(self):
        """Reverse ball direction"""
        self.direction *= -1
    
    def increase_speed(self):
        """Increase ball speed"""
        self.speed *= BALL_ACCELERATION
    
    def reset_speed(self):
        """Reset ball speed to initial value"""
        self.speed = INITIAL_BALL_SPEED
    
    def update(self, dt):
        """Update ball position"""
        if not self.is_active:
            # Count down spawn timer
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.is_active = True
            return
        
        # Calculate angular velocity based on speed
        radius = PLANET_RADIUS + self.radius_offset
        angular_velocity = self.speed / radius
        self.angle += angular_velocity * dt * self.direction
        
        # Keep angle in range [0, 2π]
        if self.angle < 0:
            self.angle += 2 * math.pi
        elif self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi