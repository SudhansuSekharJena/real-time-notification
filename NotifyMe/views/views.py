import logging
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from ..serializers import UserSerializer, SubscriptionSerializer, SubscriptionPlanSerializer
from ..serializers import MaintenanceSerializer
from NotifyMe.models.user import User
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.maintenanceModel import MaintenanceModel
from datetime import datetime
from rest_framework import status 
from rest_framework.views import APIView
from NotifyMe.services.service import UserService, SubscriptionService, SubscriptionPlanService, SubscriptionNotificationService, MaintenanceNotificationService
from NotifyMe.constants import plans, plans_duration, plans_id



logger = logging.getLogger(__name__)


# ---------USER-API---------------- 
# DONOT CALL MODEL INSIDE VIEW---> ONLY CALL SERVICE AND SERIALIZER

def get_response_data(success, message=None, data=None):
    response_data = {'success': success}
    if message:
        response_data['message'] = message
    if data is not None:
        response_data['data'] = data
    return response_data

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotifySubscriptionEndAPI(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subscription_notification_service = SubscriptionNotificationService()

    def get(self, request):
        try:
            expiration_threshold = timezone.now() + timedelta(days=7)
            expired_subscriptions = self.subscription_notification_service.get_expiring_subscriptions(expiration_threshold)
            
            for subscription in expired_subscriptions:
                try:
                    self.subscription_notification_service.send_expiration_notification(subscription)
                except Exception as e:
                    logger.error(f"Failed to send notification for subscription {subscription.id}: {e}")
                    continue
            
            response_data = get_response_data(success=True, message="Notifications sent")
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Failed to check expiring subscriptions: {e}")
            response_data = get_response_data(success=False, message=str(e))
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                           
        
class UserAPI(APIView):
    
    def __init__(self):
        self.user_service = UserService()
        
    def get(self, request):
        try:
            logger.info("Fetching user data")
            objects = self.user_service.get_user_data()
            serializer = UserSerializer(objects, many=True)
            logger.info("Successfully fetched user data")
            return Response(get_response_data(True, data=serializer.data))
        except PermissionDenied:
            logger.warning("Permission denied while fetching user data")
            return Response(get_response_data(False, "You don't have permission to access this data"), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching user data: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return Response(get_response_data(True, "User added successfully"), status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Validation error occurred while creating a user: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            logger.warning("Invalid subscription plan ID provided")
            return Response(get_response_data(False, "Invalid subscription plan ID"), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.warning("Integrity error: A user with this information already exists")
            return Response(get_response_data(False, "A user with this information already exists"), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            logger.warning(f"Validation error occurred: {e}")
            return Response(get_response_data(False, str(e)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating a user: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        try:
            logger.info("Updating a user")
            data = request.data
            user = self.user_service.get_userId_data(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User updated successfully")
                return Response(get_response_data(True, "Updated successfully"))
            else:
                logger.warning(f"Validation error occurred while updating a user: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.warning("User not found for update")
            return Response(get_response_data(False, "User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while updating user data")
            return Response(get_response_data(False, "You don't have permission to update this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for update")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while updating a user: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        try:
            logger.info("Patching a user")
            data = request.data
            user = self.user_service.get_userId_data(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("User patched successfully")
                return Response(get_response_data(True, "Patched successfully"))
            else:
                logger.warning(f"Validation error occurred while patching a user: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.warning("User not found for patch")
            return Response(get_response_data(False, "User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while patching user data")
            return Response(get_response_data(False, "You don't have permission to update this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for patch")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while patching a user: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        try:
            logger.info("Deleting a user")
            data = request.data
            user = self.user_service.get_userId_data(data)
            user.delete()
            logger.info("User deleted successfully")
            return Response(get_response_data(True, "Deleted successfully"))
        except User.DoesNotExist:
            logger.warning("User not found for deletion")
            return Response(get_response_data(False, "User not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while deleting user data")
            return Response(get_response_data(False, "You don't have permission to delete this user"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for deletion")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting a user: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):
    def __init__(self):
        self.subscription_service = SubscriptionService()
        

    def get(self, request):
        try:
            objects = self.subscription_service.get_subscription_data(request)
            serializer = SubscriptionSerializer(objects, many=True)
            return Response(get_response_data(True, data=serializer.data))
        except Subscription.DoesNotExist:
            logger.warning(f"No subscriptions found for user {request.user}")
            return Response(get_response_data(False, "No subscriptions found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user} while accessing subscriptions")
            return Response(get_response_data(False, "You don't have permission to access this data"), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error in GET /subscriptions: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"New subscription created by user {request.user}")
                return Response(get_response_data(True, "Subscription added successfully"), status=status.HTTP_201_CREATED)
            else:
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.warning(f"Duplicate subscription attempted by user {request.user}")
            return Response(get_response_data(False, "A subscription with this information already exists"), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            logger.warning(f"Validation error in subscription creation: {e}")
            return Response(get_response_data(False, str(e)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in POST /subscriptions: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            data = request.data
            subscription = self.subscription_service.get_subscriptionId_data(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Subscription {subscription.id} updated by user {request.user}")
                return Response(get_response_data(True, "Updated successfully"))
            else:
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            logger.warning(f"Update attempted on non-existent subscription by user {request.user}")
            return Response(get_response_data(False, "Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user} while updating subscription")
            return Response(get_response_data(False, "You don't have permission to update this subscription"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for PUT /subscriptions")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in PUT /subscriptions: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            subscription = self.subscription_service.get_subscriptionId_data(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Subscription {subscription.id} patched by user {request.user}")
                return Response(get_response_data(True, "Patched successfully"))
            else:
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            logger.warning(f"Patch attempted on non-existent subscription by user {request.user}")
            return Response(get_response_data(False, "Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user} while patching subscription")
            return Response(get_response_data(False, "You don't have permission to update this subscription"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for PATCH /subscriptions")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in PATCH /subscriptions: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            data = request.data
            subscription = self.subscription_service.get_subscriptionId_data(data)
            subscription.delete()
            logger.info(f"Subscription {subscription.id} deleted by user {request.user}")
            return Response(get_response_data(True, "Deleted successfully"))
        except Subscription.DoesNotExist:
            logger.warning(f"Deletion attempted on non-existent subscription by user {request.user}")
            return Response(get_response_data(False, "Subscription not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user} while deleting subscription")
            return Response(get_response_data(False, "You don't have permission to delete this subscription"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for DELETE /subscriptions")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in DELETE /subscriptions: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubscriptionPlanAPI(APIView):
    def __init__(self):
        self.subscriptionPlan_service = SubscriptionPlanService()
        
    def get(self, request):
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = self.subscriptionPlan_service.get_subscriptionPlan_data(request)
            serializer = SubscriptionPlanSerializer(objects, many=True)
            logger.info("Successfully fetched SubscriptionPlan data")
            return Response(get_response_data(True, data=serializer.data))
        except PermissionDenied:
            logger.warning("Permission denied while fetching Subscription-Plan data")
            return Response(get_response_data(False, "You don't have permission to access this data"), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching user data: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
            logger.info("Creating new Subscription-Plan")
            data = request.data
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Subscription-Plan created successfully")
                return Response(get_response_data(True, "Subscription-Plan added successfully"), status = status.HTTP_201_CREATED)
            else:
                logger.warning(f"Validation error occurred while creating a Subscription-Plan: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request):
        try:
            logger.info("Deleting a Subscription-Plan")
            data = request.data # id came in Json--deserialize it
            subscriptionPlan = self.subscriptionPlan_service.get_subscriptionPlan_id(data)
            subscriptionPlan.delete()
            logger.info("Subscription-Plan deleted successfully")
            return Response(get_response_data(True, "Deleted successfully"))
        except SubscriptionPlan.DoesNotExist:
            logger.warning("Subscription-Plan not found for deletion")
            return Response(get_response_data(False, "Subscription-Plan not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning("Permission denied while deleting Subscription-Plan data")
            return Response(get_response_data(False, "You don't have permission to delete this Subscription-Plan"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning("Missing 'id' in the request data for deletion")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting a Subscription-Plan: {e}")
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        
class MaintenanceNotificationAPI(APIView):
    def __init__(self):
        self.maintenance_notification_service = MaintenanceNotificationService()
        
    def get(self, request):
        objects = self.maintenance_notification_service.get_maintenance_data()
        serializer = MaintenanceSerializer(objects, many=True)
        logger.info("Successfully fetched Maintenance data")
        return Response(get_response_data(True, data=serializer.data))
    
    
    def post(self, request):
        logger.info("Creating new Maintenance Notification")
        data = request.data 
        serializer = MaintenanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Maintenance Alert created Successfully")
            return Response(get_response_data(True, "Maintenance Alert added successfully"), status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"Validation error occurred while creating a maintenance alert: {serializer.errors}")
            return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
        
    
        
        
        
  
  

