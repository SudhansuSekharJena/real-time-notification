from django.db import models
from datetime import timedelta


class NotificationType(models.Model):
  notification_type = models.CharField(max_length = 60)
  
  class Meta:
    db_table='ms_notification_type'
  def __str__(self):
    return self.notification_type