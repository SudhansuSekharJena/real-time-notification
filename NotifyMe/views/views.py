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
from NotifyMe.utils.exceptionManager import CustomException, SuccessHandler, ExceptionHandler



logger = logging.getLogger(__name__)


# ---------USER-API---------------- 
# DONOT CALL MODEL INSIDE VIEW---> ONLY CALL SERVICE AND SERIALIZER
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
            return Response(SuccessHandler.handle_success("Successfully fetched user data", data=serializer.data))
        except User.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("No users found for user", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception("Unexpected error occurred while fetching user data", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return Response(SuccessHandler.handle_success("User added successfully", status_code=201), status=status.HTTP_201_CREATED)
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while creating a user: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("Invalid subscription plan ID provided", status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(ExceptionHandler.handle_api_exception("Integrity error: A user with this information already exists", status_code=409), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            return Response(ExceptionHandler.handle_api_exception("Validation error occurred", data=e, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception("Unexpected error occurred while creating a user", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        user_service = UserService()
        try:
            logger.info("Updating a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success("User updated successfully"))
            else:

                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while updating a user: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("User not found for update", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response(ExceptionHandler.handle_api_exception("Permission denied while updating user data", status_code=403), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            return Response(ExceptionHandler.handle_api_exception("Missing 'id' in the request data for update", status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception("An unexpected error occurred", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        user_service = UserService()
        try:
            logger.info("Patching a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success( "User patched successfully"))
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while patching a user: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("User not found for patch", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response(ExceptionHandler.handle_api_exception("Permission denied while patching user data", status_code=403), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            return Response(ExceptionHandler.handle_api_exception("Missing 'id' in the request data for patch", status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error occurred while patching a user: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        user_service = UserService()
        try:
            logger.info("Deleting a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            user.delete()
            return Response(SuccessHandler.handle_success("User deleted successfully"))
        except User.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("User not found for deletion", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response(ExceptionHandler.handle_api_exception("Permission denied while deleting user data", status_code=403), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            return Response(ExceptionHandler.handle_api_exception("Missing 'id' in the request data for deletion", status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error occurred while deleting a user: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):       

    def get(self, request):
        subscription_service = SubscriptionService()
        try:
            objects = subscription_service.get_all_subscriptions(request)
            serializer = SubscriptionSerializer(objects, many=True)
            return Response(SuccessHandler.handle_success(
            "Successfully fetched user data", data=serializer.data))
        except Subscription.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception(f"No subscriptions found", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error in GET /subscriptions: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success( f"New subscription created", status_code=201), status=status.HTTP_201_CREATED)
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while creating a subscription data: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(ExceptionHandler.handle_api_exception(f"Duplicate subscription attempted by user", status_code=409), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            return Response(ExceptionHandler.handle_api_exception(f"Validation error in subscription creation: {e}", data=e, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error in POST /subscriptions: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success( f"Subscription {subscription.id} updated by user {request.user}", status_code=202), status=status.HTTP_202_ACCEPTED)
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while updating a subscription: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception(f"Update attempted on non-existent subscription by user {request.user}", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error in PUT /subscriptions: {e}", status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success( f"Subscription {subscription.id} patched by user {request.user}", status_code=202), status=status.HTTP_202_ACCEPTED)
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while patching a Subscription: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception(f"Patch attempted on non-existent subscription by user {request.user}", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error in PATCH /subscriptions: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            subscription.delete()
            return Response(SuccessHandler.handle_success(f"Subscription {subscription.id} deleted by user {request.user}", status_code=200))
        except Subscription.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception(f"Deletion attempted on non-existent subscription by user {request.user}", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error in DELETE /subscriptions: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubscriptionPlanAPI(APIView):
        
    def get(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = subscription_plan_service.get_all_subscription_plans(request)
            serializer = SubscriptionPlanSerializer(objects, many=True)
            return Response(SuccessHandler.handle_success("Successfully fetched SubscriptionPlan data", data=serializer.data), status=status.HTTP_200_OK)
        except SubscriptionPlan.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("No subscription plans found", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error occurred while fetching user data: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            logger.info("Creating new Subscription-Plan")
            data = request.data
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(SuccessHandler.handle_success( "Subscription-Plan added successfully", status_code=201), status=status.HTTP_201_CREATED)
            else:
                return Response(ExceptionHandler.handle_api_exception(f"Validation error occurred while creating a Subscription-Plan: {serializer.errors}", data=serializer.errors, status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response(ExceptionHandler.handle_api_exception(f"IntegrityError occurred while creating Subscription-Plan: {e}", data=e, status_code=409), status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error occurred while creating Subscription-Plan: {e}", data=e, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            data = request.data # id came in Json--deserialize it
            subscriptionPlan = subscription_plan_service.get_subscription_plan_by_id(data)
            subscriptionPlan.delete()
            return Response(SuccessHandler.handle_success("Subscription-Plan deleted successfully"))
        except SubscriptionPlan.DoesNotExist:
            return Response(ExceptionHandler.handle_api_exception("Subscription-Plan not found for deletion", status_code=404), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response(ExceptionHandler.handle_api_exception("Permission denied while deleting Subscription-Plan data", status_code=403), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            return Response(ExceptionHandler.handle_api_exception("Missing 'id' in the request data", status_code=400), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ExceptionHandler.handle_api_exception(f"Unexpected error occurred while deleting a Subscription-Plan: {e}", data=E, status_code=500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    

