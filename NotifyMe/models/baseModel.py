from django.db import models
from django.utils import timezone
from safedelete.models import SafeDeleteModel
from safedelete.config import SOFT_DELETE_CASCADE

class  BaseModel(SafeDeleteModel):
  _safedelete_policy = SOFT_DELETE_CASCADE
  
  created_at = models.DateTimeField(default=timezone.now)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    abstract = True