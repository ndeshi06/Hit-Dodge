"""
Player model - represents a player in the game
"""
import math
from .player_state import PlayerState
from config.constants import *

class Player:
    def __init__(self, player_id, angle, color):
        self.id = player_id
        self.angle = angle  # Angle around the planet (in radians)
        self.color = color
        self.state = PlayerState.STANDING
        self.dodge_timer = 0  # Time remaining in dodge state
        self.swing_timer = 0  # Time remaining in swing state
        self.hit_cooldown = 0  # Time remaining before can hit again
        self.stick_angle = 0  # Angle of the stick
        self.swing_target_angle = 0  # Target angle to swing towards when hitting ball
        self.swing_progress = 0  # Progress of swing animation (0-1)
        self.fly_velocity_x = 0  # For flying off screen animation
        self.fly_velocity_y = 0
        self.x = 0  # Current screen position
        self.y = 0
        self.update_position()
        
    def update_position(self):
        """Update position based on current state"""
        if self.state == PlayerState.FLYING_OFF:
            return  # Position updated by physics
        
        if self.state == PlayerState.DODGING:
            # Underground position (closer to planet center)
            self.x = PLANET_CENTER[0] + (PLANET_RADIUS - PLAYER_RADIUS//2) * math.cos(self.angle)
            self.y = PLANET_CENTER[1] + (PLANET_RADIUS - PLAYER_RADIUS//2) * math.sin(self.angle)
        else:
            # Surface position (further from planet center to accommodate larger players)
            self.x = PLANET_CENTER[0] + (PLANET_RADIUS + PLAYER_RADIUS + 5) * math.cos(self.angle)
            self.y = PLANET_CENTER[1] + (PLANET_RADIUS + PLAYER_RADIUS + 5) * math.sin(self.angle)
        
    def get_position(self):
        """Get player position on the planet surface"""
        x = PLANET_CENTER[0] + (PLANET_RADIUS + PLAYER_RADIUS + 5) * math.cos(self.angle)
        y = PLANET_CENTER[1] + (PLANET_RADIUS + PLAYER_RADIUS + 5) * math.sin(self.angle)
        return (x, y)
    
    def get_dodge_position(self):
        """Get player position when dodging (underground)"""
        x = PLANET_CENTER[0] + (PLANET_RADIUS - PLAYER_RADIUS//2) * math.cos(self.angle)
        y = PLANET_CENTER[1] + (PLANET_RADIUS - PLAYER_RADIUS//2) * math.sin(self.angle)
        return (x, y)
    
    def can_hit(self, ball_x, ball_y):
        """Check if ball is within hitting range"""
        distance = math.sqrt((self.x - ball_x)**2 + (self.y - ball_y)**2)
        return distance <= HIT_RANGE
    
    def start_dodge(self):
        """Start dodging for a short duration"""
        if self.state == PlayerState.STANDING:
            self.state = PlayerState.DODGING
            self.dodge_timer = 1.0  # Dodge for 1 second
            self.update_position()
    
    def hit_ball(self, ball):
        """Hit the ball, reversing its direction and increasing speed"""
        if self.state == PlayerState.STANDING and self.hit_cooldown <= 0:
            # Check if ball can be hit before starting swing
            ball_pos = ball.get_position()
            distance = math.sqrt((self.x - ball_pos[0])**2 + (self.y - ball_pos[1])**2)
            can_affect_ball = ball.is_active and distance <= HIT_RANGE
            
            # Calculate angle towards the ball for swing animation
            dx = ball_pos[0] - self.x
            dy = ball_pos[1] - self.y
            ball_angle = math.atan2(dy, dx)
            
            # Calculate base angle for each player's stick orientation
            if self.id == 0:  # Player 1 (bottom) - horizontal, pointing right
                base_angle = 0  # 0 degrees (right)
            elif self.id == 1:  # Player 2 (left) - vertical, pointing up
                base_angle = math.pi/2  # 90 degrees (up)
            elif self.id == 2:  # Player 3 (top) - horizontal, pointing left
                base_angle = math.pi  # 180 degrees (left)
            elif self.id == 3:  # Player 4 (right) - vertical, pointing down
                base_angle = -math.pi/2  # -90 degrees (down)
            
            # Calculate relative angle from player's base stick position
            self.swing_target_angle = ball_angle - base_angle
            
            # Normalize angle to reasonable swing range (-90 to +90 degrees)
            while self.swing_target_angle > math.pi:
                self.swing_target_angle -= 2 * math.pi
            while self.swing_target_angle < -math.pi:
                self.swing_target_angle += 2 * math.pi
            
            # Limit swing to reasonable range
            max_swing = math.radians(90)
            self.swing_target_angle = max(-max_swing, min(max_swing, self.swing_target_angle))
            
            # Always perform swing animation when hit is pressed
            self.state = PlayerState.SWINGING
            self.swing_timer = SWING_DURATION
            self.hit_cooldown = HIT_COOLDOWN  # Set cooldown timer
            
            # Only affect the ball if it was in range when we started the swing
            if can_affect_ball:
                ball.reverse_direction()
                ball.increase_speed()
                return True
            return False
        return False
    
    def eliminate(self, ball_x, ball_y):
        """Start flying off screen animation"""
        # Calculate direction to fly off
        dx = self.x - ball_x
        dy = self.y - ball_y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Set flying velocity
        speed = 300
        self.fly_velocity_x = dx * speed
        self.fly_velocity_y = dy * speed - 150  # Add upward component
        self.state = PlayerState.FLYING_OFF
    
    def update(self, dt):
        """Update player state"""
        # Update hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
        
        if self.state == PlayerState.DODGING:
            self.dodge_timer -= dt
            if self.dodge_timer <= 0:
                self.state = PlayerState.STANDING
                self.update_position()
        
        elif self.state == PlayerState.SWINGING:
            self.swing_timer -= dt
            # Update swing animation - swing towards the ball direction
            progress = 1 - (self.swing_timer / SWING_DURATION)
            self.swing_progress = progress
            # Create a smooth swing motion towards the target
            swing_intensity = math.sin(progress * math.pi)  # 0 -> 1 -> 0
            self.stick_angle = math.degrees(self.swing_target_angle * swing_intensity)
            
            if self.swing_timer <= 0:
                self.state = PlayerState.STANDING
                self.stick_angle = 0
                self.swing_target_angle = 0
                self.swing_progress = 0
        
        elif self.state == PlayerState.FLYING_OFF:
            # Apply physics for flying off screen
            self.x += self.fly_velocity_x * dt
            self.y += self.fly_velocity_y * dt
            self.fly_velocity_y += 400 * dt  # Gravity
            
            # Check if off screen
            if (self.x < -100 or self.x > SCREEN_WIDTH + 100 or 
                self.y > SCREEN_HEIGHT + 100):
                self.state = PlayerState.ELIMINATED