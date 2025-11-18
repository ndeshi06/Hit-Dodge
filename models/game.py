import math
from .player import Player
from .ball import Ball
from .player_state import PlayerState
from config.constants import *

class Game:
    def __init__(self, num_players=4):
        self.players = []
        self.ball = Ball()
        self.game_over = False
        self.winner = None
        
        for i in range(num_players):
            angle = i * (2 * math.pi / 4)
            player = Player(i, angle, PLAYER_COLORS[i])
            self.players.append(player)
    
    def check_collisions(self):
        if not self.ball.is_active:
            return
            
        ball_pos = self.ball.get_position()
        
        for player in self.players:
            if player.state in [PlayerState.ELIMINATED, PlayerState.DODGING, PlayerState.FLYING_OFF]:
                continue
                
            distance = math.sqrt((ball_pos[0] - player.x)**2 + (ball_pos[1] - player.y)**2)
            
            if distance < BALL_RADIUS + PLAYER_RADIUS:
                player.eliminate(ball_pos[0], ball_pos[1])
                self.ball.reset_speed()
                print(f"Player {player.id + 1} eliminated!")
                break
    
    def check_game_over(self):
        active_players = [p for p in self.players if p.state != PlayerState.ELIMINATED]
        if len(active_players) <= 1:
            self.game_over = True
            if len(active_players) == 1:
                self.winner = active_players[0]
    
    def update(self, dt):
        if not self.game_over:
            self.ball.update(dt)
            for player in self.players:
                player.update(dt)
            self.check_collisions()
            self.check_game_over()
    
    def reset(self):
        self.__init__()