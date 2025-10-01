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

### Option 1: Use the Launcher (Recommended)
```bash
python launcher.py
```
Choose "Run Server" to host a game or "Join Game" to connect to someone's server.

### Option 2: Manual Setup

#### Start the Server with GUI
```bash
python server_gui.py
```
- The server GUI shows active rooms, player lists, and server statistics
- Click "Start Server" to begin accepting connections
- Share your IP address with friends for them to connect

#### Start the Game Client
```bash
python main.py
```

### 3. Create or Join a Room
- **Create Room**: Leave Room ID empty and press ENTER (generates random 4-char ID)
- **Join Room**: Enter a 4-character room ID and press ENTER
- Use TAB to switch between Player Name and Room ID inputs

### 4. Wait for Players
- Game requires exactly 4 players to start
- The waiting room shows all current members
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