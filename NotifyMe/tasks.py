# tasks.py in NotifyMe

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from NotifyMe.models.subscription import Subscription
from NotifyMe.services.service import SubscriptionNotificationService
import logging

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def check_expiring_subscriptions():
    try:
        service = SubscriptionNotificationService()
        expiration_threshold = timezone.now() + timedelta(days=7)
        expiring_subscriptions = Subscription.objects.filter(end_date__lte=expiration_threshold, end_date__gt=timezone.now())

        for subscription in expiring_subscriptions:
            try:
                service.send_expiration_notification(subscription)
            except Exception as e:
                logger.error(f"Failed to send notification for subscription {subscription.id}: {e}")
                continue
        
        logger.info("Expiring subscription notifications sent successfully")
    except Exception as e:
        logger.error(f"Failed to check expiring subscriptions: {e}")
