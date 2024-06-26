from django.db import models
from NotificationModule.constants import Length
from .subscriptionPlan import SubscriptionPlan
from .baseModel import BaseModel

class User(BaseModel):
  email_id = models.EmailField(unique=True)
  first_name = models.CharField(max_length=Length['MAX_TITLE_LENGTH'])
  last_name = models.CharField(max_length=Length['MAX_TITLE_LENGTH'])
  subscription_plan = models.ForeignKey(SubscriptionPlan, null=False, on_delete=models.CASCADE)