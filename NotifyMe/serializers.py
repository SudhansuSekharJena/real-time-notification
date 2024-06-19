# import serializers from rest_framework
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models.notification import Notification 
from .models.subscription import Subscription
from .models.subscriptionPlan import SubscriptionPlan
from .models.user import User
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from .models.notificationType import NotificationType
from .constants import *

class UserSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())

    class Meta:
        model = User
        fields = ('id', 'email_id', 'first_name', 'last_name', 'subscription_plan', 'created_at', 'updated_at')
        depth=1
        
    def get_endtime(self, validated_data, start_date):
      subscription_plan = validated_data.pop('subscription_plan')
      if subscription_plan.subscription_plan == plans["basic_plan"]:
          end_date = start_date + timedelta(days=30)
      elif subscription_plan.subscription_plan == plans["regular_plan"]:
          end_date = start_date + timedelta(days=3*30)
      elif subscription_plan.subscription_plan == plans["standard_plan"]:
          end_date = start_date + timedelta(days=6*30)
      elif subscription_plan.subscription_plan == plans["premium_plan"]:
          end_date = start_date + timedelta(days=365)
      else:
          end_date = None
      
      
      
    
    # THIS IS HELPING IN CREATING SUBSCRIPTION INSTANCE FROM THE INSIDE OF USER... 
    def create(self, validated_data):
      try:
          subscription_plan = validated_data.pop('subscription_plan')
          
          user = User.objects.create(subscription_plan=subscription_plan, **validated_data)
          
          # Create a new Subscription
          Subscription.objects.create(
              user_id=user,
              subscription_plan=subscription_plan,
              start_date=timezone.now(),
              end_date = self.get_endtime(validated_data, start_date=timezone.now())     
          )
          
          return user
      except IntegrityError as e:
        error_message = str(e)
        raise ValidationError(f"IntegrityError: {error_message}")
      except Exception as e:
        error_message = str(e)
        raise ValidationError(f"An error occured: {error_message}")
    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subscription_plan'] = instance.subscription_plan.subscription_plan
        return representation
        
        
    
class SubscriptionSerializer(serializers.ModelSerializer):
  user_id = serializers.PrimaryKeyRelatedField(queryset = User.objects.all()) 
  
  subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())
  
  class Meta:
    model = Subscription
    fields = '__all__'
  
  # this code is responsible for showing Subscription_plan insted of id.
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subscription_plan'] = instance.subscription_plan.subscription_plan
        return representation
    

class NotificationSerializer(serializers.ModelSerializer):
  notification_type = serializers.PrimaryKeyRelatedField(queryset=NotificationType.objects.all())
  
  class Meta:
    model = Notification
    fields = '__all__'
    
    
