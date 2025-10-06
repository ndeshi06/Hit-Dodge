"""
Hit & Dodge Game - Main Entry Point
A 4-player online multiplayer game where players must hit or dodge a ball orbiting around a planet.

MVC Architecture:
- Models: Player, Ball, Game logic
- Views: GameRenderer, LobbyRenderer for all drawing operations  
- Controllers: OnlineGameController for input handling and network communication
- Network: Client-server architecture for multiplayer
"""

import sys
from controllers.online_controller import OnlineGameController

def main():
    """Main entry point of the online multiplayer game"""
    # Parse command line arguments
    create_room = False
    join_room_id = None
    player_name = "Player"
    host = "localhost"
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--create":
            create_room = True
        elif arg == "--join" and i + 1 < len(sys.argv):
            join_room_id = sys.argv[i + 1]
            i += 1  # Skip next argument as it's the room ID
        elif arg == "--name" and i + 1 < len(sys.argv):
            player_name = sys.argv[i + 1]
            i += 1  # Skip next argument as it's the player name
        elif arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
            i += 1  # Skip next argument as it's the host/IP
        i += 1
    
    controller = OnlineGameController(host=host)
    
    # Set player name if provided
    if player_name != "Player":
        controller.player_name = player_name
    
    # Handle auto-create or auto-join
    if create_room:
        controller.auto_create_room = True
    elif join_room_id:
        controller.auto_join_room = join_room_id
    
    controller.run()

if __name__ == "__main__":
    main()