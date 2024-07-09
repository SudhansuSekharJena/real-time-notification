from django.db import models
from NotificationModule.constants import Length

class NotificationType(models.Model):
  notification_type = models.CharField(max_length=Length.MAX_TITLE_LENGTH.value)
  
  class Meta:
    db_table='ms_notification_type'
  def __str__(self):
    return self.notification_type