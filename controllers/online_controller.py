"""
Online game controller - handles networked multiplayer game
"""
import pygame
import sys
from network.client import NetworkClient
from network.protocol import *
from views.game_renderer import GameRenderer
from views.lobby_renderer import LobbyRenderer, WaitingRoomRenderer
from config.constants import *

class OnlineGameController:
    def __init__(self, host='localhost', port=12345):
        # Initialize Pygame
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge - Online")
        self.clock = pygame.time.Clock()
        
        # Network client
        self.client = NetworkClient(host, port)
        
        # Renderers
        self.lobby_renderer = LobbyRenderer()
        self.waiting_renderer = WaitingRoomRenderer()
        self.game_renderer = GameRenderer()
        
        # Game state
        self.running = True
        self.current_view = "lobby"  # "lobby", "waiting", "game"
        self.players_in_room = 0
        self.my_player_id = None
        self.room_player_names = []  # List of player names in current room
        
        # Auto-play options
        self.player_name = "Player"
        self.auto_create_room = False
        self.auto_join_room = None
        
        # Setup message handlers
        self.setup_message_handlers()
    
    def setup_message_handlers(self):
        """Setup handlers for network messages"""
        self.client.set_message_handler(MessageType.ROOM_CREATED, self.on_room_created)
        self.client.set_message_handler(MessageType.ROOM_JOINED, self.on_room_joined)
        self.client.set_message_handler(MessageType.ROOM_FULL, self.on_room_full)
        self.client.set_message_handler(MessageType.ROOM_NOT_FOUND, self.on_room_not_found)
        self.client.set_message_handler(MessageType.ROOM_UPDATE, self.on_room_update)
        self.client.set_message_handler(MessageType.GAME_START, self.on_game_start)
        self.client.set_message_handler(MessageType.GAME_OVER, self.on_game_over)
    
    def on_room_created(self, data):
        """Handle room created message"""
        self.my_player_id = data.get('player_id')
        self.players_in_room = data.get('players_count', 1)
        self.current_view = "waiting"
        self.lobby_renderer.set_status(f"Room {data.get('room_id')} created! Waiting for players...", GREEN)
    
    def on_room_joined(self, data):
        """Handle room joined message"""
        self.my_player_id = data.get('player_id')
        self.players_in_room = data.get('players_count', 1)
        self.current_view = "waiting"
        self.lobby_renderer.set_status(f"Joined room {data.get('room_id')}!", GREEN)
    
    def on_room_full(self, data):
        """Handle room full message"""
        self.lobby_renderer.set_status("Room is full!", RED)
    
    def on_room_not_found(self, data):
        """Handle room not found message"""
        self.lobby_renderer.set_status("Room not found!", RED)
    
    def on_room_update(self, data):
        """Handle room update message with player list"""
        self.players_in_room = data.get('players_count', 0)
        self.room_player_names = data.get('player_names', [])
    
    def on_game_start(self, data):
        """Handle game start message"""
        self.current_view = "game"
    
    def on_game_over(self, data):
        """Handle game over message"""
        # Game over is handled in the game renderer
        pass
    
    def handle_lobby_input(self, event):
        """Handle input in lobby view"""
        action = None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                action = self.lobby_renderer.handle_button_click(event.pos)
        else:
            self.lobby_renderer.handle_text_input(event)
        
        if action == "create_room":
            if not self.client.connected:
                if not self.client.connect():
                    self.lobby_renderer.set_status("Failed to connect to server!", RED)
                    return
            
            self.client.create_room(self.lobby_renderer.player_name_input)
            self.lobby_renderer.set_status("Creating room...", BLUE)
        
        elif action == "join_room":
            if not self.lobby_renderer.room_id_input:
                self.lobby_renderer.set_status("Please enter a room ID!", RED)
                return
            
            # Get server IP from lobby input
            server_ip = self.lobby_renderer.server_ip_input or "localhost"
            
            # Reconnect if the server IP changed
            if server_ip != self.client.host or not self.client.connected:
                self.client.disconnect()
                self.client.host = server_ip
                if not self.client.connect():
                    self.lobby_renderer.set_status(f"Failed to connect to {server_ip}!", RED)
                    return
            
            self.client.join_room(
                self.lobby_renderer.room_id_input,
                self.lobby_renderer.player_name_input
            )
            self.lobby_renderer.set_status("Joining room...", BLUE)
    
    def handle_game_input(self, event):
        """Handle input in game view"""
        if event.type == pygame.KEYDOWN:
            # Hit controls: SPACE or UP arrow
            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                self.client.send_action(ActionType.HIT)
            # Dodge controls: DOWN arrow or ENTER
            elif event.key in [pygame.K_DOWN, pygame.K_RETURN]:
                self.client.send_action(ActionType.DODGE)
    
    def update_waiting_room(self):
        """Update waiting room player count"""
        # Update player count from latest game state
        if self.client.game_state:
            players = self.client.game_state.get('players', [])
            self.players_in_room = len([p for p in players if p.get('state') != 4])  # Not eliminated
    
    def run(self):
        """Main game loop"""
        # Handle auto-actions on first run
        auto_handled = False
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle auto-create or auto-join on first loop
            if not auto_handled and self.current_view == "lobby":
                if self.auto_create_room:
                    self.client.connect()
                    if self.client.connected:
                        self.client.create_room(self.player_name)
                        auto_handled = True
                elif self.auto_join_room:
                    self.client.connect()
                    if self.client.connected:
                        self.client.join_room(self.auto_join_room, self.player_name)
                        auto_handled = True
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.current_view == "lobby":
                    self.handle_lobby_input(event)
                elif self.current_view == "game":
                    self.handle_game_input(event)
            
            # Update waiting room
            if self.current_view == "waiting":
                self.update_waiting_room()
            
            # Render current view
            if self.current_view == "lobby":
                self.lobby_renderer.render(self.screen)
            elif self.current_view == "waiting":
                self.waiting_renderer.render(
                    self.screen, 
                    self.client.room_id or "????", 
                    self.players_in_room,
                    4,  # max_players
                    self.room_player_names
                )
            elif self.current_view == "game":
                self.game_renderer.render_online_game(
                    self.screen, 
                    self.client.game_state, 
                    self.my_player_id
                )
            
            # Update display
            pygame.display.flip()
        
        # Cleanup
        if self.client.connected:
            self.client.disconnect()
        pygame.quit()
        sys.exit()