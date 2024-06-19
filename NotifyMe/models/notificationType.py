from django.db import models
from datetime import timedelta
from NotificationModule.constants import MAX_TITLE_LENGTH

class NotificationType(models.Model):
  notification_type = models.CharField(max_length=MAX_TITLE_LENGTH)
  
  class Meta:
    db_table='ms_notification_type'
  def __str__(self):
    return self.notification_type