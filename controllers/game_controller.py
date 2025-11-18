import pygame
import sys
from models.game import Game
from views.game_renderer import GameRenderer
from config.constants import *

class GameController:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge")
        self.clock = pygame.time.Clock()
        
        self.game = Game()
        self.renderer = GameRenderer()
        
        self.running = True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.game.game_over:
                if event.key == pygame.K_q:
                    self.game.players[0].hit_ball(self.game.ball)
                elif event.key == pygame.K_a:
                    self.game.players[0].start_dodge()
                
                elif event.key == pygame.K_w:
                    self.game.players[1].hit_ball(self.game.ball)
                elif event.key == pygame.K_s:
                    self.game.players[1].start_dodge()
                
                elif event.key == pygame.K_e:
                    self.game.players[2].hit_ball(self.game.ball)
                elif event.key == pygame.K_d:
                    self.game.players[2].start_dodge()
                
                elif event.key == pygame.K_r:
                    self.game.players[3].hit_ball(self.game.ball)
                elif event.key == pygame.K_f:
                    self.game.players[3].start_dodge()
            
            if event.key == pygame.K_SPACE and self.game.game_over:
                self.game.reset()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)
            
            self.game.update(dt)
            
            self.renderer.render(self.screen, self.game)
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()