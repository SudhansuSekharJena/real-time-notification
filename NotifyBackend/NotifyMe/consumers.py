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
        pass
        

    # Receive message from room group
    async def send_notification(self, event):
        message = event["message"]
        notification_type = event['notification_type']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message':message}))
    
    async def send_announcement_notification(self, event):
        message = event['message']
        notification_type = event['notification_type']
        await self.send(text_data=json.dumps({"message": message}))
        
    async def send_maintenance_alert(self, event):
        message = event['message']
        notification_type = event['notification_type']
        await self.send(text_data=json.dumps({"message":message}))
        
    


    