import pygame
import sys
import socket
import threading
import json
import random
import string
import time
from models.game import Game
from views.game_renderer import GameRenderer
from config.constants import *

class P2PHost:
    def __init__(self, room_code, player_name):
        self.room_code = room_code
        self.player_name = player_name
        self.players = {0: player_name}
        self.client_sockets = {}
        self.server_socket = None
        self.running = False
        self.game = None
        self.game_started = False
        self.player_actions = {}
        self.action_lock = threading.Lock()
        
    def start(self, port=12345):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(3)
            self.running = True
            
            print(f"Host started on port {port}")
            
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True, port
        except Exception as e:
            print(f"Failed to start host: {e}")
            return False, None
    
    def accept_connections(self):
        while self.running and len(self.players) < 4:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, addr = self.server_socket.accept()
                
                data = client_socket.recv(1024).decode()
                msg = json.loads(data)
                
                if msg['type'] == 'join' and msg['room_code'] == self.room_code:
                    player_id = len(self.players)
                    player_name = msg['player_name']
                    
                    self.players[player_id] = player_name
                    self.client_sockets[player_id] = client_socket
                    
                    response = {
                        'type': 'joined',
                        'player_id': player_id,
                        'players': self.players
                    }
                    client_socket.send((json.dumps(response) + '\n').encode())
                    
                    self.broadcast_room_update()
                    
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, player_id))
                    client_thread.daemon = True
                    client_thread.start()
                    
                    print(f"Player {player_id} ({player_name}) joined. Total players: {len(self.players)}")
                    
                    if len(self.players) == 4:
                        time.sleep(0.5)
                        self.start_game()
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, player_id):
        buffer = ""
        try:
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    msg = json.loads(line)
                    
                    if msg['type'] == 'action':
                        with self.action_lock:
                            self.player_actions[player_id] = msg['action']
                        print(f"Received action from player {player_id}: {msg['action']}")
                        
        except Exception as e:
            print(f"Client {player_id} disconnected: {e}")
        finally:
            if player_id in self.client_sockets:
                del self.client_sockets[player_id]
            if player_id in self.players:
                del self.players[player_id]
    
    def broadcast_room_update(self):
        msg = {
            'type': 'room_update',
            'players': self.players
        }
        self.broadcast(msg)
    
    def start_game(self):
        num_players = len(self.players)
        self.game = Game(num_players=num_players)
        self.game_started = True
        print(f"Host: Starting game with {num_players} players:", self.players)
        
        msg = {'type': 'game_start'}
        self.broadcast(msg)
    
    def broadcast(self, msg):
        data = json.dumps(msg) + '\n'
        for client_socket in self.client_sockets.values():
            try:
                client_socket.send(data.encode())
            except:
                pass
    
    def update_game(self, dt):
        if not self.game_started or not self.game:
            return
        
        try:
            with self.action_lock:
                actions_to_process = self.player_actions.copy()
                self.player_actions.clear()
            
            for player_id, action in actions_to_process.items():
                if player_id < len(self.game.players):
                    player = self.game.players[player_id]
                    print(f"Processing action for player {player_id}: {action}")
                    if action == 'hit':
                        result = player.hit_ball(self.game.ball)
                        print(f"  Hit result: {result}")
                    elif action == 'dodge':
                        player.start_dodge()
                        print(f"  Dodge started")
            
            
            self.game.update(dt)
            
            game_state = self.create_game_state()
            msg = {
                'type': 'game_state',
                'state': game_state
            }
            self.broadcast(msg)
        except Exception as e:
            print(f"Error updating game: {e}")
            import traceback
            traceback.print_exc()
    
    def create_game_state(self):
        players_data = []
        for i, player in enumerate(self.game.players):
            players_data.append({
                'id': i,
                'name': self.players.get(i, f'Player {i+1}'),
                'x': player.x,
                'y': player.y,
                'angle': player.angle,
                'state': player.state.value,
                'color': player.color,
                'stick_angle': player.stick_angle,
                'swing_progress': player.swing_progress,
                'hit_cooldown': player.hit_cooldown
            })
        
        ball_data = {
            'x': self.game.ball.x,
            'y': self.game.ball.y,
            'angle': self.game.ball.angle,
            'speed': self.game.ball.speed,
            'countdown': self.game.ball.countdown,
            'is_active': self.game.ball.is_active,
            'spawn_timer': self.game.ball.spawn_timer
        }
        
        return {
            'players': players_data,
            'ball': ball_data,
            'game_over': self.game.game_over,
            'winner_id': self.game.winner.id if self.game.winner else None
        }
    
    def handle_host_action(self, action):
        if self.game_started and self.game and len(self.game.players) > 0:
            player = self.game.players[0]
            if action == 'hit':
                player.hit_ball(self.game.ball)
            elif action == 'dodge':
                player.start_dodge()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for socket in self.client_sockets.values():
            socket.close()


