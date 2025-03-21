import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Conexión establecida"}))

    async def disconnect(self, close_code):
        pass  # Puedes manejar la desconexión aquí

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"message": "Mensaje recibido"}))
