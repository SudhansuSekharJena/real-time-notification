from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.user import User
from .models.subscriptionPlan import SubscriptionPlan
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=SubscriptionPlan)
def notify_new_subscriptionPlan(sender, instance, created, **kwargs):
  if created:
    channel_layer = get_channel_layer()
    message = {
      'type':'subscription.plan.added',
      'message': f"New plan added: {instance.subscription_plan}"
    }
    
    async_to_sync(channel_layer.group_send)('Our_clients', message)

    
@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
  if created:
    channel_layer = get_channel_layer()
    message = {
      "type":"user.added",
      "message":f"New User added: {instance.email_id}"
    }
    async_to_sync(channel_layer.group_send)("Our_clients", message)