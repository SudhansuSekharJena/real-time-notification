import logging
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from ..serializers import UserSerializer, SubscriptionSerializer, NotificationSerializer
from NotifyMe.models.user import User
from NotifyMe.models.notification import Notification
from NotifyMe.models.notificationType import NotificationType
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from rest_framework import status 
from rest_framework.views import APIView
from NotifyMe.services.service import *
from channels.layers import get_channel_layer
from django.http import HttpResponse
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

from asgiref.sync import async_to_sync
logger = logging.getLogger(__name__)

# def index(request):
#     return render(request, 'index.html', {'room_name': "broadcast"
        
#     })
  
# test request...  
# def test(Request):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "notification_broadcast",
#         {
#             'type': 'send_notification',
#             'message': 'Notification'
#         }
#     )
#     return HttpResponse("Done")

# ---------USER-API---------------- 
# DONOT CALL MODEL INSIDE VIEW---> ONLY CALL SERVICE AND SERIALIZER

def get_response_data(success, message=None, data=None):
    response_data = {'success': success}
    if message:
        response_data['message'] = message
    if data is not None:
        response_data['data'] = data
    return response_data


class UserAPI(APIView):
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        
    def get(self, request):
        try:
            logger.info("Fetching user data")
            objects = self.user_service.get_user_data(request)
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
        except self.user_service.get_subscriptionPlanDatabase().DoesNotExist:
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
        except self.user_service.get_userDatabase().DoesNotExist:
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
        except self.user_service.get_userDatabase().DoesNotExist:
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
        except self.user_service.get_userDatabase().DoesNotExist:
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
    def __init__(self, subscription_service: SubscriptionService):
        self.subscription_service = subscription_service
        

    def get(self, request):
        try:
            objects = self.subscription_service.get_subscription_data(request)
            serializer = SubscriptionSerializer(objects, many=True)
            return Response(get_response_data(True, data=serializer.data))
        except self.subscription_service.get_subscriptionDatabase().DoesNotExist:
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
        except self.subscription_service.get_subscriptionDatabase().DoesNotExist:
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
        except self.subscription_service.get_subscriptionDatabase().DoesNotExist:
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
        except self.subscription_service.get_subscriptionDatabase().DoesNotExist:
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

#---------------NOTIFICATION-API---------------------

class NotificationAPI(APIView):
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
    
    def get(self, request):
        try:
            objects = self.notification_service.get_notification_data(request)
            serializer = NotificationSerializer(objects, many=True)
            logger.info(f"Retrieved {len(objects)} notifications for user {request.user.id}")
            return Response(get_response_data(True, data=serializer.data))
        except self.notification_service.get_notificationDatabase().DoesNotExist:
            logger.warning(f"No notifications found for user {request.user.id}")
            return Response(get_response_data(False, "No notifications found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to access notifications")
            return Response(get_response_data(False, "You don't have permission to access this data"), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error in GET /notifications: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            serializer = NotificationSerializer(data=request.data)
            if serializer.is_valid():
                notification = serializer.save()
                logger.info(f"Notification {notification.id} created by user {request.user.id}")
                return Response(get_response_data(True, "Notification added successfully", {"notification_id": notification.id}), status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Invalid notification data submitted by user {request.user.id}: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.warning(f"Duplicate notification attempted by user {request.user.id}")
            return Response(get_response_data(False, "A notification with this information already exists"), status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            logger.warning(f"Validation error for notification by user {request.user.id}: {e}")
            return Response(get_response_data(False, str(e)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in POST /notifications: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        try:
            data = request.data
            notification = self.notification_service.get_notificationId_data(data)
            serializer = NotificationSerializer(notification, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Notification {notification.id} updated by user {request.user.id}")
                return Response(get_response_data(True, "Updated successfully"))
            else:
                logger.warning(f"Invalid update data for notification {notification.id} by user {request.user.id}: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except self.notification_service.get_notificationDatabase().DoesNotExist:
            logger.warning(f"Update attempted on non-existent notification by user {request.user.id}")
            return Response(get_response_data(False, "Notification not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to update notification {data.get('id')}")
            return Response(get_response_data(False, "You don't have permission to update this notification"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning(f"Missing 'id' in PUT request data from user {request.user.id}")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in PUT /notifications: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        try:
            data = request.data
            notification = self.notification_service.get_notificationId_data(data)
            serializer = NotificationSerializer(notification, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Notification {notification.id} patched by user {request.user.id}")
                return Response(get_response_data(True, "Patched successfully"))
            else:
                logger.warning(f"Invalid patch data for notification {notification.id} by user {request.user.id}: {serializer.errors}")
                return Response(get_response_data(False, data=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except self.notification_service.get_notificationDatabase().DoesNotExist:
            logger.warning(f"Patch attempted on non-existent notification by user {request.user.id}")
            return Response(get_response_data(False, "Notification not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to patch notification {data.get('id')}")
            return Response(get_response_data(False, "You don't have permission to update this notification"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning(f"Missing 'id' in PATCH request data from user {request.user.id}")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in PATCH /notifications: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        try:
            data = request.data
            notification = self.notification_service.get_notificationId_data(data)
            notification.delete()
            logger.info(f"Notification {data.get('id')} deleted by user {request.user.id}")
            return Response(get_response_data(True, "Deleted successfully"))
        except self.notification_service.get_notificationDatabase().DoesNotExist:
            logger.warning(f"Deletion attempted on non-existent notification by user {request.user.id}")
            return Response(get_response_data(False, "Notification not found"), status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to delete notification {data.get('id')}")
            return Response(get_response_data(False, "You don't have permission to delete this notification"), status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.warning(f"Missing 'id' in DELETE request data from user {request.user.id}")
            return Response(get_response_data(False, "Missing 'id' in the request data"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in DELETE /notifications: {e}", exc_info=True)
            return Response(get_response_data(False, "An unexpected error occurred"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  

