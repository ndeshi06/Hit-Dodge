"""
Game renderer - handles all drawing operations
"""
import pygame
import math
from config.constants import *
from models.player_state import PlayerState

class GameRenderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_planet(self, screen):
        """Draw the planet"""
        pygame.draw.circle(screen, DARK_GRAY, PLANET_CENTER, PLANET_RADIUS, 3)
    
    def draw_player(self, screen, player):
        """Draw a single player"""
        if player.state == PlayerState.ELIMINATED:
            return
            
        if player.state == PlayerState.DODGING:
            # Draw as smaller circle when dodging (underground)
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), PLAYER_RADIUS // 2)
        else:
            # Draw player
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), PLAYER_RADIUS)
            
            # Draw stick with swing animation
            if player.state in [PlayerState.STANDING, PlayerState.SWINGING, PlayerState.FLYING_OFF]:
                stick_length = 35  # Made longer for larger players
                
                # Set base angle based on player position
                if player.id == 0:  # Player 1 (bottom) - horizontal, pointing right
                    base_angle = 0  # 0 degrees (right)
                elif player.id == 1:  # Player 2 (left) - vertical, pointing up
                    base_angle = math.pi/2  # 90 degrees (up)
                elif player.id == 2:  # Player 3 (top) - horizontal, pointing left
                    base_angle = math.pi  # 180 degrees (left)
                elif player.id == 3:  # Player 4 (right) - vertical, pointing down
                    base_angle = -math.pi/2  # -90 degrees (down)
                
                swing_offset = math.radians(player.stick_angle)
                stick_angle = base_angle + swing_offset
                
                stick_end_x = player.x + stick_length * math.cos(stick_angle)
                stick_end_y = player.y + stick_length * math.sin(stick_angle)
                pygame.draw.line(screen, BLACK, (int(player.x), int(player.y)), 
                               (int(stick_end_x), int(stick_end_y)), 4)  # Thicker stick too
        
        # Draw hit range indicator when standing
        if player.state == PlayerState.STANDING:
            if player.hit_cooldown <= 0:
                # Normal hit range indicator when ready to hit
                pygame.draw.circle(screen, (*player.color, 50), (int(player.x), int(player.y)), HIT_RANGE, 2)
            else:
                # Dimmed hit range indicator during cooldown
                pygame.draw.circle(screen, (*player.color, 20), (int(player.x), int(player.y)), HIT_RANGE, 1)
                # Small cooldown indicator
                cooldown_progress = player.hit_cooldown / HIT_COOLDOWN
                pygame.draw.arc(screen, (255, 100, 100), 
                              (int(player.x - 20), int(player.y - 20), 40, 40),
                              0, 2 * math.pi * cooldown_progress, 3)
    
    def draw_ball(self, screen, ball):
        """Draw the ball"""
        pos = ball.get_position()
        
        if not ball.is_active:
            # Draw ball with pulsing effect during countdown
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            radius = BALL_RADIUS + int(pulse * 5)
            pygame.draw.circle(screen, (255, 100, 100), (int(pos[0]), int(pos[1])), radius)
            
            # Draw countdown timer
            countdown = int(ball.spawn_timer) + 1
            text = self.font.render(str(countdown), True, BLACK)
            text_rect = text.get_rect(center=(int(pos[0]), int(pos[1]) - 30))
            screen.blit(text, text_rect)
        else:
            # Draw normal moving ball
            pygame.draw.circle(screen, BLACK, (int(pos[0]), int(pos[1])), BALL_RADIUS)
    
    def draw_ui(self, screen, game):
        """Draw UI elements"""
        # Draw instructions
        instructions = [
            "Player 1 (Red): Q=Hit, A=Dodge",
            "Player 2 (Green): W=Hit, S=Dodge", 
            "Player 3 (Blue): E=Hit, D=Dodge",
            "Player 4 (Yellow): R=Hit, F=Dodge"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, PLAYER_COLORS[i])
            screen.blit(text, (10, 10 + i * 25))
        
        # Draw game over screen
        if game.game_over:
            if game.winner:
                text = self.font.render(f"Player {game.winner.id + 1} Wins!", True, game.winner.color)
            else:
                text = self.font.render("Game Over!", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text, text_rect)
            
            restart_text = self.small_font.render("Press SPACE to restart", True, BLACK)
            screen.blit(restart_text, (10, 150))
    
    def render_online_game(self, screen, game_state, my_player_id):
        """Render the game from network state"""
        if not game_state:
            return
            
        # Clear screen
        screen.fill(WHITE)
        
        # Draw planet
        self.draw_planet(screen)
        
        # Draw players from network data
        for player_data in game_state.get('players', []):
            self.draw_network_player(screen, player_data, my_player_id)
        
        # Draw ball from network data
        ball_data = game_state.get('ball', {})
        self.draw_network_ball(screen, ball_data)
        
        # Draw UI
        self.draw_online_ui(screen, game_state, my_player_id)
    
    def draw_network_player(self, screen, player_data, my_player_id):
        """Draw a player from network data"""
        player_id = player_data.get('id', 0)
        x = player_data.get('x', 0)
        y = player_data.get('y', 0)
        state = player_data.get('state', 1)  # Default to STANDING
        stick_angle = player_data.get('stick_angle', 0)
        color = tuple(player_data.get('color', [255, 255, 255]))
        
        # Skip eliminated players
        if state == 4:  # ELIMINATED
            return
            
        if state == 2:  # DODGING
            # Draw as smaller circle when dodging
            pygame.draw.circle(screen, color, (int(x), int(y)), PLAYER_RADIUS // 2)
        else:
            # Draw player
            pygame.draw.circle(screen, color, (int(x), int(y)), PLAYER_RADIUS)
            
            # Draw stick
            if state in [1, 3, 5]:  # STANDING, SWINGING, FLYING_OFF
                stick_length = 35
                
                # Set base angle based on player position
                if player_id == 0:  # Player 1 (bottom) - horizontal, pointing right
                    base_angle = 0
                elif player_id == 1:  # Player 2 (left) - vertical, pointing up
                    base_angle = math.pi/2
                elif player_id == 2:  # Player 3 (top) - horizontal, pointing left
                    base_angle = math.pi
                elif player_id == 3:  # Player 4 (right) - vertical, pointing down
                    base_angle = -math.pi/2
                
                swing_offset = math.radians(stick_angle)
                stick_angle_rad = base_angle + swing_offset
                
                stick_end_x = x + stick_length * math.cos(stick_angle_rad)
                stick_end_y = y + stick_length * math.sin(stick_angle_rad)
                pygame.draw.line(screen, BLACK, (int(x), int(y)), 
                               (int(stick_end_x), int(stick_end_y)), 4)
        
        # Highlight current player
        if player_id == my_player_id:
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), PLAYER_RADIUS + 5, 3)
    
    def draw_network_ball(self, screen, ball_data):
        """Draw the ball from network data"""
        x = ball_data.get('x', 0)
        y = ball_data.get('y', 0)
        is_active = ball_data.get('is_active', False)
        spawn_timer = ball_data.get('spawn_timer', 0)
        
        if not is_active:
            # Draw ball with pulsing effect during countdown
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            radius = BALL_RADIUS + int(pulse * 5)
            pygame.draw.circle(screen, (255, 100, 100), (int(x), int(y)), radius)
            
            # Draw countdown timer
            countdown = int(spawn_timer) + 1
            text = self.font.render(str(countdown), True, BLACK)
            text_rect = text.get_rect(center=(int(x), int(y) - 30))
            screen.blit(text, text_rect)
        else:
            # Draw normal moving ball
            pygame.draw.circle(screen, BLACK, (int(x), int(y)), BALL_RADIUS)
    
    def draw_online_ui(self, screen, game_state, my_player_id):
        """Draw UI for online game"""
        # Draw controls for current player
        controls_text = "Your controls: SPACE/UP = Hit, DOWN/ENTER = Dodge"
        text = self.small_font.render(controls_text, True, BLACK)
        screen.blit(text, (10, SCREEN_HEIGHT - 30))
        
        # Draw game over screen
        if game_state.get('game_over', False):
            winner_id = game_state.get('winner_id')
            if winner_id is not None:
                if winner_id == my_player_id:
                    text = self.font.render("You Win!", True, GREEN)
                else:
                    text = self.font.render(f"Player {winner_id + 1} Wins!", True, RED)
            else:
                text = self.font.render("Game Over!", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text, text_rect)
    
    def render(self, screen, game):
        """Render the local game"""
        # Clear screen
        screen.fill(WHITE)
        
        # Draw planet
        self.draw_planet(screen)
        
        # Draw ball
        self.draw_ball(screen, game.ball)
        
        # Draw players
        for player in game.players:
            self.draw_player(screen, player)
        
        # Draw UI
        self.draw_ui(screen, game)