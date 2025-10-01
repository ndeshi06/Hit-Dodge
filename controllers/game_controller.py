"""
Game controller - handles input and game flow
"""
import pygame
import sys
from models.game import Game
from views.game_renderer import GameRenderer
from config.constants import *

class GameController:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge")
        self.clock = pygame.time.Clock()
        
        # Create game components
        self.game = Game()
        self.renderer = GameRenderer()
        
        # Game state
        self.running = True
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if not self.game.game_over:
                # Player 1 controls
                if event.key == pygame.K_q:  # Hit
                    self.game.players[0].hit_ball(self.game.ball)
                elif event.key == pygame.K_a:  # Dodge
                    self.game.players[0].start_dodge()
                
                # Player 2 controls
                elif event.key == pygame.K_w:  # Hit
                    self.game.players[1].hit_ball(self.game.ball)
                elif event.key == pygame.K_s:  # Dodge
                    self.game.players[1].start_dodge()
                
                # Player 3 controls
                elif event.key == pygame.K_e:  # Hit
                    self.game.players[2].hit_ball(self.game.ball)
                elif event.key == pygame.K_d:  # Dodge
                    self.game.players[2].start_dodge()
                
                # Player 4 controls
                elif event.key == pygame.K_r:  # Hit
                    self.game.players[3].hit_ball(self.game.ball)
                elif event.key == pygame.K_f:  # Dodge
                    self.game.players[3].start_dodge()
            
            # Restart game
            if event.key == pygame.K_SPACE and self.game.game_over:
                self.game.reset()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)
            
            # Update game
            self.game.update(dt)
            
            # Render game
            self.renderer.render(self.screen, self.game)
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()