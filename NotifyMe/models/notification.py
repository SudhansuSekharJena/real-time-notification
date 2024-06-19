from django.db import models
from django.utils import timezone
from datetime import timedelta
from .notificationType import NotificationType
from NotificationModule.constants import MAX_TITLE_LENGTH
from .baseModel import BaseModel

#-------NOTIFICATION MODEL---------
class Notification(BaseModel):
  title = models.CharField(max_length=MAX_TITLE_LENGTH)
  message = models.CharField(max_length=MAX_TITLE_LENGTH)
  recipient = models.EmailField(null=True)
  notification_type = models.ForeignKey(NotificationType, null=False,on_delete=models.CASCADE)
  def __str__(self):
     return self.message