from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationManager:
  
  def announcement_notification(self, group_name, message, notification_type):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
      group_name,
      {
        'type': 'send_announcement_notification', 
        'message': message,
        "notification_type":notification_type
      }
    )
    
  def maintenance_alert(self, group_name, message, notification_type):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
      group_name,
      {
        'type': 'send_maintenance_alert',
        'message': message,
        "notification_type":notification_type
      }
    )
  
  