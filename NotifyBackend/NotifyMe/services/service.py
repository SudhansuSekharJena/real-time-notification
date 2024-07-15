import logging
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from NotifyMe.constants import Plans, PlansDuration
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User
from NotifyMe.models.notification import Notification
from NotifyMe.utils.exceptionManager import NotifyMeException, NotifyMeException
from django.core.exceptions import PermissionDenied
from NotifyMe.utils.error_codes import ErrorCodeMessages, ErrorCodes
from NotifyMe.constants import NotificationTypeId


logger = logging.getLogger(__name__)

class UserService:
    def get_all_users(self):
        """
        Get all Users.
        
        Returns:
           QuerySet of all User objects.
           
        Raises:
           ValidationError: If there is an error retrieving the users.
        
        """
        try:
            users = User.objects.all()
            return users
        except User.DoesNotExist as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_153_DATABASE_ERROR_WHILE_FETCHING_USERS.value,
                status_code=ErrorCodes.HTTP_153_DATABASE_ERROR.value,
                e=e
                )
        except Exception as e:
            logger.error(f"An Unexpected error occured while fetching User from Database. ERROR: {e}")
            raise e
            
    def get_user_by_id(self, data):
        
        """
        Retrieve a user by their ID.
        
        Args:
           data(dict): A dictionary containing the user ID
           
        Returns:
            User: The User object with the given ID.
            
        Raise:
            ValidationError: If the user ID is missing or if there is an error retrieving th user.
        
        """
        user_id = data.get('id')
        if user_id is None:
            raise ValueError
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_101_USER_NOT_FOUND.value,
                                    status_code=ErrorCodes.HTTP_101_USER_NOT_FOUND.value,
                                    e=e)
        except KeyError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value,
                                    status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value,
                                    e=e)
        except ValueError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_157_USER_ID_MISSING.value,
                                    status_code=ErrorCodes.HTTP_157_USER_ID_MISSING.value,
                                    e=e)
        except PermissionDenied as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_112_PERMISSION_DENIED_WHILE_DELETING_USER_DATA.value,
                status_code=ErrorCodes.HTTP_112_PERMISSION_DENIED_WHILE_DELETING_USER_DATA.value,
                e=e
                )
        except Exception as e:
            logger.error(f"An Unexpected error occurred while fetching user data. ERROR: {e}")
            raise e

    def get_end_time(self, subscription_plan, start_date):
        """
        Calculate the end-date of subscription based on its plan.
        
        Args:
          subscription_plan (SubscriptionPlan): The subscription plan.
          start_date (datetime): The start date of the subscription.
          
        Returns:
            datetime: The calculated end date of the subscription according to PlanType.
            
        Raises:
            ValueError: If the subscription plan is invalid.
            KeyError: If the plan or duration is not found in the dictionaries.
        """
        try:
            plan_type = subscription_plan.subscription_plan

            if plan_type == Plans.BASIC_PLAN.value:
                return start_date + timedelta(days=PlansDuration.BASIC.value)
            elif plan_type == Plans.REGULAR_PLAN.value:
                return start_date + timedelta(days=PlansDuration.REGULAR.value)
            elif plan_type == Plans.STANDARD_PLAN.value:
                return start_date + timedelta(days=PlansDuration.STANDARD.value)
            elif plan_type == Plans.PREMIUM_PLAN.value:
                return start_date + timedelta(days=PlansDuration.PREMIUM.value)
            else:
                raise ValidationError
        except KeyError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_154_DURATION_NOT_FOUND_ERROR_FOR_SUBSCRIPTION_PLAN_TYPE.value, status_code=ErrorCodes.HTTP_154_DURATION_NOT_FOUND_ERROR_FOR_SUBSCRIPTION_PLAN_TYPE.value,
                                    e=e)
        except ValidationError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_158_INVALID_SUBSCRIPTION_PLAN_PROVIDED.value,
                                    status_code=ErrorCodes.HTTP_158_INVALID_SUBSCRIPTION_PLAN_PROVIDED.value,
                                    e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while calculating end date. ERROR: {e}")
            raise e
        
    def create_user(self, validated_data):
        """
        Create a new user and their subscription.
        
        Args: 
            validated_data (dict): A dictionary containing the validated user data.
            
        Returns:
             User: A new created User object.
             
        Raises:
             ValueError: If the subscription_plan is missing.
             IntegrityError: If there's a database integrity error.
        """
        subscription_plan = validated_data.pop('subscription_plan')

        if subscription_plan is None:
            raise ValidationError
        try:
            user = User.objects.create(subscription_plan=subscription_plan, **validated_data)

            start_date = timezone.now()
            end_date = self.get_end_time(subscription_plan, start_date)

            Subscription.objects.create(
                user_id=user,
                subscription_plan=subscription_plan,
                start_date=start_date,
                end_date=end_date    
            )

            logger.info(f"User created successfully with ID: {user.id}")
            return user
        except User.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_102_UNEXPECTED_ERROR_WHILE_FETCHING_USER.value,
                                    status_code=ErrorCodes.HTTP_102_UNEXPECTED_ERROR_WHILE_FETCHING_USER.value,
                                    e=e)
        except SubscriptionPlan.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_105_INVALID_SUBSCRIPTION_ID_PROVIDED.value,
                                    status_code=ErrorCodes.HTTP_105_INVALID_SUBSCRIPTION_ID_PROVIDED.value,
                                    e=e)
        except ValidationError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_160_SUBSCRIPTION_PLAN_FIELD_IS_MISSING.value,
                                    status_code=ErrorCodes.HTTP_160_SUBSCRIPTION_PLAN_FIELD_IS_MISSING.value,
                                    e=e)
        except IntegrityError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_108_INVALID_USER_ID_PROVIDED.value,
                                    status_code=ErrorCodes.HTTP_108_INVALID_USER_ID_PROVIDED.value,
                                    e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while creating user. ERROR: {e}")
            raise e
        

