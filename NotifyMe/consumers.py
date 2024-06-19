import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "Our_clients"

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        notification_type = text_data_json['notification_type']

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name, {
                "type": "send_notification",
                "message": message,
                "notification_type": notification_type
                }
        )
        
        self.send(text_data=json.dumps({
            'message': text_data_json['message'],
            'status': 'Received'
        }))

    # Receive message from room group
    async def send_notification(self, event):
        message = event["message"]
        notification_type = event['notification_type']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message':message}))