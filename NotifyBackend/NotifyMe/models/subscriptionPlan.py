from django.db import models
from NotificationModule.constants import Length

class SubscriptionPlan(models.Model):
  subscription_plan = models.CharField(max_length=Length.MAX_TITLE_LENGTH.value, null=False)
  
  class Meta:
    db_table='ms_subscription_plan'
  def __str__(self):
    return self.subscription_plan