class SubscriptionService: 
    def get_all_subscriptions(self):
        
        """
        Retrieve all subscriptions from the database.
        
        Args: 
           request(HttpRequest): The request object.
           
        Returns:
            QuerySet: A QuerySet of all Subscription objects.
            
        Raises:
            DatabaseError: If there is a database-related error retrieving the subscriptions.
        """
        try:
            subscriptions = Subscription.objects.all()
            logger.info(f"Retrieved {subscriptions.count()} subscriptions")
            return subscriptions
        except Subscription.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_144_DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS.value,       status_code=ErrorCodes.HTTP_144_DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS.value,
                                    e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscriptions: ERROR: {e}")
            raise e
        
    def get_subscription_by_id(self, data):
        """
        Retrieve Subscription by ID
        
        Args:
           data(dict): A dictionary containing Subscription ID.
           
        Returns:
            Subscription: The Subscription object with the given ID.
            
        Raises:
            ValueError: If Subscription ID is missing.
            ObjectDoesNotExist: If no subscription with the given ID exists.
        """
        subscription_id = data.get('id')
        if subscription_id is None:
            raise ValueError
        
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            logger.info(f"Retrieved subscription with ID {subscription_id}")
            return subscription
        except KeyError as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value, 
                status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value,
                e=e
            )
        except ValueError as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_159_SUBSCRIPTION_ID_IS_MISSING.value,
                status_code=ErrorCodes.HTTP_159_SUBSCRIPTION_ID_IS_MISSING.value,
                e=e
            )
        except Subscription.DoesNotExist as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_131_SUBSCRIPTION_PLANS_NOT_FOUND.value,
                status_code=ErrorCodes.HTTP_131_SUBSCRIPTION_PLANS_NOT_FOUND.value,
                e=e
                ) 
        except PermissionDenied as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_156_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_DATA.value,
                status_code=ErrorCodes.HTTP_156_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_DATA.value,
                e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving subscription with ID {subscription_id}. ERROR: {e}")
            raise e
        
