from django.db import models
from django.utils import timezone
from datetime import timedelta
from .notificationType import NotificationType

#-------NOTIFICATION MODEL---------
class Notification(models.Model):
  title = models.CharField(max_length=40)
  message = models.CharField(max_length=100)
  recipient = models.EmailField(null=True) # EmailField shouldnot have any attribute.
  created_at = models.DateTimeField(default=timezone.now)
  # auto_now_Add = True -> The argument means that the field will automatically be set to the current date and time when the notification is created.
  notification_type = models.ForeignKey(NotificationType, null=False,on_delete=models.CASCADE)
  def __str__(self):
     return self.message