
import logging
from datetime import timedelta
from NotifyMe.constants import *
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
            return start_date + timedelta(days=30)
        elif subscription_plan.subscription_plan == plans["REGULAR_PLAN"]:
            return start_date + timedelta(days=3 * 30)
        elif subscription_plan.subscription_plan == plans["STANDARD_PLAN"]:
            return start_date + timedelta(days=6 * 30)
        elif subscription_plan.subscription_plan == plans["PREMIUM_PLAN"]:
            return start_date + timedelta(days=365)
        else:
            return None
        
        

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
        
        