class SubscriptionPlanService:
    def get_all_subscription_plans(self, request):
        """
        Retrieves all Subscription plans from the database.
        
        Args:
           request(HttpRequest): The request object.
           
        Returns:
           QuerySet: A QuerySet of all SubscriptionPlan objects.
           
        Raises: 
            DatabaseError: If there is a database-related error retrieving the subscription plans.
        """
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            logger.info(f"Retrieved {subscription_plans.count()} subscription plans")
            return subscription_plans
        except SubscriptionPlan.DoesNotExist as e:
            raise NotifyMeException(
                    message=ErrorCodeMessages.HTTP_145_DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS_PLANS.value,
                    status_code=ErrorCodes.HTTP_145_DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS_PLANS.value,
                    e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscription plans. ERROR: {e}")
            raise e
        
        
    def get_subscription_plan_by_id(self, data):
        """
        Retrieve a subscription plan by its ID.
        
        Args: 
          data(dict): A dictionary containing the subscription plan ID.
          
        Returns:
           SubscriptionPlan: A SubscriptionPlan object with the given ID.
           
        Raises:
            ValueError: If the subscription plan ID is missing.
            ObjectDoesNotExist: If no subscription plan with the given ID exists.
        """
        plan_id = data.get('id')
        if plan_id is None:
            raise ValueError
        
        try:
            subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
            logger.info(f"Retrieved subscription plan with ID {plan_id}")
            return subscription_plan
        except KeyError as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value,
                status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE.value,
                e=e)
        except ValueError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_161_SUBSCRIPTION_PLAN_ID_MISSING.value,
                                    status_code=ErrorCodes.HTTP_161_SUBSCRIPTION_PLAN_ID_MISSING.value,
                                    e=e)
        except SubscriptionPlan.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_131_SUBSCRIPTION_PLANS_NOT_FOUND.value,
                                    status_code=ErrorCodes.HTTP_131_SUBSCRIPTION_PLANS_NOT_FOUND.value,
                                    e=e)
        except PermissionDenied as e:
            raise NotifyMeException(
                message=ErrorCodeMessages.HTTP_139_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_PLAN_DATA.value,
                status_code=ErrorCodes.HTTP_139_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_PLAN_DATA.value,
                e=e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving subscription plan with ID {plan_id}: {e}")
            raise e
        

class AnnouncementsService:
    
    def get_all_announcements(self):
        try:
            announcements = Notification.objects.filter(notification_type_id=2) # return query set of Notification instances
            logger.info(f"Retrieved {announcements.count()} announcement notifications")
            return announcements
        except Notification.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_169_DATABASE_ERROR_WHILE_RETRIEVING_ANNOUNCEMENTS.value, status_code=ErrorCodes.HTTP_169_DATABASE_ERROR_WHILE_RETRIEVING_ANNOUNCEMENTS.value, e=e)
        except Exception as e:
            logger.info(f"An Unexpected error while fetching announcements from database. ERROR: {e}")
            raise e
  
    
    def get_announcement_by_id(self, data):
        announcement_id = data.get('id')
        if announcement_id is None:
            raise ValueError
        try:
            return Notification.objects.get(id=announcement_id)
        except Notification.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_171_NOTIFICATION_DATABASE_ERROR.value, status_code=ErrorCodes.HTTP_171_NOTIFICATION_DATABASE_ERROR.value, e=e)
        except KeyError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_175_MISSING_ID_FOR_NOTIFICATION_DELETION.value, status_code=ErrorCodes.HTTP_175_MISSING_ID_FOR_NOTIFICATION_DELETION.value, e=e)
        except ValueError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_176_NOTIFICATION_ID_MISSING.value, status_code=ErrorCodes.HTTP_176_NOTIFICATION_ID_MISSING.value, e=e)
        except PermissionDenied as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_177_PERMISSION_DENIED_WHILE_DELETING_NOTIFICATION.value, status_code=ErrorCodes.HTTP_177_PERMISSION_DENIED_WHILE_DELETING_NOTIFICATION.value, e=e)
        except Exception as e:
            logger.info(f"An unexpected error occured while fetching notification data. ERROR: {e}")
            raise e
        

class MaintenanceService:
    def get_all_maintenance_notifications(self):
        try:
            maintenances = Notification.objects.filter(notification_type_id=NotificationTypeId.MAINTENANCE_ALERT.value)
            logger.info(f"Retrieved {maintenances.count()} maintenances notifications")
            return maintenances
        except Notification.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_179_DATABASE_ERROR_WHILE_RETRIEVING_ANNOUNCEMENTS.value, status_code=ErrorCodes.HTTP_179_DATABASE_ERROR_WHILE_RETRIEVING_ANNOUNCEMENTS.value, e=e)
        except Exception as e:
            logger.info(f"An Unexpected error while fetching maintenance notifications from the database. ERROR: {e}")
            raise e
        
        
    def get_maintenance_notification_by_id(self, data):
        maintenance_id = data.get('id')
        if maintenance_id is None:
            raise ValueError
        try:
            return Notification.objects.get(id=maintenance_id)
        except Notification.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_171_NOTIFICATION_DATABASE_ERROR.value, status_code=ErrorCodes.HTTP_171_NOTIFICATION_DATABASE_ERROR.value, e=e)
        except KeyError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_175_MISSING_ID_FOR_NOTIFICATION_DELETION.value, status_code=ErrorCodes.HTTP_175_MISSING_ID_FOR_NOTIFICATION_DELETION.value, e=e)
        except ValueError as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_176_NOTIFICATION_ID_MISSING.value, status_code=ErrorCodes.HTTP_176_NOTIFICATION_ID_MISSING.value, e=e)
        except PermissionDenied as e:
            raise NotifyMeException(message=ErrorCodeMessages.HTTP_177_PERMISSION_DENIED_WHILE_DELETING_NOTIFICATION.value, status_code=ErrorCodes.HTTP_177_PERMISSION_DENIED_WHILE_DELETING_NOTIFICATION.value, e=e)
        except Exception as e:
            logger.info(f"An unexpected error occured while fetching maintenance notification data. ERROR: {e}")
            raise e

    