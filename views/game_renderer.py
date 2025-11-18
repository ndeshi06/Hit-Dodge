import pygame
import math
from config.constants import *
from models.player_state import PlayerState

class GameRenderer:
    def __init__(self):
        try:
            self.font = pygame.font.SysFont('arial', 48)
            self.small_font = pygame.font.SysFont('arial', 24)
        except:
            self.font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 24)
    
    def rotate_point(self, x, y, rotation_angle):
        x_rel = x - PLANET_CENTER[0]
        y_rel = y - PLANET_CENTER[1]
        
        cos_a = math.cos(rotation_angle)
        sin_a = math.sin(rotation_angle)
        x_rot = x_rel * cos_a - y_rel * sin_a
        y_rot = x_rel * sin_a + y_rel * cos_a
        
        return x_rot + PLANET_CENTER[0], y_rot + PLANET_CENTER[1]
    
    def draw_planet(self, screen):
        pygame.draw.circle(screen, DARK_GRAY, PLANET_CENTER, PLANET_RADIUS, 3)
    
    def draw_player(self, screen, player):
        if player.lives <= 0:
            return
        
        name_font = pygame.font.SysFont('arial', 16)
        player_name = f'Player {player.id + 1}'
        name_text = name_font.render(player_name, True, BLACK)
        name_rect = name_text.get_rect(center=(int(player.x), int(player.y - 55)))
        screen.blit(name_text, name_rect)
        
        heart_size = 12
        heart_spacing = 15
        total_hearts_width = 4 * heart_spacing - heart_spacing + heart_size
        hearts_start_x = player.x - total_hearts_width / 2
        hearts_y = player.y - 40
        
        for i in range(4):
            heart_x = hearts_start_x + i * heart_spacing
            if i < player.lives:
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (heart_x, hearts_y + 3),
                    (heart_x - 5, hearts_y - 3),
                    (heart_x, hearts_y - 6),
                    (heart_x + 5, hearts_y - 3)
                ])
                pygame.draw.circle(screen, (255, 0, 0), (int(heart_x - 3), int(hearts_y - 3)), 4)
                pygame.draw.circle(screen, (255, 0, 0), (int(heart_x + 3), int(hearts_y - 3)), 4)
            else:
                pygame.draw.polygon(screen, (100, 100, 100), [
                    (heart_x, hearts_y + 3),
                    (heart_x - 5, hearts_y - 3),
                    (heart_x, hearts_y - 6),
                    (heart_x + 5, hearts_y - 3)
                ])
                pygame.draw.circle(screen, (100, 100, 100), (int(heart_x - 3), int(hearts_y - 3)), 4)
                pygame.draw.circle(screen, (100, 100, 100), (int(heart_x + 3), int(hearts_y - 3)), 4)
            
        if player.state == PlayerState.DODGING:
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), PLAYER_RADIUS // 2)
        else:
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), PLAYER_RADIUS)
            
            if player.state in [PlayerState.STANDING, PlayerState.SWINGING]:
                stick_length = 35
                
                if player.id == 0:
                    base_angle = 0
                elif player.id == 1:
                    base_angle = math.pi/2
                elif player.id == 2:
                    base_angle = math.pi
                elif player.id == 3:
                    base_angle = -math.pi/2
                
                swing_offset = math.radians(player.stick_angle)
                stick_angle = base_angle + swing_offset
                
                stick_end_x = player.x + stick_length * math.cos(stick_angle)
                stick_end_y = player.y + stick_length * math.sin(stick_angle)
                pygame.draw.line(screen, BLACK, (int(player.x), int(player.y)), 
                               (int(stick_end_x), int(stick_end_y)), 4)
        
        if player.invincible_timer > 0:
            shield_alpha = int((abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100) + 50)
            shield_surface = pygame.Surface((PLAYER_RADIUS * 3, PLAYER_RADIUS * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha), 
                             (PLAYER_RADIUS * 1.5, PLAYER_RADIUS * 1.5), PLAYER_RADIUS + 10, 3)
            screen.blit(shield_surface, (int(player.x - PLAYER_RADIUS * 1.5), int(player.y - PLAYER_RADIUS * 1.5)))
        
        if player.state == PlayerState.STANDING:
            if player.hit_cooldown <= 0:
                pygame.draw.circle(screen, (*player.color, 50), (int(player.x), int(player.y)), HIT_RANGE, 2)
            else:
                pygame.draw.circle(screen, (*player.color, 20), (int(player.x), int(player.y)), HIT_RANGE, 1)
                cooldown_progress = player.hit_cooldown / HIT_COOLDOWN
                pygame.draw.arc(screen, (255, 100, 100), 
                              (int(player.x - 20), int(player.y - 20), 40, 40),
                              0, 2 * math.pi * cooldown_progress, 3)
    
    def draw_ball(self, screen, ball):
        pos = ball.get_position()
        
        if not ball.is_active:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            radius = BALL_RADIUS + int(pulse * 5)
            pygame.draw.circle(screen, (255, 100, 100), (int(pos[0]), int(pos[1])), radius)
            
            countdown = int(ball.spawn_timer) + 1
            text = self.font.render(str(countdown), True, BLACK)
            text_rect = text.get_rect(center=(int(pos[0]), int(pos[1]) - 30))
            screen.blit(text, text_rect)
        else:
            pygame.draw.circle(screen, BLACK, (int(pos[0]), int(pos[1])), BALL_RADIUS)
    
    def draw_ui(self, screen, game):
        instructions = [
            "Player 1 (Red): Q=Hit, A=Dodge",
            "Player 2 (Green): W=Hit, S=Dodge", 
            "Player 3 (Blue): E=Hit, D=Dodge",
            "Player 4 (Yellow): R=Hit, F=Dodge"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, PLAYER_COLORS[i])
            screen.blit(text, (10, 10 + i * 25))
        
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
        if not game_state:
            return
        
        rotation_angle = (1 - my_player_id) * math.pi / 2 + math.pi
        
        screen.fill(WHITE)
        
        self.draw_planet(screen)
        
        for player_data in game_state.get('players', []):
            self.draw_network_player(screen, player_data, my_player_id, rotation_angle)
        
        ball_data = game_state.get('ball', {})
        self.draw_network_ball(screen, ball_data, rotation_angle)
        
        return self.draw_online_ui(screen, game_state, my_player_id)
    
    def draw_network_player(self, screen, player_data, my_player_id, rotation_angle=0):
        player_id = player_data.get('id', 0)
        x = player_data.get('x', 0)
        y = player_data.get('y', 0)
        state = player_data.get('state', 1)
        stick_angle = player_data.get('stick_angle', 0)
        color = tuple(player_data.get('color', [255, 255, 255]))
        lives = player_data.get('lives', 4)
        
        if lives <= 0:
            return
        
        x_rot, y_rot = self.rotate_point(x, y, rotation_angle)
            
        if state == 2:
            pygame.draw.circle(screen, color, (int(x_rot), int(y_rot)), PLAYER_RADIUS // 2)
        else:
            pygame.draw.circle(screen, color, (int(x_rot), int(y_rot)), PLAYER_RADIUS)
            
            if state in [1, 3, 5]:
                stick_length = 35
                
                if player_id == 0:
                    base_angle = 0
                elif player_id == 1:
                    base_angle = math.pi/2
                elif player_id == 2:
                    base_angle = math.pi
                elif player_id == 3:
                    base_angle = -math.pi/2
                
                swing_offset = math.radians(stick_angle)
                stick_angle_rad = base_angle + swing_offset + rotation_angle
                
                stick_end_x = x_rot + stick_length * math.cos(stick_angle_rad)
                stick_end_y = y_rot + stick_length * math.sin(stick_angle_rad)
                pygame.draw.line(screen, BLACK, (int(x_rot), int(y_rot)), 
                               (int(stick_end_x), int(stick_end_y)), 4)
        
        invincible_timer = player_data.get('invincible_timer', 0)
        if invincible_timer > 0:
            shield_alpha = int((abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100) + 50)
            shield_surface = pygame.Surface((PLAYER_RADIUS * 3, PLAYER_RADIUS * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha), 
                             (PLAYER_RADIUS * 1.5, PLAYER_RADIUS * 1.5), PLAYER_RADIUS + 10, 3)
            screen.blit(shield_surface, (int(x_rot - PLAYER_RADIUS * 1.5), int(y_rot - PLAYER_RADIUS * 1.5)))
        
        if player_id == my_player_id:
            pygame.draw.circle(screen, WHITE, (int(x_rot), int(y_rot)), PLAYER_RADIUS + 5, 3)
        
        player_name = player_data.get('name', f'Player {player_id + 1}')
        
        original_angle = player_id * math.pi / 2
        rotated_name_angle = original_angle + rotation_angle
        
        name_distance = PLAYER_RADIUS + 45
        name_x = x_rot + name_distance * math.cos(rotated_name_angle)
        name_y = y_rot + name_distance * math.sin(rotated_name_angle)
        
        final_angle_normalized = rotated_name_angle % (2 * math.pi)
        angle_deg_from_right = math.degrees(final_angle_normalized)
        
        if 45 <= angle_deg_from_right < 135:
            text_rotation = 180
        elif 135 <= angle_deg_from_right < 225:
            text_rotation = 90
        elif 225 <= angle_deg_from_right < 315:
            text_rotation = 0
        else:
            text_rotation = -90
        
        name_text = self.small_font.render(player_name, True, BLACK)
        if text_rotation != 0:
            name_text = pygame.transform.rotate(name_text, text_rotation)
        
        name_rect = name_text.get_rect(center=(int(name_x), int(name_y)))
        
        bg_rect = name_rect.inflate(8, 4)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((*color, 180))
        screen.blit(bg_surface, bg_rect.topleft)
        screen.blit(name_text, name_rect)
        
        lives = player_data.get('lives', 4)
        heart_size = 12
        heart_spacing = 15
        total_hearts_width = 4 * heart_spacing - heart_spacing + heart_size
        
        hearts_distance = name_distance - 15
        hearts_center_x = x_rot + hearts_distance * math.cos(rotated_name_angle)
        hearts_center_y = y_rot + hearts_distance * math.sin(rotated_name_angle)
        
        for i in range(4):
            offset_x = (i - 1.5) * heart_spacing
            
            if 45 <= angle_deg_from_right < 135:
                heart_x = hearts_center_x - offset_x
                heart_y = hearts_center_y
            elif 135 <= angle_deg_from_right < 225:
                heart_x = hearts_center_x
                heart_y = hearts_center_y - offset_x
            elif 225 <= angle_deg_from_right < 315:
                heart_x = hearts_center_x + offset_x
                heart_y = hearts_center_y
            else:
                heart_x = hearts_center_x
                heart_y = hearts_center_y + offset_x
            
            if i < lives:
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (heart_x, heart_y + 3),
                    (heart_x - 5, heart_y - 3),
                    (heart_x, heart_y - 6),
                    (heart_x + 5, heart_y - 3)
                ])
                pygame.draw.circle(screen, (255, 0, 0), (int(heart_x - 3), int(heart_y - 3)), 4)
                pygame.draw.circle(screen, (255, 0, 0), (int(heart_x + 3), int(heart_y - 3)), 4)
            else:
                pygame.draw.polygon(screen, (100, 100, 100), [
                    (heart_x, heart_y + 3),
                    (heart_x - 5, heart_y - 3),
                    (heart_x, heart_y - 6),
                    (heart_x + 5, heart_y - 3)
                ])
                pygame.draw.circle(screen, (100, 100, 100), (int(heart_x - 3), int(heart_y - 3)), 4)
                pygame.draw.circle(screen, (100, 100, 100), (int(heart_x + 3), int(heart_y - 3)), 4)
    
    def draw_network_ball(self, screen, ball_data, rotation_angle=0):
        x = ball_data.get('x', 0)
        y = ball_data.get('y', 0)
        is_active = ball_data.get('is_active', False)
        spawn_timer = ball_data.get('spawn_timer', 0)
        
        x_rot, y_rot = self.rotate_point(x, y, rotation_angle)
        
        if not is_active:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            radius = BALL_RADIUS + int(pulse * 5)
            pygame.draw.circle(screen, (255, 100, 100), (int(x_rot), int(y_rot)), radius)
            
            countdown = int(spawn_timer) + 1
            text = self.font.render(str(countdown), True, BLACK)
            text_rect = text.get_rect(center=(int(x_rot), int(y_rot) - 30))
            screen.blit(text, text_rect)
        else:
            pygame.draw.circle(screen, BLACK, (int(x_rot), int(y_rot)), BALL_RADIUS)
    
    def draw_online_ui(self, screen, game_state, my_player_id, ready_clicked=False):
        if not game_state.get('game_over', False):
            controls_text = "Your controls: SPACE/UP = Hit, DOWN/ENTER = Dodge"
            text = self.small_font.render(controls_text, True, BLACK)
            screen.blit(text, (10, SCREEN_HEIGHT - 30))
        else:
            winner_id = game_state.get('winner_id')
            if winner_id is not None:
                if winner_id == my_player_id:
                    text = self.font.render("You Win!", True, GREEN)
                else:
                    text = self.font.render(f"Player {winner_id + 1} Wins!", True, RED)
            else:
                text = self.font.render("Game Over!", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(text, text_rect)
            

            
            back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 220, 200, 60)
            
            pygame.draw.rect(screen, RED, back_button)
            pygame.draw.rect(screen, BLACK, back_button, 3)
            
            back_text = self.small_font.render("BACK TO MENU", True, WHITE)
            
            screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2,
                                   back_button.centery - back_text.get_height() // 2))
            
            return None, back_button
        
        return None, None
    
    def render(self, screen, game):
        screen.fill(WHITE)
        
        self.draw_planet(screen)
        
        self.draw_ball(screen, game.ball)
        
        for player in game.players:
            self.draw_player(screen, player)
        
        self.draw_ui(screen, game)