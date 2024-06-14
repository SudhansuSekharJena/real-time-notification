from django.db import models
from datetime import timedelta 
from django.utils import timezone

from .subscriptionPlan import SubscriptionPlan

class User(models.Model):
  email_id = models.EmailField(unique=True)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=40)
  subscription_plan = models.ForeignKey(SubscriptionPlan, null=False, on_delete=models.CASCADE)
  created_at = models.DateTimeField(default=timezone.now)
  updated_at = models.DateTimeField(auto_now=True)
  

  # auto_now: this option is used to set the value of the field to the current date and time everytime the model instance is saved, regardless being created or updated
  
  # auto_now_add: thgis option is used to set the value of the field to the current date and timme only when the model instance is created.