from django.db import models
from datetime import timedelta
from django.utils import timezone

from .user import User
from .subscriptionPlan import SubscriptionPlan

class Subscription(models.Model):
  user_id = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
  
  subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
  
  start_date = models.DateTimeField(default=timezone.now)
  end_date = models.DateTimeField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)