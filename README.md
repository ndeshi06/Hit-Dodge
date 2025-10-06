# Hit & Dodge Game - Online Multiplayer

A 4-player online multiplayer game built with Pygame where players must hit or dodge a ball orbiting around a planet.

## Game Rules

- 4 players join a room using a 4-character room ID
- Game starts when room has exactly 4 players
- A ball spawns between random players and orbits around the planet
- Players can **Hit** to reverse the ball's direction and increase its speed
- Players can **Dodge** to hide underground for 1 second
- If the ball touches a player, they are eliminated and fly off screen
- Last player standing wins!

## Controls

- **Hit**: SPACE or UP Arrow
- **Dodge**: DOWN Arrow or ENTER

## How to Play Online

### Step 1: Start the Server (Host Only)

**IMPORTANT**: The host must start the server FIRST before anyone can join!

```bash
python server_gui.py
```

The Server GUI will:
- ✅ **Auto-start the server** when it opens
- 📡 Display your IP address for LAN connections (e.g., `192.168.1.100:12345`)
- 📊 Show active rooms, players, and statistics
- 🎮 Allow you to create/join rooms directly from the GUI

**For LAN Play**: Share the IP address shown in the server GUI with your friends.

### Step 2: Connect as Player

You have two options:

#### Option A: Use Server GUI (Easy)
1. On the server computer, go to the **"Room Management"** tab
2. Enter your player name
3. Click **"Create New Room"** to host or enter Room ID to **"Join Room"**
4. A game window will open automatically

#### Option B: Run Client Manually
```bash
python main.py
```

In the lobby:
1. Enter your player name
2. **If joining from another PC**: Enter the server's IP address (e.g., `192.168.1.100`)
3. Click **"Create New Room"** or **"Join Existing Room"**
4. If joining: Enter the 4-character Room ID

### Step 3: Wait for Players
- Game requires exactly **4 players** to start
- The waiting room shows all current members
- Once 4 players join, the game starts automatically!
- Share your room ID with friends to join

## Architecture (MVC + Network)

### Models (`/models/`)
- `player.py` - Player logic, state, and behavior
- `ball.py` - Ball physics and movement
- `game.py` - Game state management and collision detection
- `player_state.py` - Player state enumeration

### Views (`/views/`)
- `game_renderer.py` - Game rendering for both local and network data
- `lobby_renderer.py` - Lobby and waiting room UI

### Controllers (`/controllers/`)
- `online_controller.py` - Online multiplayer input handling and game flow
- `game_controller.py` - Local game controller (legacy)

### Network (`/network/`)
- `server.py` - Game server handling rooms and game logic
- `client.py` - Network client for connecting to server
- `protocol.py` - Network message protocol definitions

### Config (`/config/`)
- `constants.py` - Game constants and settings

## Features

- **Room-based Multiplayer**: Create or join rooms with 4-character IDs
- **Real-time Synchronization**: Game state synchronized across all clients
- **Hit Range Detection**: Players can only hit when ball is in range
- **Swing Animation**: Stick rotates towards ball direction when hitting
- **Hit Cooldown**: 0.5 second cooldown between hits to prevent spam
- **Flying Elimination**: Eliminated players fly off screen with physics
- **Ball Spawn System**: Ball spawns between random players with 3-second countdown
- **Speed Reset**: Ball speed resets when a player is eliminated
- **Connection Handling**: Graceful handling of player disconnections

## File Structure

```
HIT&DODGE/
├── launcher.py                # Game launcher (server or client)
├── main.py                    # Client entry point
├── server.py                  # Server entry point (console)
├── server_gui.py              # Server entry point (GUI)
├── config/
│   ├── __init__.py
│   └── constants.py           # Game constants
├── models/
│   ├── __init__.py
│   ├── player.py             # Player model
│   ├── ball.py               # Ball model
│   ├── game.py               # Game logic
│   └── player_state.py       # Player states
├── views/
│   ├── __init__.py
│   ├── game_renderer.py      # Game rendering
│   └── lobby_renderer.py     # Lobby/waiting room UI
├── controllers/
│   ├── __init__.py
│   ├── online_controller.py  # Online multiplayer controller
│   └── game_controller.py    # Local game controller (legacy)
├── network/
│   ├── __init__.py
│   ├── server.py             # Game server
│   ├── client.py             # Network client
│   └── protocol.py           # Network protocol
├── requirements.txt
└── README.md
```

## Network Protocol

The game uses a custom JSON-based protocol over TCP sockets:

- **Room Management**: Create/join rooms with unique IDs
- **Player Actions**: Hit and dodge actions sent to server
- **Game State**: Complete game state synchronized to all clients
- **Connection Events**: Handle player joins, leaves, and disconnections

## Requirements

```bash
pip install pygame
```

No additional network libraries required - uses Python's built-in socket module.