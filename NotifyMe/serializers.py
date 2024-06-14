# import serializers from rest_framework

from rest_framework import serializers
from .models.notification import Notification 
from .models.subscription import Subscription
from .models.subscriptionPlan import SubscriptionPlan
from .models.user import User
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from .models.notificationType import NotificationType

class UserSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())

    class Meta:
        model = User
        fields = ('id', 'email_id', 'first_name', 'last_name', 'subscription_plan', 'created_at', 'updated_at')
        depth=1
    
    # THIS IS HELPING IN CREATING SUBSCRIPTION INSTANCE FROM THE INSIDE OF USER... 
    def create(self, validated_data):
        subscription_plan = validated_data.pop('subscription_plan')
        user = User.objects.create(subscription_plan=subscription_plan, **validated_data)
        
        start_date = timezone.now()
        
        if subscription_plan.subscription_plan == "Basic": # start_Date+30days
          end_date = start_date + timedelta(days=30)
        elif subscription_plan.subscription_plan == "Regular": # start_Date + 3*30days
          end_date = start_date + timedelta(days=3*30)
        elif subscription_plan.subscription_plan == "Standard": # start_date + 6*30days
          end_date = start_date + timedelta(days=6*30)
        elif subscription_plan.subscription_plan == "Premium": # start_date + 365 days
          end_date = start_date + timedelta(days=365)
        else:
          end_date = None
          
        
        
        # Create a new Subscription
        Subscription.objects.create(
            user_id=user,
            subscription_plan=subscription_plan,
            start_date=timezone.now(),
            # calculate the end date
            end_date = end_date
              
            
            
        )
        
        return user
    
    
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
    
    
