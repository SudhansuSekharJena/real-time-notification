import logging
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from NotifyMe.constants import Plans, PlansDuration
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User
from django.db import DatabaseError


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
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            raise ValidationError(f"Object does not exist error: {e}")
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            raise ValidationError(f"Multiple objects returned error: {e}")
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise ValidationError(f"Database error: {e}")
        except Exception as e:
            logger.error(f"General error: {e}")
            raise ValidationError(f"General error: {e}")

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
        try:
            user_id = data.get('id')
            if user_id is None:
                raise ValidationError("User ID is missing from the data")
            
            user = User.objects.get(id=user_id)
            return user
        except ObjectDoesNotExist:
            logger.error(f"User with id {user_id} does not exist")
            raise ValidationError(f"User with id {user_id} does not exist")
        except ValueError as e:
            logger.error(str(e))
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"An error occurred while fetching user data: {str(e)}")
            raise ValidationError(f"An error occurred while fetching user data: {str(e)}")

    def get_end_time(self, subscription_plan, start_date):
        """
        Calculate the end-date of subscription based on its plan.
        
        Args:
          subscription_plan(SubscriptionPlan):  The subscription plan.
          start_date(datetime): The start date of the subscription.
          
        Returns:
            datetime: The calculated end date of the subscription according to PlanType.
            
        Raises:
            ValidationError: If the subscription plan is invalid or if there are errors in the calculation.
        
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
            logger.error(f"KeyError: {e} - One of the keys was not found in the plans or plans_duration dictionary.")
            raise ValidationError(f"KeyError: {e} - One of the keys was not found in the plans or plans_duration dictionary.")
        except TypeError as e:
            logger.error(f"TypeError: {e} - There was an issue with the type of an argument.")
            raise ValidationError(f"TypeError: {e} - There was an issue with the type of an argument.")
        except AttributeError as e:
            logger.error(f"AttributeError: {e} - The subscription_plan object does not have the expected attribute.")
            raise ValidationError(f"AttributeError: {e} - The subscription_plan object does not have the expected attribute.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise ValidationError(f"An unexpected error occurred: {e}")
        
    def create_user(self, validated_data):
        
        """
        Create a new user and their subscription.
        
        Args: 
            validated_data (dict): A dictionary containing the validated user data. Eg: VALIDATED DATA: {'subscription_plan': <SubscriptionPlan: STANDARD>, 'email_id': 'raklt@gmail.com
            
        Returns:
             User: A new created User object.
             
        Raises:
             ValidationError: If there is any error while creating the user or their subscription.
        """
        try:
            subscription_plan = validated_data.pop('subscription_plan')  # contains key:value pair of subscription_plan and its value but its an instance.

            if subscription_plan is None:
                raise ValidationError("The 'subscription_plan' field is required.")

            user = User.objects.create(subscription_plan=subscription_plan, **validated_data)

            start_date = timezone.now()
            end_date = self.get_end_time(subscription_plan, start_date)
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
    
    
    """
    Retrieve all subscriptions from the database.
    
    Args: 
       request(HttpRequest): The request object.
       
    Returns:
        QuerySet: A QuerySet of all Subscription objects.
        
    Raises:
        ValidationError: If there is an error retrieving the subscriptions.
    
    """
    def get_all_subscriptions(self, request):
        try:
            subscriptions = Subscription.objects.all()
            logger.info(f"Retrieved all subscriptions: {subscriptions}")
            return subscriptions
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            raise e
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            raise e
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise e
        except Exception as e:
            logger.error(f"General error: {e}")
            raise e
        
    def get_subscription_by_id(self, data):
        
        """
        Retrieve Subscription by ID
        
        Args:
           data(dict): A dictionary containing Subscription ID.
           
        Returns:
            Subscription: The Subscription object with the given ID.
            
        Raises:
            ValidationError: If Subscription ID is missing or if there is an error retrieving the subscription.
        
        """
        try:
            subscription_id = data.get('id')
            if subscription_id is None:
                error_message = "No ID provided in the data."
                logger.error(error_message)
                raise ValueError(error_message)
            
            subscription = Subscription.objects.get(id=subscription_id)
            logger.info(f"Retrieved subscription with ID {subscription_id}: {subscription}")
            return subscription
        except ObjectDoesNotExist as e:
            logger.error(f"Subscription with the given ID does not exist: {e}")
            raise e
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple subscriptions found with the same ID: {e}")
            raise e
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise e     
        
class SubscriptionPlanService:
    def get_all_subscription_plans(self, request):
        """
        Retrieves all Subscription plans from the database.
        
        Args:
           request(HttpRequest): The request object.
           
        Returns:
           QuerySet: A QuerySet of all SubscriptionPlan objects.
           
        Raise: 
            ValidationError: If there is an error retrieving the subscription plans.
        
        """
        
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            logger.info(f"Retrieved all subscription plans: {subscription_plans}")
            return subscription_plans
        except ObjectDoesNotExist as e:
            logger.error(f"Object does not exist error: {e}")
            raise e
        except MultipleObjectsReturned as e:
            logger.error(f"Multiple objects returned error: {e}")
            raise e
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise e
        except Exception as e:
            logger.error(f"General error: {e}")
            raise e
        
        
    def get_subscription_plan_by_id(self, data):
        """
        Retrieve a subscription plan by its ID.
        
        Args: 
          data(dict): A dictionary containing the subscription with the given ID.
          
        Returns:
           SubscriptionPlan: A SubscriptionPlan object with the given ID.
           
        Raise:
            ValidationError: If the subscription plan ID is missing or if there is an error retrieving the subscription plan.
        
        """
        
        try:
            plan_id = data.get('id')
            if plan_id is None:
                error_message = "Subscription Plan ID is missing from the data"
                logger.error(error_message)
                raise ValueError(error_message)
            
            # Note: Use .get() instead of .all() to retrieve a single object
            subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
            logger.info(f"Retrieved subscription plan with ID {plan_id}: {subscription_plan}")
            return subscription_plan
        except ObjectDoesNotExist:
            logger.error(f"SubscriptionPlan with the given ID does not exist: {e}")
            raise e
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            # Log the error here if you have a logging system set up
            raise Exception(f"An error occurred while fetching subscription plan data: {str(e)}")
       