from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.user import User
from .models.maintenanceModel import MaintenanceModel
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

    
@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
  if created:
    channel_layer = get_channel_layer()
    message = {
      "type":"user.added",
      "message":f"New User added: {instance.email_id}"
    }
    async_to_sync(channel_layer.group_send)("Our_clients", message)
    
    
@receiver(post_save, sender=MaintenanceModel)
def notify_new_maintenance_alert(sender, instance, created, **kwargs):
  if created:
    channel_layer = get_channel_layer()
    message = {
      "type":"send.maintenance.alert", # method in consumers...
      "message":f"Maintenance Alert: {instance.maintenance_message}"
    }
    
    async_to_sync(channel_layer.group_send)("Our_clients", message)
    
  