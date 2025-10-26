"""
Hit & Dodge - Peer-to-Peer Multiplayer
Một người tạo phòng làm host, người khác join vào qua code phòng
Không cần server riêng!
"""
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
    """Host game - người tạo phòng"""
    def __init__(self, room_code, player_name):
        self.room_code = room_code
        self.player_name = player_name
        self.players = {0: player_name}  # player_id -> name
        self.client_sockets = {}  # player_id -> socket
        self.server_socket = None
        self.running = False
        self.game = None
        self.game_started = False
        self.player_actions = {}  # player_id -> latest action
        
    def start(self, port=12345):
        """Khởi động host server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to all interfaces (0.0.0.0) to accept connections from LAN
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(3)  # Chấp nhận tối đa 3 người join (host + 3 = 4)
            self.running = True
            
            print(f"Host started on port {port}")
            
            # Thread để chấp nhận kết nối
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True, port
        except Exception as e:
            print(f"Failed to start host: {e}")
            return False, None
    
    def accept_connections(self):
        """Chấp nhận kết nối từ các người chơi"""
        while self.running and len(self.players) < 4:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, addr = self.server_socket.accept()
                
                # Nhận tên người chơi
                data = client_socket.recv(1024).decode()
                msg = json.loads(data)
                
                if msg['type'] == 'join' and msg['room_code'] == self.room_code:
                    player_id = len(self.players)
                    player_name = msg['player_name']
                    
                    self.players[player_id] = player_name
                    self.client_sockets[player_id] = client_socket
                    
                    # Gửi xác nhận
                    response = {
                        'type': 'joined',
                        'player_id': player_id,
                        'players': self.players
                    }
                    client_socket.send((json.dumps(response) + '\n').encode())
                    
                    # Broadcast cập nhật phòng
                    self.broadcast_room_update()
                    
                    # Bắt đầu nhận tin nhắn từ client này
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, player_id))
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # Nếu đủ 4 người, bắt đầu game
                    if len(self.players) == 4:
                        time.sleep(0.5)  # Đợi chút để mọi người nhận được room update
                        self.start_game()
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, player_id):
        """Xử lý tin nhắn từ một client"""
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
                        self.player_actions[player_id] = msg['action']
                        
        except Exception as e:
            print(f"Client {player_id} disconnected: {e}")
        finally:
            if player_id in self.client_sockets:
                del self.client_sockets[player_id]
            if player_id in self.players:
                del self.players[player_id]
    
    def broadcast_room_update(self):
        """Gửi cập nhật phòng cho tất cả người chơi"""
        msg = {
            'type': 'room_update',
            'players': self.players
        }
        self.broadcast(msg)
    
    def start_game(self):
        """Bắt đầu game"""
        self.game = Game()
        self.game_started = True
        
        msg = {'type': 'game_start'}
        self.broadcast(msg)
    
    def broadcast(self, msg):
        """Gửi tin nhắn cho tất cả clients"""
        data = json.dumps(msg) + '\n'
        for client_socket in self.client_sockets.values():
            try:
                client_socket.send(data.encode())
            except:
                pass
    
    def update_game(self, dt):
        """Cập nhật game và gửi state cho clients"""
        if not self.game_started or not self.game:
            return
        
        # Xử lý actions của người chơi
        for player_id, action in self.player_actions.items():
            if player_id < len(self.game.players):
                player = self.game.players[player_id]
                if action == 'hit':
                    player.hit_ball(self.game.ball)
                elif action == 'dodge':
                    player.start_dodge()
        self.player_actions.clear()
        
        # Xử lý action của host (player 0)
        # (Sẽ được xử lý từ controller)
        
        # Update game
        self.game.update(dt)
        
        # Tạo game state và broadcast
        game_state = self.create_game_state()
        msg = {
            'type': 'game_state',
            'state': game_state
        }
        self.broadcast(msg)
    
    def create_game_state(self):
        """Tạo game state để gửi cho clients"""
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
                'swing_progress': player.swing_progress
            })
        
        ball_data = {
            'x': self.game.ball.x,
            'y': self.game.ball.y,
            'angle': self.game.ball.angle,
            'speed': self.game.ball.speed,
            'countdown': self.game.ball.countdown
        }
        
        return {
            'players': players_data,
            'ball': ball_data,
            'game_over': self.game.game_over,
            'winner_id': self.game.winner.id if self.game.winner else None
        }
    
    def handle_host_action(self, action):
        """Xử lý action của host (player 0)"""
        if self.game_started and self.game and len(self.game.players) > 0:
            player = self.game.players[0]
            if action == 'hit':
                player.hit_ball(self.game.ball)
            elif action == 'dodge':
                player.start_dodge()
    
    def stop(self):
        """Dừng host"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for socket in self.client_sockets.values():
            socket.close()


