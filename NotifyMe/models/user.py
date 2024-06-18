from django.db import models
from datetime import timedelta 
from django.utils import timezone
from NotificationModule.settings import MAX_TITLE_LENGTH
from .subscriptionPlan import SubscriptionPlan
from .baseModel import BaseModel

class User(BaseModel):
  email_id = models.EmailField(unique=True)
  first_name = models.CharField(max_length=60)
  last_name = models.CharField(max_length=60)
  subscription_plan = models.ForeignKey(SubscriptionPlan, null=False, on_delete=models.CASCADE)