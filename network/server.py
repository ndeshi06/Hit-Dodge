"""
Game server for Hit & Dodge multiplayer
"""
import socket
import threading
import time
import random
import string
from models.game import Game
from models.player_state import PlayerState
from network.protocol import *

class GameRoom:
    def __init__(self, room_id, max_players=4):
        self.room_id = room_id
        self.max_players = max_players
        self.players = {}  # client_socket -> player_info
        self.game = None
        self.game_running = False
        self.last_update = time.time()
        
    def add_player(self, client_socket, player_name):
        if len(self.players) >= self.max_players:
            return False
        
        player_id = len(self.players)
        self.players[client_socket] = {
            'id': player_id,
            'name': player_name,
            'socket': client_socket
        }
        
        # Send room update to all players
        self.send_room_update()
        
        # Start game if room is full
        if len(self.players) == self.max_players:
            self.start_game()
        
        return True
    
    def remove_player(self, client_socket):
        if client_socket in self.players:
            del self.players[client_socket]
            # Send room update to remaining players
            self.send_room_update()
            # Stop game if not enough players
            if len(self.players) < self.max_players:
                self.game_running = False
    
    def send_room_update(self):
        """Send room update with player list to all players"""
        player_names = []
        for player_info in self.players.values():
            player_names.append(player_info['name'])
        
        room_data = {
            'room_id': self.room_id,
            'players_count': len(self.players),
            'max_players': self.max_players,
            'player_names': player_names
        }
        
        update_msg = NetworkMessage(MessageType.ROOM_UPDATE, room_data)
        self.broadcast_message(update_msg)
    
    def start_game(self):
        self.game = Game()
        self.game_running = True
        
        # Notify all players that game is starting
        start_msg = NetworkMessage(MessageType.GAME_START)
        self.broadcast_message(start_msg)
    
    def handle_player_action(self, client_socket, action):
        if not self.game_running or client_socket not in self.players:
            return
        
        player_info = self.players[client_socket]
        player_id = player_info['id']
        
        if player_id < len(self.game.players):
            player = self.game.players[player_id]
            
            if action == ActionType.HIT.value:
                player.hit_ball(self.game.ball)
            elif action == ActionType.DODGE.value:
                player.start_dodge()
    
    def update_game(self):
        if not self.game_running or not self.game:
            return
        
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        self.game.update(dt)
        
        # Send game state to all players
        game_state = self.serialize_game_state()
        state_msg = create_game_state_message(game_state)
        self.broadcast_message(state_msg)
        
        # Check if game is over
        if self.game.game_over:
            self.game_running = False
            game_over_msg = NetworkMessage(MessageType.GAME_OVER, {
                'winner_id': self.game.winner.id if self.game.winner else None
            })
            self.broadcast_message(game_over_msg)
    
    def serialize_game_state(self):
        players_data = []
        for player in self.game.players:
            players_data.append({
                'id': player.id,
                'x': player.x,
                'y': player.y,
                'state': player.state.value,
                'stick_angle': player.stick_angle,
                'color': player.color
            })
        
        ball_data = {
            'x': self.game.ball.get_position()[0],
            'y': self.game.ball.get_position()[1],
            'is_active': self.game.ball.is_active,
            'spawn_timer': self.game.ball.spawn_timer
        }
        
        return {
            'players': players_data,
            'ball': ball_data,
            'game_over': self.game.game_over
        }
    
    def broadcast_message(self, message):
        for client_socket in list(self.players.keys()):
            try:
                client_socket.send((message.to_json() + '\n').encode())
            except:
                # Remove disconnected client
                self.remove_player(client_socket)

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rooms = {}  # room_id -> GameRoom
        self.running = False
        
    def generate_room_id(self):
        """Generate a unique 4-character room ID"""
        while True:
            room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if room_id not in self.rooms:
                return room_id
    
    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        
        print(f"Game server started on {self.host}:{self.port}")
        
        # Start game update thread
        update_thread = threading.Thread(target=self.game_update_loop)
        update_thread.daemon = True
        update_thread.start()
        
        try:
            while self.running:
                client_socket, address = self.socket.accept()
                print(f"Client connected from {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        self.socket.close()
    
    def game_update_loop(self):
        """Update all active games"""
        while self.running:
            for room in list(self.rooms.values()):
                room.update_game()
            time.sleep(1/60)  # 60 FPS
    
    def handle_client(self, client_socket, address):
        try:
            buffer = ""
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = NetworkMessage.from_json(line)
                    if message:
                        self.process_message(client_socket, message)
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Remove client from any room
            for room in self.rooms.values():
                room.remove_player(client_socket)
            client_socket.close()
    
    def process_message(self, client_socket, message):
        if message.type == MessageType.CREATE_ROOM:
            self.handle_create_room(client_socket, message.data)
        elif message.type == MessageType.JOIN_ROOM:
            self.handle_join_room(client_socket, message.data)
        elif message.type == MessageType.PLAYER_ACTION:
            self.handle_player_action(client_socket, message.data)
    
    def handle_create_room(self, client_socket, data):
        room_id = self.generate_room_id()
        room = GameRoom(room_id)
        self.rooms[room_id] = room
        
        player_name = data.get('player_name', 'Player')
        room.add_player(client_socket, player_name)
        
        response = NetworkMessage(MessageType.ROOM_CREATED, {
            'room_id': room_id,
            'player_id': 0,
            'players_count': len(room.players)
        })
        
        try:
            client_socket.send((response.to_json() + '\n').encode())
            # Send initial room update
            room.send_room_update()
        except:
            pass
    
    def handle_join_room(self, client_socket, data):
        room_id = data.get('room_id')
        player_name = data.get('player_name', 'Player')
        
        if room_id not in self.rooms:
            response = NetworkMessage(MessageType.ROOM_NOT_FOUND)
            try:
                client_socket.send((response.to_json() + '\n').encode())
            except:
                pass
            return
        
        room = self.rooms[room_id]
        if len(room.players) >= room.max_players:
            response = NetworkMessage(MessageType.ROOM_FULL)
            try:
                client_socket.send((response.to_json() + '\n').encode())
            except:
                pass
            return
        
        player_id = len(room.players)
        room.add_player(client_socket, player_name)
        
        response = NetworkMessage(MessageType.ROOM_JOINED, {
            'room_id': room_id,
            'player_id': player_id,
            'players_count': len(room.players)
        })
        
        try:
            client_socket.send((response.to_json() + '\n').encode())
            # Send room update to show all players
            room.send_room_update()
        except:
            pass
    
    def handle_player_action(self, client_socket, data):
        action = data.get('action')
        
        # Find which room this client is in
        for room in self.rooms.values():
            if client_socket in room.players:
                room.handle_player_action(client_socket, action)
                break

if __name__ == "__main__":
    server = GameServer()
    server.start()