class P2PClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_id = None
        self.players = {}
        self.game_state = None
        self.game_started = False
        
    def connect(self, host_ip, port, room_code, player_name):
        try:
            print(f"Attempting to connect to {host_ip}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host_ip, port))
            print("Connected!")
            
            msg = {
                'type': 'join',
                'room_code': room_code,
                'player_name': player_name
            }
            self.socket.send(json.dumps(msg).encode())
            print("Join request sent")
            
            data = self.socket.recv(1024).decode()
            print(f"Received: {data}")
            response = json.loads(data.strip())
            
            if response['type'] == 'joined':
                self.player_id = response['player_id']
                self.players = {int(k): v for k, v in response['players'].items()}
                self.connected = True
                print(f"Joined as player {self.player_id}")
                
                self.socket.settimeout(None)
                
                recv_thread = threading.Thread(target=self.receive_messages)
                recv_thread.daemon = True
                recv_thread.start()
                
                return True, self.player_id
            else:
                print(f"Join failed: {response}")
            
        except socket.timeout:
            print("Connection timeout - Host not responding")
            return False, None
        except ConnectionRefusedError:
            print("Connection refused - Cannot connect to host")
            return False, None
        except Exception as e:
            print(f"Failed to connect: {e}")
            import traceback
            traceback.print_exc()
            return False, None
        
        return False, None
    
    def receive_messages(self):
        buffer = ""
        try:
            while self.connected:
                data = self.socket.recv(4096).decode()
                if not data:
                    print("Connection closed by host")
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        msg = json.loads(line)
                        
                        if msg['type'] == 'room_update':
                            self.players = {int(k): v for k, v in msg['players'].items()}
                        elif msg['type'] == 'game_start':
                            self.game_started = True
                            print("Game started!")
                        elif msg['type'] == 'game_state':
                            self.game_state = msg['state']
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}, line: {line}")
                        continue
                        
        except socket.timeout:
            print("Connection lost: timed out")
        except ConnectionResetError:
            print("Connection lost: connection reset by host")
        except Exception as e:
            print(f"Connection lost: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.connected = False
    
    def send_action(self, action):
        if self.connected:
            msg = {
                'type': 'action',
                'action': action
            }
            try:
                self.socket.send((json.dumps(msg) + '\n').encode())
            except:
                self.connected = False
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            self.socket.close()


class P2PGameController:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge - P2P")
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.mode = None
        self.host = None
        self.client = None
        self.game_renderer = GameRenderer()
        
        self.current_view = "menu"
        self.room_code = None
        self.player_name = ""
        self.host_ip = ""
        self.error_message = None
        
        self.input_active = None
        
    def generate_room_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        font_title = pygame.font.Font(None, 64)
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        title = font_title.render("HIT & DODGE - P2P", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        name_label = font_normal.render("Your name:", True, BLACK)
        self.screen.blit(name_label, (100, 150))
        
        name_box = pygame.Rect(100, 190, 600, 40)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'name' else GRAY, name_box, 2)
        name_text = font_normal.render(self.player_name, True, BLACK)
        self.screen.blit(name_text, (110, 195))
        
        host_button = pygame.Rect(100, 270, 280, 60)
        pygame.draw.rect(self.screen, GREEN, host_button)
        host_text = font_normal.render("CREATE ROOM (HOST)", True, WHITE)
        self.screen.blit(host_text, (host_button.x + 20, host_button.y + 15))
        
        join_label = font_normal.render("Or join a room:", True, BLACK)
        self.screen.blit(join_label, (420, 270))
        
        ip_label = font_small.render("Host IP:", True, BLACK)
        self.screen.blit(ip_label, (420, 310))
        
        ip_box = pygame.Rect(420, 340, 280, 35)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'ip' else GRAY, ip_box, 2)
        ip_text = font_small.render(self.host_ip, True, BLACK)
        self.screen.blit(ip_text, (430, 345))
        
        code_label = font_small.render("Room code:", True, BLACK)
        self.screen.blit(code_label, (420, 390))
        
        code_box = pygame.Rect(420, 420, 280, 35)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'code' else GRAY, code_box, 2)
        code_text = font_small.render(self.room_code or "", True, BLACK)
        self.screen.blit(code_text, (430, 425))
        
        join_button = pygame.Rect(420, 475, 280, 50)
        pygame.draw.rect(self.screen, BLUE, join_button)
        join_text = font_normal.render("JOIN", True, WHITE)
        self.screen.blit(join_text, (join_button.x + 90, join_button.y + 10))
        
        self.host_button_rect = host_button
        self.join_button_rect = join_button
        self.name_box_rect = name_box
        self.ip_box_rect = ip_box
        self.code_box_rect = code_box
        
        if self.error_message:
            error_font = pygame.font.Font(None, 24)
            error_text = error_font.render(self.error_message, True, RED)
            self.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 550))
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return local_ip
            except:
                return "Unknown"
    
    def draw_waiting_room(self):
        self.screen.fill(WHITE)
        
        font_title = pygame.font.Font(None, 48)
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        title = font_title.render(f"Room: {self.room_code}", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        if self.mode == 'host':
            local_ip = self.get_local_ip()
            
            ip_label = font_small.render("Share this info with friends:", True, GRAY)
            self.screen.blit(ip_label, (SCREEN_WIDTH // 2 - ip_label.get_width() // 2, 100))
            
            ip_text = font_normal.render(f"IP: {local_ip}", True, BLUE)
            self.screen.blit(ip_text, (SCREEN_WIDTH // 2 - ip_text.get_width() // 2, 130))
            
            code_text = font_normal.render(f"Room Code: {self.room_code}", True, GREEN)
            self.screen.blit(code_text, (SCREEN_WIDTH // 2 - code_text.get_width() // 2, 170))
            
            guide = font_small.render("Friends enter IP and room code to join", True, GRAY)
            self.screen.blit(guide, (SCREEN_WIDTH // 2 - guide.get_width() // 2, 210))
        
        players_label = font_normal.render("Players:", True, BLACK)
        self.screen.blit(players_label, (100, 220))
        
        y = 270
        players = self.host.players if self.mode == 'host' else self.client.players
        for player_id, player_name in sorted(players.items()):
            color = PLAYER_COLORS[player_id]
            player_text = font_normal.render(f"{player_id + 1}. {player_name}", True, color)
            self.screen.blit(player_text, (120, y))
            y += 40
        
        count_text = font_normal.render(f"{len(players)}/4 players", True, BLACK)
        self.screen.blit(count_text, (100, y + 20))
        
        if len(players) < 4:
            waiting_text = font_normal.render("Waiting for players...", True, GRAY)
            self.screen.blit(waiting_text, (SCREEN_WIDTH // 2 - waiting_text.get_width() // 2, 480))
            
            if self.mode == 'host' and len(players) >= 2:
                start_hint = font_small.render("Press SPACE to start game (no need to wait for 4 players)", True, GREEN)
                self.screen.blit(start_hint, (SCREEN_WIDTH // 2 - start_hint.get_width() // 2, 520))
    
    def handle_menu_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.name_box_rect.collidepoint(event.pos):
                self.input_active = 'name'
            elif self.ip_box_rect.collidepoint(event.pos):
                self.input_active = 'ip'
            elif self.code_box_rect.collidepoint(event.pos):
                self.input_active = 'code'
            elif self.host_button_rect.collidepoint(event.pos):
                self.create_host()
            elif self.join_button_rect.collidepoint(event.pos):
                self.join_room()
            else:
                self.input_active = None
                
        elif event.type == pygame.KEYDOWN:
            if self.input_active == 'name':
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.input_active = None
                elif len(self.player_name) < 20:
                    self.player_name += event.unicode
                    
            elif self.input_active == 'ip':
                if event.key == pygame.K_BACKSPACE:
                    self.host_ip = self.host_ip[:-1]
                elif event.key == pygame.K_RETURN:
                    self.input_active = None
                elif len(self.host_ip) < 15:
                    self.host_ip += event.unicode
                    
            elif self.input_active == 'code':
                if event.key == pygame.K_BACKSPACE:
                    self.room_code = self.room_code[:-1] if self.room_code else ""
                elif event.key == pygame.K_RETURN:
                    self.input_active = None
                elif self.room_code and len(self.room_code) < 4:
                    self.room_code += event.unicode.upper()
                elif not self.room_code:
                    self.room_code = event.unicode.upper()
    
    def create_host(self):
        if not self.player_name:
            return
        
        self.room_code = self.generate_room_code()
        self.mode = 'host'
        self.host = P2PHost(self.room_code, self.player_name)
        success, port = self.host.start()
        
        if success:
            self.current_view = "waiting"
    
    def join_room(self):
        if not self.player_name or not self.host_ip or not self.room_code:
            self.error_message = "Please enter all information!"
            return
        
        self.error_message = "Connecting..."
        self.mode = 'client'
        self.client = P2PClient()
        success, player_id = self.client.connect(self.host_ip, 12345, self.room_code, self.player_name)
        
        if success:
            self.current_view = "waiting"
            self.error_message = None
        else:
            self.error_message = "Cannot connect! Check IP and room code."
            self.mode = None
            self.client = None
    
    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            action = None
            
            if event.key == pygame.K_SPACE:
                action = 'hit'
            elif event.key == pygame.K_RETURN:
                action = 'dodge'
            
            if action:
                if self.mode == 'host':
                    self.host.handle_host_action(action)
                elif self.mode == 'client':
                    self.client.send_action(action)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    if self.current_view == "menu":
                        self.handle_menu_input(event)
                    elif self.current_view == "waiting":
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            if self.mode == 'host' and len(self.host.players) >= 2 and not self.host.game_started:
                                self.host.start_game()
                    elif self.current_view == "game":
                        self.handle_game_input(event)
            
            if self.current_view == "waiting":
                if self.mode == 'host' and self.host.game_started:
                    self.current_view = "game"
                elif self.mode == 'client' and self.client.game_started:
                    self.current_view = "game"
            
            if self.current_view == "game":
                if self.mode == 'host':
                    self.host.update_game(dt)
            
            if self.current_view == "menu":
                self.draw_menu()
            elif self.current_view == "waiting":
                self.draw_waiting_room()
            elif self.current_view == "game":
                if self.mode == 'host' and self.host.game:
                    game_state = self.host.create_game_state()
                    self.game_renderer.render_online_game(self.screen, game_state, 0)
                elif self.mode == 'client':
                    self.draw_client_game()
            
            pygame.display.flip()
        
        if self.host:
            self.host.stop()
        if self.client:
            self.client.disconnect()
        
        pygame.quit()
        sys.exit()
    
    def draw_client_game(self):
        state = self.client.game_state
        if not state:
            self.screen.fill(WHITE)
            font = pygame.font.Font(None, 48)
            text = font.render("Loading game...", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            return
        
        self.game_renderer.render_online_game(self.screen, state, self.client.player_id)


def main():
    controller = P2PGameController()
    controller.run()


if __name__ == "__main__":
    main()