class P2PClient:
    """Client - người join vào phòng"""
    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_id = None
        self.players = {}
        self.game_state = None
        self.game_started = False
        
    def connect(self, host_ip, port, room_code, player_name):
        """Kết nối đến host"""
        try:
            print(f"Attempting to connect to {host_ip}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((host_ip, port))
            print("Connected!")
            
            # Gửi yêu cầu join
            msg = {
                'type': 'join',
                'room_code': room_code,
                'player_name': player_name
            }
            self.socket.send(json.dumps(msg).encode())
            print("Join request sent")
            
            # Nhận xác nhận
            data = self.socket.recv(1024).decode()
            print(f"Received: {data}")
            response = json.loads(data.strip())
            
            if response['type'] == 'joined':
                self.player_id = response['player_id']
                self.players = {int(k): v for k, v in response['players'].items()}
                self.connected = True
                print(f"Joined as player {self.player_id}")
                
                # Bắt đầu nhận tin nhắn
                recv_thread = threading.Thread(target=self.receive_messages)
                recv_thread.daemon = True
                recv_thread.start()
                
                return True, self.player_id
            else:
                print(f"Join failed: {response}")
            
        except socket.timeout:
            print("Connection timeout - Host không phản hồi")
            return False, None
        except ConnectionRefusedError:
            print("Connection refused - Không thể kết nối đến host")
            return False, None
        except Exception as e:
            print(f"Failed to connect: {e}")
            import traceback
            traceback.print_exc()
            return False, None
        
        return False, None
    
    def receive_messages(self):
        """Nhận tin nhắn từ host"""
        buffer = ""
        try:
            while self.connected:
                data = self.socket.recv(4096).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    msg = json.loads(line)
                    
                    if msg['type'] == 'room_update':
                        self.players = {int(k): v for k, v in msg['players'].items()}
                    elif msg['type'] == 'game_start':
                        self.game_started = True
                    elif msg['type'] == 'game_state':
                        self.game_state = msg['state']
                        
        except Exception as e:
            print(f"Connection lost: {e}")
        finally:
            self.connected = False
    
    def send_action(self, action):
        """Gửi action cho host"""
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
        """Ngắt kết nối"""
        self.connected = False
        if self.socket:
            self.socket.close()


class P2PGameController:
    """Controller cho P2P multiplayer"""
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hit & Dodge - P2P")
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.mode = None  # 'host' hoặc 'client'
        self.host = None
        self.client = None
        self.game_renderer = GameRenderer()
        
        self.current_view = "menu"  # "menu", "waiting", "game"
        self.room_code = None
        self.player_name = ""
        self.host_ip = ""
        self.error_message = None  # Thông báo lỗi
        
        # UI state
        self.input_active = None  # 'name', 'ip', 'code'
        
    def generate_room_code(self):
        """Tạo mã phòng 4 ký tự"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    def draw_menu(self):
        """Vẽ menu chính"""
        self.screen.fill(WHITE)
        
        font_title = pygame.font.Font(None, 64)
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title = font_title.render("HIT & DODGE - P2P", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Player name input
        name_label = font_normal.render("Tên của bạn:", True, BLACK)
        self.screen.blit(name_label, (100, 150))
        
        name_box = pygame.Rect(100, 190, 600, 40)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'name' else GRAY, name_box, 2)
        name_text = font_normal.render(self.player_name, True, BLACK)
        self.screen.blit(name_text, (110, 195))
        
        # Host button
        host_button = pygame.Rect(100, 270, 280, 60)
        pygame.draw.rect(self.screen, GREEN, host_button)
        host_text = font_normal.render("TẠO PHÒNG (HOST)", True, WHITE)
        self.screen.blit(host_text, (host_button.x + 20, host_button.y + 15))
        
        # Join section
        join_label = font_normal.render("Hoặc tham gia phòng:", True, BLACK)
        self.screen.blit(join_label, (420, 270))
        
        # Host IP input
        ip_label = font_small.render("IP của host:", True, BLACK)
        self.screen.blit(ip_label, (420, 310))
        
        ip_box = pygame.Rect(420, 340, 280, 35)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'ip' else GRAY, ip_box, 2)
        ip_text = font_small.render(self.host_ip, True, BLACK)
        self.screen.blit(ip_text, (430, 345))
        
        # Room code input
        code_label = font_small.render("Mã phòng:", True, BLACK)
        self.screen.blit(code_label, (420, 390))
        
        code_box = pygame.Rect(420, 420, 280, 35)
        pygame.draw.rect(self.screen, BLUE if self.input_active == 'code' else GRAY, code_box, 2)
        code_text = font_small.render(self.room_code or "", True, BLACK)
        self.screen.blit(code_text, (430, 425))
        
        # Join button
        join_button = pygame.Rect(420, 475, 280, 50)
        pygame.draw.rect(self.screen, BLUE, join_button)
        join_text = font_normal.render("THAM GIA", True, WHITE)
        self.screen.blit(join_text, (join_button.x + 70, join_button.y + 10))
        
        # Store rects for click detection
        self.host_button_rect = host_button
        self.join_button_rect = join_button
        self.name_box_rect = name_box
        self.ip_box_rect = ip_box
        self.code_box_rect = code_box
        
        # Draw error message if any
        if self.error_message:
            error_font = pygame.font.Font(None, 24)
            error_text = error_font.render(self.error_message, True, RED)
            self.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 550))
        
    def get_local_ip(self):
        """Lấy IP address của máy trong mạng LAN"""
        try:
            # Tạo socket để lấy IP thật (không phải 127.0.0.1)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                # Fallback method
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return local_ip
            except:
                return "Unknown"
    
    def draw_waiting_room(self):
        """Vẽ phòng chờ"""
        self.screen.fill(WHITE)
        
        font_title = pygame.font.Font(None, 48)
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        title = font_title.render(f"Phòng: {self.room_code}", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        if self.mode == 'host':
            # Hiển thị IP để share
            local_ip = self.get_local_ip()
            
            ip_label = font_small.render("Chia sẻ thông tin này với bạn bè:", True, GRAY)
            self.screen.blit(ip_label, (SCREEN_WIDTH // 2 - ip_label.get_width() // 2, 100))
            
            ip_text = font_normal.render(f"IP: {local_ip}", True, BLUE)
            self.screen.blit(ip_text, (SCREEN_WIDTH // 2 - ip_text.get_width() // 2, 130))
            
            code_text = font_normal.render(f"Mã phòng: {self.room_code}", True, GREEN)
            self.screen.blit(code_text, (SCREEN_WIDTH // 2 - code_text.get_width() // 2, 170))
            
            # Hướng dẫn cho bạn bè
            guide = font_small.render("Bạn bè nhập IP và mã phòng để tham gia", True, GRAY)
            self.screen.blit(guide, (SCREEN_WIDTH // 2 - guide.get_width() // 2, 210))
        
        # Hiển thị danh sách người chơi
        players_label = font_normal.render("Người chơi:", True, BLACK)
        self.screen.blit(players_label, (100, 220))
        
        y = 270
        players = self.host.players if self.mode == 'host' else self.client.players
        for player_id, player_name in sorted(players.items()):
            color = PLAYER_COLORS[player_id]
            player_text = font_normal.render(f"{player_id + 1}. {player_name}", True, color)
            self.screen.blit(player_text, (120, y))
            y += 40
        
        # Hiển thị số người chơi
        count_text = font_normal.render(f"{len(players)}/4 người chơi", True, BLACK)
        self.screen.blit(count_text, (100, y + 20))
        
        if len(players) < 4:
            waiting_text = font_normal.render("Đang chờ người chơi...", True, GRAY)
            self.screen.blit(waiting_text, (SCREEN_WIDTH // 2 - waiting_text.get_width() // 2, 500))
    
    def handle_menu_input(self, event):
        """Xử lý input trong menu"""
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
        """Tạo phòng host"""
        if not self.player_name:
            return
        
        self.room_code = self.generate_room_code()
        self.mode = 'host'
        self.host = P2PHost(self.room_code, self.player_name)
        success, port = self.host.start()
        
        if success:
            self.current_view = "waiting"
    
    def join_room(self):
        """Tham gia phòng"""
        if not self.player_name or not self.host_ip or not self.room_code:
            self.error_message = "Vui lòng nhập đầy đủ thông tin!"
            return
        
        self.error_message = "Đang kết nối..."
        self.mode = 'client'
        self.client = P2PClient()
        success, player_id = self.client.connect(self.host_ip, 12345, self.room_code, self.player_name)
        
        if success:
            self.current_view = "waiting"
            self.error_message = None
        else:
            self.error_message = "Không thể kết nối! Kiểm tra IP và mã phòng."
            self.mode = None
            self.client = None
    
    def handle_game_input(self, event):
        """Xử lý input trong game"""
        if event.type == pygame.KEYDOWN:
            action = None
            
            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                action = 'hit'
            elif event.key in [pygame.K_DOWN, pygame.K_RETURN]:
                action = 'dodge'
            
            if action:
                if self.mode == 'host':
                    self.host.handle_host_action(action)
                elif self.mode == 'client':
                    self.client.send_action(action)
    
    def run(self):
        """Main loop"""
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
                    elif self.current_view == "game":
                        self.handle_game_input(event)
            
            # Update
            if self.current_view == "waiting":
                if self.mode == 'host' and self.host.game_started:
                    self.current_view = "game"
                elif self.mode == 'client' and self.client.game_started:
                    self.current_view = "game"
            
            if self.current_view == "game":
                if self.mode == 'host':
                    self.host.update_game(dt)
            
            # Draw
            if self.current_view == "menu":
                self.draw_menu()
            elif self.current_view == "waiting":
                self.draw_waiting_room()
            elif self.current_view == "game":
                if self.mode == 'host' and self.host.game:
                    self.game_renderer.render(self.screen, self.host.game)
                elif self.mode == 'client' and self.client.game_state:
                    self.draw_client_game()
            
            pygame.display.flip()
        
        # Cleanup
        if self.host:
            self.host.stop()
        if self.client:
            self.client.disconnect()
        
        pygame.quit()
        sys.exit()
    
    def draw_client_game(self):
        """Vẽ game cho client (từ game state)"""
        self.screen.fill(WHITE)
        
        state = self.client.game_state
        if not state:
            return
        
        # Draw planet
        pygame.draw.circle(self.screen, DARK_GRAY, PLANET_CENTER, PLANET_RADIUS, 3)
        
        # Draw ball
        ball = state['ball']
        if ball['countdown'] > 0:
            # Draw countdown
            font = pygame.font.Font(None, 48)
            countdown_text = str(int(ball['countdown']) + 1)
            text = font.render(countdown_text, True, RED)
            text_rect = text.get_rect(center=(int(ball['x']), int(ball['y'])))
            self.screen.blit(text, text_rect)
        else:
            pygame.draw.circle(self.screen, BLACK, (int(ball['x']), int(ball['y'])), BALL_RADIUS)
        
        # Draw players
        from models.player_state import PlayerState
        import math
        
        for p in state['players']:
            if p['state'] == PlayerState.ELIMINATED.value:
                continue
            
            x, y = int(p['x']), int(p['y'])
            color = tuple(p['color'])
            
            if p['state'] == PlayerState.DODGING.value:
                pygame.draw.circle(self.screen, color, (x, y), PLAYER_RADIUS // 2)
            else:
                pygame.draw.circle(self.screen, color, (x, y), PLAYER_RADIUS)
                
                # Draw stick
                stick_length = 35
                if p['id'] == 0:
                    base_angle = 0
                elif p['id'] == 1:
                    base_angle = math.pi/2
                elif p['id'] == 2:
                    base_angle = math.pi
                else:
                    base_angle = -math.pi/2
                
                stick_angle = base_angle + math.radians(p['stick_angle'])
                stick_end_x = p['x'] + stick_length * math.cos(stick_angle)
                stick_end_y = p['y'] + stick_length * math.sin(stick_angle)
                pygame.draw.line(self.screen, BLACK, (x, y), 
                               (int(stick_end_x), int(stick_end_y)), 4)
        
        # Draw game over
        if state['game_over']:
            font = pygame.font.Font(None, 64)
            winner_id = state['winner_id']
            if winner_id is not None:
                if winner_id == self.client.player_id:
                    text = font.render("Bạn thắng!", True, GREEN)
                else:
                    winner_name = self.client.players.get(winner_id, f'Player {winner_id+1}')
                    text = font.render(f"{winner_name} thắng!", True, RED)
            else:
                text = font.render("Hòa!", True, BLACK)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(text, text_rect)


def main():
    controller = P2PGameController()
    controller.run()


if __name__ == "__main__":
    main()
