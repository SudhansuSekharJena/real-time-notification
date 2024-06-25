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
        
        
    async def user_added(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message":message}))
        
        
    async def send_maintenance_alert(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({"message":message}))
        
    
        
        
class AssessmentConsumer(AsyncWebsocketConsumer):
    # connect, disconnect, recieve, end
    # connect -> give group_name, channel_layer.group_add then accept
    
    async def connect(self):
        self.group_name = "Assessment_clients"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.connect()
        
        
    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    
    async def recieve(self, text_data):
        pass
    
    
class SubscriptionNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # i want a group name like user_1, user_2
        self.user_id = self.scope['user'].id
        self.group_name = f"user_{self.user_id}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.accept()
        
        
    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        
    async def recieve(self, text_data):
        pass
    
    
    async def send_expiry_notification(self, event):
        message = event['message']
        
        await self.send(text_data = json.dumps({"message":message}))
        
    
    