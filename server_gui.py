"""
Server GUI for Hit & Dodge multiplayer
Shows active rooms, players, and server statistics
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import os
from datetime import datetime
from network.server import GameServer

class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hit & Dodge Server")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Get current working directory
        self.game_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.server = None
        self.server_thread = None
        self.running = False
        
        self.setup_ui()
        
        # Auto-start server after UI is ready
        self.root.after(100, self.start_server)
        
        self.update_display()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(
            title_frame, 
            text="Hit & Dodge Game Server", 
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack()
        
        # Server status (no control buttons)
        status_frame = tk.Frame(self.root, bg='#f0f0f0')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Server Status: Starting...",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='orange'
        )
        self.status_label.pack()
        
        # Server info
        self.info_label = tk.Label(
            status_frame,
            text=self.get_server_info_text(),
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='blue'
        )
        self.info_label.pack(pady=(5, 0))
        
        # Main content area with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Rooms tab
        rooms_frame = ttk.Frame(notebook)
        notebook.add(rooms_frame, text="Active Rooms")
        self.setup_rooms_tab(rooms_frame)
        
        # Room Management tab
        management_frame = ttk.Frame(notebook)
        notebook.add(management_frame, text="Create/Join Room")
        self.setup_management_tab(management_frame)
        
        # Statistics tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        self.setup_stats_tab(stats_frame)
    
    def setup_rooms_tab(self, parent):
        """Setup the rooms display tab"""
        # Rooms header
        header_frame = tk.Frame(parent)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(
            header_frame,
            text="Active Rooms",
            font=('Arial', 12, 'bold')
        ).pack(side='left')
        
        self.refresh_button = tk.Button(
            header_frame,
            text="Refresh",
            command=self.refresh_rooms,
            bg='#2196F3',
            fg='white',
            width=10
        )
        self.refresh_button.pack(side='right')
        
        # Rooms display area
        rooms_container = tk.Frame(parent)
        rooms_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollable frame for rooms
        canvas = tk.Canvas(rooms_container, bg='white')
        scrollbar = ttk.Scrollbar(rooms_container, orient="vertical", command=canvas.yview)
        self.rooms_frame = tk.Frame(canvas, bg='white')
        
        self.rooms_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.rooms_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_management_tab(self, parent):
        """Setup the room management tab"""
        # Title
        title_label = tk.Label(
            parent,
            text="Room Management",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=20)
        
        # Create Room section
        create_frame = tk.LabelFrame(
            parent,
            text="Create New Room",
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=20
        )
        create_frame.pack(fill='x', padx=50, pady=20)
        
        tk.Label(
            create_frame,
            text="Player Name:",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        self.create_name_entry = tk.Entry(
            create_frame,
            font=('Arial', 12),
            width=30
        )
        self.create_name_entry.pack(fill='x', pady=(0, 10))
        self.create_name_entry.insert(0, "Host Player")
        
        self.create_button = tk.Button(
            create_frame,
            text="🏠 Create New Room",
            command=self.create_room_local,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2
        )
        self.create_button.pack(fill='x')
        
        # Join Room section
        join_frame = tk.LabelFrame(
            parent,
            text="Join Existing Room",
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=20
        )
        join_frame.pack(fill='x', padx=50, pady=20)
        
        # Server IP
        ip_frame = tk.Frame(join_frame)
        ip_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            ip_frame,
            text="Server IP Address:",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.server_ip_entry = tk.Entry(
            ip_frame,
            font=('Arial', 12),
            width=30
        )
        self.server_ip_entry.pack(fill='x', pady=(5, 0))
        self.server_ip_entry.insert(0, "localhost")
        
        # Player Name
        name_frame = tk.Frame(join_frame)
        name_frame.pack(fill='x', pady=(10, 10))
        
        tk.Label(
            name_frame,
            text="Player Name:",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.join_name_entry = tk.Entry(
            name_frame,
            font=('Arial', 12),
            width=30
        )
        self.join_name_entry.pack(fill='x', pady=(5, 0))
        self.join_name_entry.insert(0, "Player")
        
        room_frame = tk.Frame(join_frame)
        room_frame.pack(fill='x', pady=(10, 10))
        
        tk.Label(
            room_frame,
            text="Room ID (4 characters):",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        self.room_id_entry = tk.Entry(
            room_frame,
            font=('Arial', 14, 'bold'),
            width=10,
            justify='center'
        )
        self.room_id_entry.pack(pady=(5, 0))
        
        self.join_button = tk.Button(
            join_frame,
            text="🚪 Join Room",
            command=self.join_room_local,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2
        )
        self.join_button.pack(fill='x', pady=(10, 0))
        
        # Status display
        self.management_status = tk.Label(
            parent,
            text="",
            font=('Arial', 10),
            fg='blue'
        )
        self.management_status.pack(pady=10)
    
    def setup_stats_tab(self, parent):
        """Setup the statistics tab"""
        # Title
        title_label = tk.Label(
            parent,
            text="Server Statistics",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=20)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(
            parent,
            text="Server Information",
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=20
        )
        stats_frame.pack(fill='x', padx=50, pady=20)
        
        self.total_rooms_label = tk.Label(
            stats_frame,
            text="Total Rooms: 0",
            font=('Arial', 12)
        )
        self.total_rooms_label.pack(anchor='w', pady=5)
        
        self.total_players_label = tk.Label(
            stats_frame,
            text="Total Players: 0",
            font=('Arial', 12)
        )
        self.total_players_label.pack(anchor='w', pady=5)
        
        self.uptime_label = tk.Label(
            stats_frame,
            text="Server Uptime: 0 seconds",
            font=('Arial', 12)
        )
        self.uptime_label.pack(anchor='w', pady=5)
    
    def create_room_local(self):
        """Create a new room and launch the game client"""
        try:
            import subprocess
            player_name = self.create_name_entry.get().strip()
            if not player_name:
                player_name = "Host Player"
            
            # Launch the main client with create room mode
            subprocess.Popen([
                "python", "main.py", "--create", "--name", player_name
            ], cwd=self.game_dir)
            
            self.management_status.config(
                text=f"Launched game client for {player_name} (Create Room)",
                fg='green'
            )
        except Exception as e:
            self.management_status.config(
                text=f"Error launching client: {str(e)}",
                fg='red'
            )
    
    def join_room_local(self):
        """Join an existing room and launch the game client"""
        try:
            import subprocess
            server_ip = self.server_ip_entry.get().strip()
            player_name = self.join_name_entry.get().strip()
            room_id = self.room_id_entry.get().strip().upper()
            
            if not server_ip:
                server_ip = "localhost"
            
            if not player_name:
                player_name = "Player"
            
            if len(room_id) != 4:
                self.management_status.config(
                    text="Room ID must be exactly 4 characters",
                    fg='red'
                )
                return
            
            # Launch the main client with join room mode
            subprocess.Popen([
                "python", "main.py", "--join", room_id, "--name", player_name, "--host", server_ip
            ], cwd=self.game_dir)
            
            self.management_status.config(
                text=f"Launched game client for {player_name} (Join Room {room_id} on {server_ip})",
                fg='green'
            )
        except Exception as e:
            self.management_status.config(
                text=f"Error launching client: {str(e)}",
                fg='red'
            )
    
    def setup_logs_tab(self, parent):
        """Setup the logs display tab"""
        tk.Label(
            parent,
            text="Server Logs",
            font=('Arial', 12, 'bold')
        ).pack(anchor='w', padx=5, pady=5)
        
        # Log display area
        log_frame = tk.Frame(parent)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Log controls
        log_controls = tk.Frame(parent)
        log_controls.pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            log_controls,
            text="Clear Logs",
            command=self.clear_logs,
            bg='#ff9800',
            fg='white',
            width=12
        ).pack(side='left', padx=5)
    
    def setup_stats_tab(self, parent):
        """Setup the statistics tab"""
        tk.Label(
            parent,
            text="Server Statistics",
            font=('Arial', 12, 'bold')
        ).pack(anchor='w', padx=5, pady=5)
        
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill='both', padx=20, pady=10)
        
        # Statistics labels
        self.stats_labels = {}
        
        stats_items = [
            ("Total Rooms Created:", "total_rooms"),
            ("Active Rooms:", "active_rooms"),
            ("Total Players Connected:", "total_players"),
            ("Games in Progress:", "games_running"),
            ("Server Uptime:", "uptime")
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            label_frame = tk.Frame(stats_frame)
            label_frame.pack(fill='x', pady=5)
            
            tk.Label(
                label_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                width=25,
                anchor='w'
            ).pack(side='left')
            
            value_label = tk.Label(
                label_frame,
                text="0",
                font=('Arial', 10),
                anchor='w'
            )
            value_label.pack(side='left')
            
            self.stats_labels[key] = value_label
        
        self.server_start_time = None
    
    def get_server_info_text(self):
        """Get server connection info including local IP"""
        import socket
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return f"Connect: localhost:12345 (same PC) or {local_ip}:12345 (LAN)"
        except:
            return "Connect: localhost:12345 or <your-ip>:12345"
    
    def start_server(self):
        """Start the game server"""
        if not self.running:
            self.server = GameServer()
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            
            self.running = True
            self.server_start_time = datetime.now()
            self.server_thread.start()
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Server Status: Running", fg='green')
                # Update server info with actual IP
                self.info_label.config(text=self.get_server_info_text())
            
            self.log_message("Server started on localhost:12345")
    
    def stop_server(self):
        """Stop the game server"""
        if self.running:
            self.running = False
            if self.server:
                self.server.stop()
            
            self.status_label.config(text="Server Status: Stopped", fg='red')
            
            self.log_message("Server stopped")
    
    def _run_server(self):
        """Run the server in a separate thread"""
        try:
            self.server.start()
        except Exception as e:
            self.log_message(f"Server error: {e}")
    
    def refresh_rooms(self):
        """Refresh the rooms display"""
        # Clear current rooms display
        for widget in self.rooms_frame.winfo_children():
            widget.destroy()
        
        if not self.server or not self.running:
            no_server_label = tk.Label(
                self.rooms_frame,
                text="Server is not running",
                font=('Arial', 12),
                fg='gray',
                bg='white'
            )
            no_server_label.pack(pady=20)
            return
        
        rooms = self.server.rooms
        
        if not rooms:
            no_rooms_label = tk.Label(
                self.rooms_frame,
                text="No active rooms",
                font=('Arial', 12),
                fg='gray',
                bg='white'
            )
            no_rooms_label.pack(pady=20)
            return
        
        # Display each room
        for room_id, room in rooms.items():
            self.create_room_widget(room_id, room)
    
    def create_room_widget(self, room_id, room):
        """Create a widget to display room information"""
        room_frame = tk.Frame(
            self.rooms_frame,
            relief='raised',
            borderwidth=2,
            bg='#ffffff',
            padx=10,
            pady=10
        )
        room_frame.pack(fill='x', padx=5, pady=5)
        
        # Room header
        header_frame = tk.Frame(room_frame, bg='#ffffff')
        header_frame.pack(fill='x')
        
        # Room ID and status
        tk.Label(
            header_frame,
            text=f"Room ID: {room_id}",
            font=('Arial', 14, 'bold'),
            fg='#2196F3',
            bg='#ffffff'
        ).pack(side='left')
        
        # Game status
        status_color = '#4CAF50' if room.game_running else '#ff9800'
        status_text = 'Game Running' if room.game_running else 'Waiting for Players'
        
        tk.Label(
            header_frame,
            text=status_text,
            font=('Arial', 10, 'bold'),
            fg=status_color,
            bg='#ffffff'
        ).pack(side='right')
        
        # Player count
        tk.Label(
            room_frame,
            text=f"Players: {len(room.players)}/4",
            font=('Arial', 10),
            bg='#ffffff'
        ).pack(anchor='w', pady=(5,0))
        
        # Players list
        if room.players:
            players_frame = tk.Frame(room_frame, bg='#ffffff')
            players_frame.pack(fill='x', pady=(5,0))
            
            tk.Label(
                players_frame,
                text="Members:",
                font=('Arial', 10, 'bold'),
                bg='#ffffff'
            ).pack(anchor='w')
            
            for i, (socket, player_info) in enumerate(room.players.items()):
                player_name = player_info.get('name', f'Player {i+1}')
                player_id = player_info.get('id', i)
                
                tk.Label(
                    players_frame,
                    text=f"  • Player {player_id + 1}: {player_name}",
                    font=('Arial', 9),
                    fg='#666666',
                    bg='#ffffff'
                ).pack(anchor='w')
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Only log if the log_text widget exists
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Clear the log display"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
    
    def update_display(self):
        """Update the display periodically"""
        # Update statistics
        if self.server and self.running:
            self.update_statistics()
        
        # Auto-refresh rooms every 2 seconds
        if self.running:
            self.refresh_rooms()
        
        # Schedule next update
        self.root.after(2000, self.update_display)
    
    def update_statistics(self):
        """Update server statistics"""
        if not self.server:
            return
        
        # Calculate statistics
        active_rooms = len(self.server.rooms)
        games_running = sum(1 for room in self.server.rooms.values() if room.game_running)
        total_players = sum(len(room.players) for room in self.server.rooms.values())
        
        # Calculate uptime
        uptime = "Not running"
        if self.server_start_time:
            delta = datetime.now() - self.server_start_time
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Update labels
        self.stats_labels['active_rooms'].config(text=str(active_rooms))
        self.stats_labels['games_running'].config(text=str(games_running))
        self.stats_labels['total_players'].config(text=str(total_players))
        self.stats_labels['uptime'].config(text=uptime)
    
    def run(self):
        """Run the GUI"""
        try:
            self.root.mainloop()
        finally:
            if self.running:
                self.stop_server()

def main():
    """Main entry point for server GUI"""
    app = ServerGUI()
    app.run()

if __name__ == "__main__":
    main()