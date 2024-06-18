from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.notification import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
  if created:
    channel_layer = get_channel_layer()
    notification_type = instance.notification_type.notification_type
    async_to_sync(channel_layer.group_send)(
      'notification_broadcast',
      {
        'type':'send_notification',
        'message': instance.message,
        'notification_type': notification_type,
      }
    )