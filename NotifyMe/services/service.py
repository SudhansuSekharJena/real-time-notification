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
from NotifyMe.utils.websocket_utils import CustomException


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
        except DatabaseError as e:
            logger.error(f"Failed to retrieve all users due to a database error: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occured while retrieving all users: {e}", exc_info=True)
            raise CustomException.handle_exception(e)

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
        except ObjectDoesNotExist as e:
            logger.error(f"User with id {user_id} does not exist: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while fetching user data: {e}", exc_info=True)
            raise CustomException.handle_exception(e)

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
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while calculating end date: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        
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
        subscription_plan = validated_data.pop('subscription_plan', None)

        if subscription_plan is None:
            logger.error("Attempt to create user without subscription plan")
            raise ValueError("The 'subscription_plan' field is required.")

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
        except IntegrityError as e:
            logger.error(f"IntegrityError while creating user: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while creating user: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        

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
        except DatabaseError as e:
            logger.error(f"Database error while retrieving all subscriptions: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscriptions: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        
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
        except ObjectDoesNotExist as e:
            logger.error(f"Subscription with ID {subscription_id} does not exist: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving subscription with ID {subscription_id}: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        
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
        except DatabaseError as e:
            logger.error(f"Database error while retrieving all subscription plans: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving all subscription plans: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        
        
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
        except ObjectDoesNotExist as e:
            logger.error(f"SubscriptionPlan with ID {plan_id} does not exist: {e}", exc_info=True)
            raise CustomException.handle_exception(e)
        except Exception as e:
            logger.error(f"An Unexpected error occurred while retrieving subscription plan with ID {plan_id}: {e}",exc_info=True)
            raise CustomException.handle_exception(e)
        

       