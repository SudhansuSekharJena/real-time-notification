import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models.notification import Notification 
from .models.subscription import Subscription
from .models.subscriptionPlan import SubscriptionPlan
from .models.user import User
from django.utils import timezone
from datetime import timedelta
from .models.notificationType import NotificationType
from .constants import *
from NotifyMe.services.service import UserService

logger = logging.getLogger(__name__)

class UserSerializer(UserService, serializers.ModelSerializer):
    
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())
   



    class Meta:
        model = User
        fields = ('id', 'email_id', 'first_name', 'last_name', 'subscription_plan', 'created_at', 'updated_at')
        depth = 1
        
    # CREATE CLASS CALL...
    def create(self, validated_data):
        return self.create_user(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subscription_plan'] = instance.subscription_plan.subscription_plan
        return representation

class SubscriptionSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())

    class Meta:
        model = Subscription
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subscription_plan'] = instance.subscription_plan.subscription_plan
        return representation

class NotificationSerializer(serializers.ModelSerializer):
    notification_type = serializers.PrimaryKeyRelatedField(queryset=NotificationType.objects.all())

    class Meta:
        model = Notification
        fields = '__all__'
        

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
