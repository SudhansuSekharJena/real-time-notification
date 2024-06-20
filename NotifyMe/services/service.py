
import logging
from django.utils import timezone
from datetime import timedelta

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from NotifyMe.constants import plans, plans_duration
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from NotifyMe.models.notification import Notification
from NotifyMe.models.notificationType import NotificationType
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User
from django.db import DatabaseError

logger = logging.getLogger(__name__)

class UserService:
    def get_user_data(self, request):
        try:
            users = User.objects.all()
            return users
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            return None
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"General error: {e}")
            return None
        
        
    def get_userId_data(self, data):
        user = User.objects.get(id=data.get('id'))
        return user
    
    
    def get_userDatabase(self):
        return User
    
    def get_subscriptionPlanDatabase(self):
        return SubscriptionPlan
    
    def get_endtime(self, subscription_plan, start_date):
        if subscription_plan.subscription_plan == plans["BASIC_PLAN"]:
            return start_date + timedelta(days=plans_duration["BASIC"])
        elif subscription_plan.subscription_plan == plans["REGULAR_PLAN"]:
            return start_date + timedelta(days=plans_duration["REGULAR"])
        elif subscription_plan.subscription_plan == plans["STANDARD_PLAN"]:
            return start_date + timedelta(days=plans_duration["STANDARD"])
        elif subscription_plan.subscription_plan == plans["PREMIUM_PLAN"]:
            return start_date + timedelta(days=plans_duration["PREMIUM"])
        else:
            return None
       
        
    def create_user(self, validated_data):
        try:
            
            subscription_plan = validated_data.pop('subscription_plan')

            if subscription_plan is None:
                raise ValidationError("The 'subscription_plan' field is required.") # User: User object (31)

            user = User.objects.create(subscription_plan=subscription_plan, **validated_data)
            

            # Create a new Subscription
            start_date = timezone.now()
            end_date = self.get_endtime(subscription_plan
                                        , start_date)
            if end_date is None:
                raise ValidationError("Invalid subscription plan")

            Subscription.objects.create(
                user_id=user,
                subscription_plan=subscription_plan,
                start_date=start_date,
                end_date=end_date    
            )

            logger.info(f"User created successfully with ID: {user.id}")

            return user
        except IntegrityError as e:
            error_message = str(e)
            logger.error(f"IntegrityError: {error_message}")
            raise ValidationError(f"IntegrityError: {error_message}")
        except Exception as e:
            error_message = str(e)
            logger.error(f"Unexpected error: {error_message}")
            raise ValidationError(f"An error occurred: {error_message}")
        
        

class SubscriptionService:
    def get_subscription_data(self, request):
        try:
            subscriptions = Subscription.objects.all()
            return subscriptions
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            return None
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"General error: {e}")
            return None
        
    def get_subscriptionId_data(self, data):
        subscription = Subscription.objects.get(id=data.get('id'))
        return subscription
    
    
    def get_subscriptionDatabase(self): # returns dataabse to check is the database exists
        return Subscription
    
    
    

class NotificationService:
    def get_notification_data(self, request):
        try:
            notifications = Notification.objects.all()
            return notifications
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            return None
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"General error: {e}")
            return None

    def get_notification_type_data(self, request):
        try:
            notification_types = NotificationType.objects.all()
            return notification_types
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            return None
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"General error: {e}")
            return None
        
    def get_notificationId_data(self, data):
        notification = Notification.objects.get(id=data.get('id')) 
        return notification
    
    def get_notificationDatabase(self):
        return Notification
    
    
    


class SubscriptionPlanService:
    def get_subscriptionPlan_data(self, request):
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            return subscription_plans
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            return None
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"General error: {e}")
            return None
        
        
    def get_subscriptionPlan_id(self, data):
        subscriptionPlan = SubscriptionPlan.objects.all(id=data.get('id'))
        return subscriptionPlan
    
    def get_subscriptionPlanDatabase(self):
        return SubscriptionPlan
        
        