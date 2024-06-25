import logging
from django.utils import timezone
from datetime import timedelta
from django.http import Http404
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from NotifyMe.constants import plans, plans_duration, plans_id, notification_type_id
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import status 
from rest_framework.response import Response
from NotifyMe.models.notification import Notification 
from NotifyMe.models.maintenanceModel import MaintenanceModel
from NotifyMe.models.notificationType import NotificationType
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User
from django.db import DatabaseError
from NotifyMe.constants import plans_id
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class UserService:
    def get_user_data(self):
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
        try:
            user_id = data.get('id')
            if user_id is None:
                raise ValueError("User ID is missing from the data")
            
            user = User.objects.get(id=user_id)
            return user
        except ObjectDoesNotExist:
            raise Http404(f"User with id {user_id} does not exist")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            # Log the error here if you have a logging system set up
            raise Exception(f"An error occurred while fetching user data: {str(e)}")


    
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
            print(f"Subscription:{subscriptions}")
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
        try:
            subscription_id = data.get('id')
            if subscription_id is None:
                logger.error("No ID provided in the data.")
                return None
            
            subscription = Subscription.objects.get(id=subscription_id)
            return subscription
        except ObjectDoesNotExist:
            logger.error("Subscription with the given ID does not exist.")
            return None
        except MultipleObjectsReturned:
            logger.error("Multiple subscriptions found with the same ID.")
            return None
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None
    
    

    
    
        
        
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
        try:
            plan_id = data.get('id')
            if plan_id is None:
                raise ValueError("Subscription Plan ID is missing from the data")
            
            # Note: Use .get() instead of .all() to retrieve a single object
            subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
            return subscription_plan
        except ObjectDoesNotExist:
            raise Http404(f"SubscriptionPlan with id {plan_id} does not exist")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            # Log the error here if you have a logging system set up
            raise Exception(f"An error occurred while fetching subscription plan data: {str(e)}")


class SubscriptionNotificationService:
    
    def get_expiring_subscriptions(self, expiration_threshold):
        try:
            expired_subscriptions = Subscription.objects.filter(end_date__lte=expiration_threshold, end_date__gt=timezone.now())
            return expired_subscriptions
        except Exception as e:
            logger.error(f"Error fetching expiring subscriptions: {e}", exc_info=True)
            return []

    def get_recommended_plans(self, subscription_plan_id):
        try:
            if subscription_plan_id == 1:
                return [plans_id.get(1), plans_id.get(2), plans_id.get(3), plans_id.get(4)]
            elif subscription_plan_id == 2:
                return [plans_id.get(2), plans_id.get(3), plans_id.get(4)]
            elif subscription_plan_id == 3:
                return [plans_id.get(3), plans_id.get(4)]
            elif subscription_plan_id == 4:
                return [plans_id.get(4)]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting recommended plans for subscription plan id {subscription_plan_id}: {e}", exc_info=True)
            return None

    def send_expiration_notification(self, subscription):
        try:
            subscription_plan_id = subscription.subscription_plan_id
            days_left = (subscription.end_date - timezone.now()).days
            recommended_plans = self.get_recommended_plans(subscription_plan_id)
            
            if recommended_plans:
                message = f"Your plan: {plans_id.get(subscription_plan_id)} is going to expire in {days_left} days. We recommend you to upgrade your plan. Plans: {', '.join(recommended_plans)}"
                
                try:
                    notification = Notification(
                        title="Subscription Upgrade Recommendations",
                        message=message,
                        recipient=subscription.user_id.email_id,
                        notification_type=notification_type_id.get(6)
                    )
                    notification.save()
                    logger.info(f"Upgrade subscription notification sent to {subscription.user_id.email_id}")
                    
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{subscription.user_id.id}",
                        {
                            "type": "send_expiry_notification",
                            "message": message,
                            "notification_type": "SUBSCRIPTION PLAN UPDATE"
                        }
                    )
                    return "Notifications sent successfully"
                
                except Exception as e:
                    logger.error(f"Unexpected error occurred while sending subscription end notifications: {e}", exc_info=True)
                    return "An unexpected error occurred"
        
        except Exception as e:
            logger.error(f"Error in send_expiration_notification method: {e}", exc_info=True)
            return "An error occurred while processing the notification"

        
        
class MaintenanceNotificationService:
    
    def get_maintenance_data(self):
        try:
            maintenance = MaintenanceModel.objects.all()
            return maintenance
        except Exception as e:
            logger.error(f"Error fetching maintenance data: {e}", exc_info=True)
            return None
    

        
        
        