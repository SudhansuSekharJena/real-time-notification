from django.db import models
from datetime import timedelta
from NotificationModule.constants import MAX_TITLE_LENGTH

class SubscriptionPlan(models.Model):
  subscription_plan = models.CharField(max_length=MAX_TITLE_LENGTH, null=False)
  
  class Meta:
    db_table='ms_subscription_plan'
  def __str__(self):
    return self.subscription_plan
