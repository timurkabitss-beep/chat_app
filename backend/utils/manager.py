from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message_data: dict, user_id: int):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message_data)

    async def broadcast_to_group(self, message_data: dict, participant_ids: list[int]):
        for uid in participant_ids:
            await self.send_personal_message(message_data, user_id=uid)

    def is_connected(self, user_id: int) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()
