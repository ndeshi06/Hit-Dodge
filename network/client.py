"""
Network client for Hit & Dodge multiplayer
"""
import socket
import threading
import time
from network.protocol import *

class NetworkClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.room_id = None
        self.player_id = None
        self.game_state = None
        self.message_handlers = {}
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            if self.socket:
                self.socket.close()
    
    def send_message(self, message):
        if self.connected and self.socket:
            try:
                self.socket.send((message.to_json() + '\n').encode())
                return True
            except Exception as e:
                print(f"Failed to send message: {e}")
                self.connected = False
                return False
        return False
    
    def receive_messages(self):
        buffer = ""
        try:
            while self.connected:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = NetworkMessage.from_json(line)
                    if message:
                        self.handle_message(message)
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.connected = False
    
    def handle_message(self, message):
        if message.type in self.message_handlers:
            self.message_handlers[message.type](message.data)
        
        # Handle common messages
        if message.type == MessageType.ROOM_CREATED:
            self.room_id = message.data.get('room_id')
            self.player_id = message.data.get('player_id')
        elif message.type == MessageType.ROOM_JOINED:
            self.room_id = message.data.get('room_id')
            self.player_id = message.data.get('player_id')
        elif message.type == MessageType.GAME_STATE:
            self.game_state = message.data
    
    def set_message_handler(self, message_type, handler):
        self.message_handlers[message_type] = handler
    
    def create_room(self, player_name):
        message = create_create_room_message(player_name)
        return self.send_message(message)
    
    def join_room(self, room_id, player_name):
        message = create_join_room_message(room_id, player_name)
        return self.send_message(message)
    
    def send_action(self, action_type):
        message = create_action_message(action_type)
        return self.send_message(message)