import pygame
import sys
from models.game import Game
from views.game_renderer import GameRenderer
from config.constants import *

class LocalMultiplayerController:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge - 4 Người Chơi Cùng Máy")
        self.clock = pygame.time.Clock()
        
        self.game = Game()
        self.renderer = GameRenderer()
        
        self.running = True
        
        self.show_controls = True
        self.controls_timer = 5.0
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.show_controls:
                self.show_controls = False
                return
            
            if not self.game.game_over:
                if event.key == pygame.K_q:
                    self.game.players[0].hit_ball(self.game.ball)
                elif event.key == pygame.K_a:
                    self.game.players[0].start_dodge()
                
                elif event.key == pygame.K_w:
                    self.game.players[1].hit_ball(self.game.ball)
                elif event.key == pygame.K_s:
                    self.game.players[1].start_dodge()
                
                elif event.key == pygame.K_o:
                    self.game.players[2].hit_ball(self.game.ball)
                elif event.key == pygame.K_l:
                    self.game.players[2].start_dodge()
                
                elif event.key == pygame.K_p:
                    self.game.players[3].hit_ball(self.game.ball)
                elif event.key == pygame.K_SEMICOLON:
                    self.game.players[3].start_dodge()
            
            if event.key == pygame.K_SPACE and self.game.game_over:
                self.game.reset()
                self.show_controls = True
                self.controls_timer = 5.0
    
    def draw_controls_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font_title = pygame.font.Font(None, 64)
        title_text = font_title.render("HIT & DODGE", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        font_subtitle = pygame.font.Font(None, 32)
        subtitle_text = font_subtitle.render("4 Người Chơi - Cùng Máy", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        font_header = pygame.font.Font(None, 40)
        controls_header = font_header.render("ĐIỀU KHIỂN", True, WHITE)
        controls_rect = controls_header.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(controls_header, controls_rect)
        
        font_controls = pygame.font.Font(None, 28)
        y_offset = 230
        spacing = 60
        
        controls = [
            ("Người chơi 1 (Đỏ):", "Q = Hit  |  A = Dodge", RED),
            ("Người chơi 2 (Xanh lá):", "W = Hit  |  S = Dodge", GREEN),
            ("Người chơi 3 (Xanh dương):", "O = Hit  |  L = Dodge", BLUE),
            ("Người chơi 4 (Vàng):", "P = Hit  |  ; = Dodge", YELLOW),
        ]
        
        for player_name, keys, color in controls:
            name_text = font_controls.render(player_name, True, color)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(name_text, name_rect)
            
            keys_text = font_controls.render(keys, True, WHITE)
            keys_rect = keys_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 25))
            self.screen.blit(keys_text, keys_rect)
            
            y_offset += spacing
        
        font_instructions = pygame.font.Font(None, 24)
        instructions = [
            "Nhấn phím bất kỳ để bắt đầu",
            "SPACE = Chơi lại khi game kết thúc",
            "ESC = Thoát game"
        ]
        
        y_offset = 520
        for instruction in instructions:
            inst_text = font_instructions.render(instruction, True, GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 25
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.handle_input(event)
            
            if self.show_controls and self.controls_timer > 0:
                self.controls_timer -= dt
                if self.controls_timer <= 0:
                    self.show_controls = False
            
            if not self.show_controls:
                self.game.update(dt)
            
            self.renderer.render(self.screen, self.game)
            
            if self.show_controls:
                self.draw_controls_screen()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


def main():
    controller = LocalMultiplayerController()
    controller.run()


if __name__ == "__main__":
    main()
