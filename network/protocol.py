"""
Network protocol definitions for Hit & Dodge game
"""
from enum import Enum
import json

class MessageType(Enum):
    # Client to Server
    JOIN_ROOM = "join_room"
    CREATE_ROOM = "create_room"
    LEAVE_ROOM = "leave_room"
    PLAYER_ACTION = "player_action"
    
    # Server to Client
    ROOM_JOINED = "room_joined"
    ROOM_CREATED = "room_created"
    ROOM_FULL = "room_full"
    ROOM_NOT_FOUND = "room_not_found"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    ROOM_UPDATE = "room_update"
    GAME_STATE = "game_state"
    GAME_START = "game_start"
    GAME_OVER = "game_over"
    ERROR = "error"

class ActionType(Enum):
    HIT = "hit"
    DODGE = "dodge"

class NetworkMessage:
    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data if data else {}
    
    def to_json(self):
        return json.dumps({
            'type': self.type.value if isinstance(self.type, MessageType) else self.type,
            'data': self.data
        })
    
    @classmethod
    def from_json(cls, json_str):
        try:
            data = json.loads(json_str)
            msg_type = MessageType(data['type'])
            return cls(msg_type, data.get('data', {}))
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

def create_join_room_message(room_id, player_name):
    return NetworkMessage(MessageType.JOIN_ROOM, {
        'room_id': room_id,
        'player_name': player_name
    })

def create_create_room_message(player_name):
    return NetworkMessage(MessageType.CREATE_ROOM, {
        'player_name': player_name
    })

def create_action_message(action_type):
    return NetworkMessage(MessageType.PLAYER_ACTION, {
        'action': action_type.value if isinstance(action_type, ActionType) else action_type
    })

def create_game_state_message(game_state):
    return NetworkMessage(MessageType.GAME_STATE, game_state)

def create_room_update_message(room_data):
    return NetworkMessage(MessageType.ROOM_UPDATE, room_data)