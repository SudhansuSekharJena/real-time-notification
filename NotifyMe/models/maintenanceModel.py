from django.db import models
from NotificationModule.constants import length

class MaintenanceModel(models.Model):
    maintenance_message = models.CharField(max_length=length['MESSAGE_MAX_LENGTH'])

    def __str__(self):
        return self.maintenance_message