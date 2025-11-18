import math
import random
import pygame
from config.constants import *

class Ball:
    def __init__(self):
        self.angle = 0
        self.speed = BALL_SPEED
        self.radius_offset = 35
        self.direction = 1
        self.spawn_timer = BALL_SPAWN_DELAY
        self.is_active = False
        self.x = 0
        self.y = 0
        self.countdown = BALL_SPAWN_DELAY
        self.spawn_between_players()
    
    def spawn_between_players(self):
        player_pair = random.randint(0, 3)
        
        player1_angle = player_pair * (2 * math.pi / 4)
        player2_angle = ((player_pair + 1) % 4) * (2 * math.pi / 4)
        
        self.angle = (player1_angle + player2_angle) / 2
        
        if player_pair == 3:
            self.angle = (player1_angle + (player2_angle + 2 * math.pi)) / 2
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
        
        self.direction = random.choice([-1, 1])
        
        self.is_active = False
        self.spawn_timer = BALL_SPAWN_DELAY
        self.countdown = BALL_SPAWN_DELAY
        
        pos = self.get_position()
        self.x = pos[0]
        self.y = pos[1]
        
    def get_position(self):
        radius = PLANET_RADIUS + self.radius_offset
        x = PLANET_CENTER[0] + radius * math.cos(self.angle)
        y = PLANET_CENTER[1] + radius * math.sin(self.angle)
        return (x, y)
    
    def reverse_direction(self):
        self.direction *= -1
    
    def increase_speed(self):
        self.speed *= BALL_ACCELERATION
    
    def reset_speed(self):
        self.speed = INITIAL_BALL_SPEED
    
    def update(self, dt):
        if not self.is_active:
            self.spawn_timer -= dt
            self.countdown = max(0, self.spawn_timer)
            if self.spawn_timer <= 0:
                self.is_active = True
            pos = self.get_position()
            self.x = pos[0]
            self.y = pos[1]
            return
        
        radius = PLANET_RADIUS + self.radius_offset
        angular_velocity = self.speed / radius
        self.angle += angular_velocity * dt * self.direction
        
        if self.angle < 0:
            self.angle += 2 * math.pi
        elif self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        
        pos = self.get_position()
        self.x = pos[0]
        self.y = pos[1]
        self.countdown = 0