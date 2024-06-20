import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "Our_clients"

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name) 
        # self.channel_layer.group_add() takes self.group_name and self_channel_name as argument

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass
        

    # Receive message from room group
    async def send_notification(self, event):
        message = event["message"]
        notification_type = event['notification_type']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message':message}))
        
    async def subscription_plan_added(self, event):
        message = event["message"]
        await self.send(text_data = json.dumps({"message": message}))
        
        
    async def user_added(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message":message}))