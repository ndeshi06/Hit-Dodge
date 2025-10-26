# Hit & Dodge Game

A 4-player multiplayer game built with Pygame where players must hit or dodge a ball orbiting around a planet.

## Game Rules

- 4 players compete in an arena
- A ball spawns between random players and orbits around the planet
- Players can **Hit** to reverse the ball's direction and increase its speed
- Players can **Dodge** to hide underground for 1 second
- If the ball touches a player, they are eliminated and fly off screen
- Last player standing wins!

## How to Play

### 🎮 Local Multiplayer (4 người trên 1 máy)

```bash
python local_multiplayer.py
```

**Controls:**
- **Player 1 (Red)**: Q = Hit, A = Dodge
- **Player 2 (Green)**: W = Hit, S = Dodge
- **Player 3 (Blue)**: O = Hit, L = Dodge
- **Player 4 (Yellow)**: P = Hit, ; = Dodge

### 🌐 P2P Multiplayer (4 máy qua mạng LAN)

```bash
python p2p_multiplayer.py
```

#### Host (Người tạo phòng):
1. Nhập tên của bạn
2. Click **"TẠO PHÒNG (HOST)"**
3. Chia sẻ **IP Address** và **Mã phòng 4 ký tự** cho bạn bè

#### Client (Người tham gia):
1. Nhập tên của bạn
2. Nhập **IP của host** và **mã phòng**
3. Click **"THAM GIA"**

**Controls:**
- **Hit**: SPACE or UP Arrow
- **Dodge**: DOWN Arrow or ENTER

#### Troubleshooting

Nếu không kết nối được:
```bash
python network_test.py
```

Checklist:
- ✅ Cùng mạng WiFi/LAN
- ✅ Firewall tắt hoặc cho phép port 12345
- ✅ Host đã tạo phòng trước
- ✅ IP và mã phòng chính xác

Xem hướng dẫn chi tiết: [HUONG_DAN.md](HUONG_DAN.md)

## Requirements

```bash
pip install -r requirements.txt
```

or simply:

```bash
pip install pygame
```

## Features

- **Local Multiplayer**: 4 players on one computer with split keyboard
- **P2P Network**: Direct peer-to-peer connection, no server needed
- **Room Codes**: Easy 4-character room codes to share
- **Hit Range Detection**: Players can only hit when ball is in range
- **Swing Animation**: Stick rotates towards ball direction when hitting
- **Hit Cooldown**: 0.5 second cooldown between hits to prevent spam
- **Flying Elimination**: Eliminated players fly off screen with physics
- **Ball Spawn System**: Ball spawns between random players with 3-second countdown
- **Speed Reset**: Ball speed resets when a player is eliminated

## File Structure

```
Hit-Dodge/
├── local_multiplayer.py      # Local 4-player mode
├── p2p_multiplayer.py         # P2P online mode
├── network_test.py            # Network diagnostic tool
├── config/
│   └── constants.py           # Game constants
├── models/
│   ├── player.py             # Player model
│   ├── ball.py               # Ball model
│   ├── game.py               # Game logic
│   └── player_state.py       # Player states
├── views/
│   ├── game_renderer.py      # Game rendering
│   └── lobby_renderer.py     # Lobby UI
├── network/
│   ├── server.py             # Game server (legacy)
│   ├── client.py             # Network client (legacy)
│   └── protocol.py           # Network protocol (legacy)
├── controllers/
│   ├── online_controller.py  # Online controller (legacy)
│   └── game_controller.py    # Game controller (legacy)
├── requirements.txt
├── README.md
└── HUONG_DAN.md              # Vietnamese guide
```

## Tips

### Playing over Internet (not on same LAN):
You need **Port Forwarding** on the router:
1. Access router settings (usually `192.168.1.1`)
2. Find **Port Forwarding** or **Virtual Server**
3. Forward port `12345` to host machine's IP
4. Use your **Public IP** (search "what is my ip" on Google)
5. Clients enter this public IP

### Network optimization:
- Use wired LAN instead of WiFi for better stability
- Ensure sufficient bandwidth (at least 1 Mbps)
- Close other network-intensive apps

## License

This project is open source and available for educational purposes.