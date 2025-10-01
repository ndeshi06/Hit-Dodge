"""
Lobby view for joining/creating rooms
"""
import pygame
from config.constants import *

class LobbyRenderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        self.room_id_input = ""
        self.player_name_input = "Player"
        self.input_active = "name"  # "name" or "room"
        self.status_message = ""
        self.status_color = BLACK
        self.show_room_input = False  # Show room input only when joining
        
    def handle_text_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.input_active == "name" and len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]
                elif self.input_active == "room" and len(self.room_id_input) > 0:
                    self.room_id_input = self.room_id_input[:-1]
        elif event.type == pygame.TEXTINPUT:
            if self.input_active == "name" and len(self.player_name_input) < 15:
                if event.text.isalnum() or event.text == " ":
                    self.player_name_input += event.text
            elif self.input_active == "room" and len(self.room_id_input) < 4:
                if event.text.isalnum():
                    self.room_id_input += event.text.upper()
        return None
    
    def handle_button_click(self, mouse_pos):
        """Handle button clicks and return action"""
        # Create Room button
        create_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 60)
        if create_rect.collidepoint(mouse_pos):
            return "create_room"
        
        # Join Room button  
        join_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 430, 300, 60)
        if join_rect.collidepoint(mouse_pos):
            if not self.show_room_input:
                self.show_room_input = True
                self.input_active = "room"
                return None
            elif self.room_id_input:
                return "join_room"
            else:
                self.set_status("Please enter a Room ID!", RED)
                return None
        
        # Player name input
        name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 40)
        if name_rect.collidepoint(mouse_pos):
            self.input_active = "name"
        
        # Room ID input (if visible)
        if self.show_room_input:
            room_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 520, 200, 40)
            if room_rect.collidepoint(mouse_pos):
                self.input_active = "room"
        
        return None
    
    def set_status(self, message, color=BLACK):
        self.status_message = message
        self.status_color = color
    
    def render(self, screen):
        screen.fill(WHITE)
        
        # Title
        title = self.font.render("Hit & Dodge", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("Online Multiplayer", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(subtitle, subtitle_rect)
        
        # Player name input
        name_label = self.small_font.render("Enter your name:", True, BLACK)
        name_label_rect = name_label.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(name_label, name_label_rect)
        
        name_color = BLUE if self.input_active == "name" else GRAY
        name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 40)
        pygame.draw.rect(screen, WHITE, name_rect)
        pygame.draw.rect(screen, name_color, name_rect, 3)
        
        name_text = self.small_font.render(self.player_name_input, True, BLACK)
        screen.blit(name_text, (name_rect.x + 10, name_rect.y + 8))
        
        # Create Room button
        create_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 60)
        pygame.draw.rect(screen, GREEN, create_rect)
        pygame.draw.rect(screen, BLACK, create_rect, 2)
        
        create_text = self.medium_font.render("🏠 Create New Room", True, WHITE)
        create_text_rect = create_text.get_rect(center=create_rect.center)
        screen.blit(create_text, create_text_rect)
        
        # Join Room button
        join_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 430, 300, 60)
        pygame.draw.rect(screen, BLUE, join_rect)
        pygame.draw.rect(screen, BLACK, join_rect, 2)
        
        join_text = self.medium_font.render("🚪 Join Existing Room", True, WHITE)
        join_text_rect = join_text.get_rect(center=join_rect.center)
        screen.blit(join_text, join_text_rect)
        
        # Room ID input (only show if joining)
        if self.show_room_input:
            room_label = self.small_font.render("Enter Room ID (4 characters):", True, BLACK)
            room_label_rect = room_label.get_rect(center=(SCREEN_WIDTH // 2, 510))
            screen.blit(room_label, room_label_rect)
            
            room_color = BLUE if self.input_active == "room" else GRAY
            room_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 540, 200, 40)
            pygame.draw.rect(screen, WHITE, room_rect)
            pygame.draw.rect(screen, room_color, room_rect, 3)
            
            room_text = self.small_font.render(self.room_id_input, True, BLACK)
            room_text_rect = room_text.get_rect(center=(room_rect.centerx, room_rect.centery))
            screen.blit(room_text, room_text_rect)
        
        # Status message
        if self.status_message:
            status_text = self.small_font.render(self.status_message, True, self.status_color)
            status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(status_text, status_rect)

class WaitingRoomRenderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        
    def render(self, screen, room_id, players_count, max_players=4, player_names=None):
        screen.fill(WHITE)
        
        # Title
        title = self.font.render(f"Room: {room_id}", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Player count
        count_text = self.small_font.render(f"Players: {players_count}/{max_players}", True, BLACK)
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(count_text, count_rect)
        
        # Players list
        if player_names and len(player_names) > 0:
            members_title = self.small_font.render("Room Members:", True, BLACK)
            screen.blit(members_title, (SCREEN_WIDTH // 2 - 100, 230))
            
            colors = [RED, GREEN, BLUE, YELLOW]
            for i, name in enumerate(player_names):
                if i < len(colors):
                    color = colors[i]
                    player_text = self.tiny_font.render(f"Player {i+1}: {name}", True, color)
                    screen.blit(player_text, (SCREEN_WIDTH // 2 - 80, 270 + i * 30))
        
        # Waiting message
        if players_count < max_players:
            waiting_text = self.small_font.render("Waiting for more players...", True, GRAY)
            waiting_rect = waiting_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
            screen.blit(waiting_text, waiting_rect)
            
            # Show room ID for sharing
            share_text = self.tiny_font.render(f"Share this Room ID with friends: {room_id}", True, BLUE)
            share_rect = share_text.get_rect(center=(SCREEN_WIDTH // 2, 480))
            screen.blit(share_text, share_rect)
        else:
            ready_text = self.small_font.render("Game starting soon!", True, GREEN)
            ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
            screen.blit(ready_text, ready_rect)