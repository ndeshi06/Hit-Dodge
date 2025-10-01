"""
Game model - main game logic and state management
"""
import math
from .player import Player
from .ball import Ball
from .player_state import PlayerState
from config.constants import *

class Game:
    def __init__(self):
        self.players = []
        self.ball = Ball()
        self.game_over = False
        self.winner = None
        
        # Create 4 players positioned around the planet
        for i in range(4):
            angle = i * (2 * math.pi / 4)  # 90 degrees apart
            player = Player(i, angle, PLAYER_COLORS[i])
            self.players.append(player)
    
    def check_collisions(self):
        """Check for ball-player collisions"""
        if not self.ball.is_active:
            return  # No collisions during spawn delay
            
        ball_pos = self.ball.get_position()
        
        for player in self.players:
            if player.state in [PlayerState.ELIMINATED, PlayerState.DODGING, PlayerState.FLYING_OFF]:
                continue
                
            # Use current player position (x, y) instead of get_position
            distance = math.sqrt((ball_pos[0] - player.x)**2 + (ball_pos[1] - player.y)**2)
            
            if distance < BALL_RADIUS + PLAYER_RADIUS:
                # Start elimination animation
                player.eliminate(ball_pos[0], ball_pos[1])
                # Reset ball speed when player is eliminated (but keep direction and position)
                self.ball.reset_speed()
                print(f"Player {player.id + 1} eliminated!")
                break  # Only eliminate one player per frame
    
    def check_game_over(self):
        """Check if game is over"""
        active_players = [p for p in self.players if p.state != PlayerState.ELIMINATED]
        if len(active_players) <= 1:
            self.game_over = True
            if len(active_players) == 1:
                self.winner = active_players[0]
    
    def update(self, dt):
        """Update game state"""
        if not self.game_over:
            self.ball.update(dt)
            for player in self.players:
                player.update(dt)
            self.check_collisions()
            self.check_game_over()
    
    def reset(self):
        """Reset the game to initial state"""
        self.__init__()