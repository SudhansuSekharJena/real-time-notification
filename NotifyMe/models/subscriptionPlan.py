from django.db import models
from datetime import timedelta

class SubscriptionPlan(models.Model):
  subscription_plan = models.CharField(max_length=40, null=False)
  
  class Meta:
    db_table='ms_subscription_plan'
  def __str__(self):
    return self.subscription_plan
