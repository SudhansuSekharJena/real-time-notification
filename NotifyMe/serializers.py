import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from rest_framework import serializers
from .models.notification import Notification 
from .models.subscription import Subscription
from .models.subscriptionPlan import SubscriptionPlan
from .models.user import User
from .models.notificationType import NotificationType
from .constants import *
from NotifyMe.services.service import UserService
from NotifyMe.constants import NotificationTypeId 

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())

    class Meta:
        model = User
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        user_service = UserService()
        try:
            return user_service.create_user(validated_data)
        except IntegrityError as e:
            error_message = str(e)
            raise ValidationError(f"IntegrityError: {error_message}")
        except ObjectDoesNotExist as e:
            error_message = str(e)
            raise ValidationError(f"Object does not exist: {error_message}")
        except DatabaseError as e:
            error_message = str(e)
            raise ValidationError(f"Database error: {error_message}")
        except MultipleObjectsReturned as e:
            error_message = str(e)
            raise ValidationError(f"Multiple objects returned: {error_message}")
        except Exception as e:
            error_message = str(e)
            raise ValidationError(f"An unexpected error occurred: {error_message}")

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



 