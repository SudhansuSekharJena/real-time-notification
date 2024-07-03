import logging
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from NotifyMe.constants import Plans, PlansDuration
from django.core.exceptions import ObjectDoesNotExist
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User
from django.db import DatabaseError
from NotifyMe.utils.exceptionManager import NotifyMeException, NotifyMeException
from NotifyMe.utils.error_codes import ErrorCodeMessages, ErrorCodes
import json


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
                message=ErrorCodeMessages[153],
                exc_param=str(e),
                status_code=ErrorCodes["DATABASE_ERROR_WHILE_FETCHING_USERS"])
        except Exception as e:
            logger.error(f"An Unexpected error occured while fetching User from Database. Error: {e}")
            raise json.dumps(e)
            
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
            logger.error("Attempt to get user with missing ID")
            raise ValueError("User ID is missing from the data")
        
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages[101], exc_param=str(e), status_code=ErrorCodes["USER_NOT_FOUND"])
        except Exception as e:
            logger.warning(f"An Unexpected error occurred while fetching user data: {e}")
            raise json.dumps(e)

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

            if plan_type == Plans["BASIC_PLAN"]:
                return start_date + timedelta(days=PlansDuration["BASIC"])
            elif plan_type == Plans["REGULAR_PLAN"]:
                return start_date + timedelta(days=PlansDuration["REGULAR"])
            elif plan_type == Plans["STANDARD_PLAN"]:
                return start_date + timedelta(days=PlansDuration["STANDARD"])
            elif plan_type == Plans["PREMIUM_PLAN"]:
                return start_date + timedelta(days=PlansDuration["PREMIUM"])
            else:
                raise ValidationError("Invalid subscription plan")
        except KeyError as e:
            logger.error(f"Duration not found for plan type: {plan_type}")
            raise NotifyMeException(message=ErrorCodeMessages[154], status_code=ErrorCodes["DURATION_NOT_FOUND_ERROR_FOR_SUBSCRIPTION_PLAN_TYPE"], exc_param=str(e))
        except Exception as e:
            logger.error(f"An Unexpected error occurred while calculating end date: {e}")
            raise json.dumps(e)
        
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
            logger.error("Attempt to create user without subscription plan")
            raise NotifyMeException(message=ErrorCodeMessages[148], status_code=ErrorCodes["SUBSCRIPTION_PLAN_FIELD_IS_REQUIRED"])
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
        except User.DoesNotExist:
            return NotifyMeException.handle_exception(message=ErrorCodeMessages[102], status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_FETCHING_USER"])
        except SubscriptionPlan.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[105], status_code=ErrorCodes["INVALID_SUBSCRIPTION_ID_PROVIDED"])
        except IntegrityError as e:
            raise NotifyMeException(message=ErrorCodeMessages[108], exc_param=str(e), status_code=ErrorCodes["INVALID_USER_ID_PROVIDED"])
        except Exception as e:
            logger.warning(f"An Unexpected error occurred while creating user: {e}")
            raise json.dumps(e)
        

class SubscriptionService: 
    def get_all_subscriptions(self, request):
        
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
            raise NotifyMeException(message=ErrorCodeMessages[144], exc_param=str(e), status_code=ErrorCodes["DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS"])
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscriptions: {e}")
            raise json.dumps(e)
        
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
            logger.error("Attempt to get subscription with missing ID")
            raise ValueError("Subscription ID is missing from the data")
        
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            logger.info(f"Retrieved subscription with ID {subscription_id}")
            return subscription
        except Subscription.DoesNotExist as e:
            raise NotifyMeException(message=ErrorCodeMessages[124], exc_param=str(e), status_code=ErrorCodes["INVALID_SUBSCRIPTION_DATA_ID_PROVIDED"]) 
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving subscription with ID {subscription_id}: {e}")
            raise json.dumps(e)
        
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
            raise NotifyMeException(message=ErrorCodeMessages[145], exc_param=str(e), status_code=ErrorCodes["DATABASE_ERROR_WHILE_RETRIEVING_ALL_SUBSCRIPTIONS_PLANS"])
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscription plans: {e}")
            raise json.dumps(e)
        
        
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
            logger.error("Attempt to get subscription plan with missing ID")
            raise ValueError("Subscription Plan ID is missing from the data")
        
        try:
            subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
            logger.info(f"Retrieved subscription plan with ID {plan_id}")
            return subscription_plan
        except SubscriptionPlan.DoesNotExist as e:
            raise NotifyMeException(f"SubscriptionPlan with ID {plan_id} does not exist: {e}", exc_param=str(e))
        except Exception as e:
            logger.warning(f"An Unexpected error occurred while retrieving subscription plan with ID {plan_id}: {e}")
            raise json.dumps(e)
        

       