from django.db import models
from django.utils import timezone
from datetime import timedelta
from .notificationType import NotificationType
from NotificationModule.settings import MAX_TITLE_LENGTH
from .baseModel import BaseModel

#-------NOTIFICATION MODEL---------
class Notification(BaseModel):
  title = models.CharField(max_length=60)
  message = models.CharField(max_length=60)
  recipient = models.EmailField(null=True)
  notification_type = models.ForeignKey(NotificationType, null=False,on_delete=models.CASCADE)
  def __str__(self):
     return self.message