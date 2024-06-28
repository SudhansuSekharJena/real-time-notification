import logging
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from ..serializers import UserSerializer, SubscriptionSerializer, SubscriptionPlanSerializer
from NotifyMe.models.user import User
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from rest_framework import status 
from rest_framework.views import APIView
from NotifyMe.services.service import UserService, SubscriptionService, SubscriptionPlanService
from NotifyMe.utils.websocket_utils import CustomException



logger = logging.getLogger(__name__)


# ---------USER-API---------------- 
# DONOT CALL MODEL INSIDE VIEW---> ONLY CALL SERVICE AND SERIALIZER

# def get_response_data(success, message=None, data=None):
#     response_data = {'success': success}
#     if message:
#         response_data['message'] = message
#     if data is not None:
#         response_data['data'] = data
#     return response_data

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

     
class UserAPI(APIView):
        
    def get(self, request):
        user_service = UserService()
        try:
            logger.info("Fetching user data")
            objects = user_service.get_all_users()
            serializer = UserSerializer(objects, many=True)
            logger.info("Successfully fetched user data")
            return Response(CustomException.handle_success(data=serializer.data))
        except User.DoesNotExist:
            logger.warning(f"No users found for user ")
            return Response(CustomException.handle_api_exception("No users found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching user data: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return Response(CustomException.handle_success("User added successfully"), status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Validation error occurred while creating a user: {serializer.errors}")
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            logger.warning("Invalid subscription plan ID provided")
            return Response(CustomException.handle_api_exception("Invalid subscription plan ID"), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.warning("Integrity error: A user with this information already exists")
            return Response(CustomException.handle_api_exception("A user with this information already exists"), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            logger.warning(f"Validation error occurred: {e}")
            return Response(CustomException.handle_api_exception(str(e)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating a user: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        user_service = UserService()
        try:
            logger.info("Updating a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User updated successfully")
                return Response(CustomException.handle_success(True, "Updated successfully"))
            else:
                logger.warning(f"Validation error occurred while updating a user: {serializer.errors}")
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.warning("User not found for update")
            return Response(CustomException.handle_api_exception("User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while updating user data")
            return Response(CustomException.handle_api_exception("You don't have permission to update this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for update")
            return Response(CustomException.handle_api_exception("Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while updating a user: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        user_service = UserService()
        try:
            logger.info("Patching a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("User patched successfully")
                return Response(CustomException.handle_success( "Patched successfully"))
            else:
                logger.warning(f"Validation error occurred while patching a user: {serializer.errors}")
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.warning("User not found for patch")
            return Response(CustomException.handle_api_exception("User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while patching user data")
            return Response(CustomException.handle_api_exception("You don't have permission to update this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for patch")
            return Response(CustomException.handle_api_exception("Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while patching a user: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        user_service = UserService()
        try:
            logger.info("Deleting a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            user.delete()
            logger.info("User deleted successfully")
            return Response(CustomException.handle_success("Deleted successfully"))
        except User.DoesNotExist:
            logger.warning("User not found for deletion")
            return Response(CustomException.handle_api_exception("User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while deleting user data")
            return Response(CustomException.handle_api_exception("You don't have permission to delete this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for deletion")
            return Response(CustomException.handle_api_exception("Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting a user: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):       

    def get(self, request):
        subscription_service = SubscriptionService()
        try:
            objects = subscription_service.get_all_subscriptions(request)
            serializer = SubscriptionSerializer(objects, many=True)
            return Response(CustomException.handle_success( data=serializer.data))
        except Subscription.DoesNotExist:
            logger.warning(f"No subscriptions found for user {request.user}")
            return Response(CustomException.handle_api_exception("No subscriptions found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in GET /subscriptions: {e}", exc_info=True)
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"New subscription created by user {request.user}")
                return Response(CustomException.handle_success( "Subscription added successfully"), status=status.HTTP_201_CREATED)
            else:
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.warning(f"Duplicate subscription attempted by user {request.user}")
            return Response(CustomException.handle_api_exception("A subscription with this information already exists"), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            logger.warning(f"Validation error in subscription creation: {e}")
            return Response(CustomException.handle_api_exception(str(e)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in POST /subscriptions: {e}", exc_info=True)
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Subscription {subscription.id} updated by user {request.user}")
                return Response(CustomException.handle_success( "Updated successfully"))
            else:
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            logger.warning(f"Update attempted on non-existent subscription by user {request.user}")
            return Response(CustomException.handle_api_exception("Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in PUT /subscriptions: {e}", exc_info=True)
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Subscription {subscription.id} patched by user {request.user}")
                return Response(CustomException.handle_success( "Patched successfully"))
            else:
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            logger.warning(f"Patch attempted on non-existent subscription by user {request.user}")
            return Response(CustomException.handle_api_exception("Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in PATCH /subscriptions: {e}", exc_info=True)
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            subscription.delete()
            logger.info(f"Subscription {subscription.id} deleted by user {request.user}")
            return Response(CustomException.handle_success("Deleted successfully"))
        except Subscription.DoesNotExist:
            logger.warning(f"Deletion attempted on non-existent subscription by user {request.user}")
            return Response(CustomException.handle_api_exception("Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in DELETE /subscriptions: {e}", exc_info=True)
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubscriptionPlanAPI(APIView):
        
    def get(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = subscription_plan_service.get_all_subscription_plans(request)
            serializer = SubscriptionPlanSerializer(objects, many=True)
            logger.info("Successfully fetched SubscriptionPlan data")
            return Response(CustomException.handle_success( data=serializer.data))
        except SubscriptionPlan.DoesNotExist:
            logger.warning(f"No subscription plans found")
            return Response(CustomException.handle_api_exception("No subscription plans found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching user data: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            logger.info("Creating new Subscription-Plan")
            data = request.data
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Subscription-Plan created successfully")
                return Response(CustomException.handle_success( "Subscription-Plan added successfully"), status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Validation error occurred while creating a Subscription-Plan: {serializer.errors}")
                return Response(CustomException.handle_api_exception(data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.warning(f"IntegrityError occurred while creating Subscription-Plan: {e}")
            return Response(CustomException.handle_api_exception("A Subscription-Plan with this information already exists"), status=status.HTTP_409_CONFLICT)
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating Subscription-Plan: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Deleting a Subscription-Plan")
            data = request.data # id came in Json--deserialize it
            subscriptionPlan = subscription_plan_service.get_subscription_plan_by_id(data)
            subscriptionPlan.delete()
            logger.info("Subscription-Plan deleted successfully")
            return Response(CustomException.handle_success("Deleted successfully"))
        except SubscriptionPlan.DoesNotExist:
            logger.warning("Subscription-Plan not found for deletion")
            return Response(CustomException.handle_api_exception("Subscription-Plan not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while deleting Subscription-Plan data")
            return Response(CustomException.handle_api_exception("You don't have permission to delete this Subscription-Plan"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for deletion")
            return Response(CustomException.handle_api_exception("Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting a Subscription-Plan: {e}")
            return Response(CustomException.handle_api_exception("An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
        
    
        
        
        
  
  

