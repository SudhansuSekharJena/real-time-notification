import logging
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from ..serializers import UserSerializer, SubscriptionSerializer, SubscriptionPlanSerializer, NotificationSerializer
from NotifyMe.models.user import User
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.notification import Notification
from NotifyMe.models.notificationType import NotificationType
from rest_framework import status 
from rest_framework.views import APIView
from NotifyMe.services.service import UserService, SubscriptionService, SubscriptionPlanService, AnnouncementsService, MaintenanceService
from NotifyMe.utils.exceptionManager import NotifyMeException, NotifyMeException, NotifyMeException
from NotifyMe.utils.error_codes import ErrorCodes, ErrorCodeMessages
from NotifyMe.utils.error_codes import SuccessCodes, SuccessCodeMessages
from rest_framework import status
from NotifyMe.constants import NotificationTypeId
from NotifyMe.utils.websocket_utils import NotificationManager

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
            return NotifyMeException.handle_success(
                message=SuccessCodeMessages.HTTP_100_USER_FETCHED_SUCCESSFULLY.value,
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(
                message=e.message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"An Unexpected error occured while fetching users. ERROR: {e}")
            return Response(f"A Unexpected error occured while fetching users from database.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_104_USER_CREATED_SUCCESSFULLY.value,
                status_code=status.HTTP_201_CREATED)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_162_USER_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_106_USER_ALREADY_EXISTS.value, status_code=status.HTTP_409_CONFLICT, e=e) 
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_103_VALIDATION_ERROR_WHILE_CREATING_USER.value, status_code=status.HTTP_400_BAD_REQUEST, e=e) 
        except Exception as e:
            logger.error(f"An Unexpected error occured while posting new user in the database. ERROR: {e}")
            return Response(f"AN UNEXPECTED ERROR OCCURED WHILE POSTING NEW USER IN THE DATABASE.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        user_service = UserService()
        try:
            logger.info("Updating a user")
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_162_USER_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_107_USER_UPDATED_SUCCESSFULLY.value, status_code=status.HTTP_200_OK)
            else:
                raise ValidationError(serializer.errors)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER.value,  status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occured while updating user. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        user_service = UserService()
        try:
            logger.info("Patching a user")
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_164_USER_PATCH.value, status_code=status.HTTP_400_BAD_REQUEST)
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_107_USER_UPDATED_SUCCESSFULLY.value, status_code=status.HTTP_200_OK)
            else:
                raise ValidationError(serializer.errors)        
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER.value,  status_code=status.HTTP_400_BAD_REQUEST, e=e)
        except Exception as e:
            logger.error(f"Un-expected error occured while updating user. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             
    
    def delete(self, request):
        user_service = UserService()
        try:
            logger.info("Deleting a user")
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_166_USER_DELETE.value, status_code=status.HTTP_400_BAD_REQUEST)
            user = user_service.get_user_by_id(data)
            
            user_service.delete_user(user) # delete
            
            return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_113_USER_DELETED_SUCCESSFULLY.value, status_code=status.HTTP_204_NO_CONTENT)      
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error occured while deleting user. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_DELETING_USER.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):
    def get(self, request):
        subscription_service = SubscriptionService()
        try:
            logger.info("Fetching Subscriptions data")
            objects = subscription_service.get_all_subscriptions()
            serializer = SubscriptionSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=SuccessCodeMessages.HTTP_116_SUBSCRIPTION_DATA_FETCHED_SUCCESSFULLY.value, data=serializer.data, status_code=status.HTTP_200_OK)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while fetching Subscription. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_DATA.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             

    def post(self, request):
        try:
            logger.info("Creating new Subscription")
            data = request.data
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=SuccessCodeMessages.HTTP_119_SUBSCRIPTION_DATA_CREATED_SUCCESSFULLY.value, status_code=status.HTTP_201_CREATED)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_163_SUBSCRIPTION_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)  
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER.value,  status_code=status.HTTP_400_BAD_REQUEST, e=e)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_120_SUBSCRIPTION_DATA_ALREADY_EXISTS.value, status_code=status.HTTP_409_CONFLICT, e=e)
        except Exception as e:
            logger.error(f"Unexpected error while creating Subscription data. ERROR: {e}")
            return Response(f" AN UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             

    def put(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_163_SUBSCRIPTION_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST) 
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=SuccessCodeMessages.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY.value,
                    status_code=status.HTTP_200_OK)
            else:
                raise ValidationError(serializer.errors)
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA.value,  status_code=status.HTTP_400_BAD_REQUEST)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected Error occured while updating Subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA.",  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_165_SUBSCRIPTION_DATA_PATCH.value, status_code=status.HTTP_400_BAD_REQUEST) 
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=SuccessCodeMessages.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY.value,
                    status_code=status.HTTP_200_OK)
            else:
                raise ValidationError
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA.value,  status_code=status.HTTP_400_BAD_REQUEST)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error occured while updating Subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA.",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             

    def delete(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_167_SUBSCRIPTION_DATA_DELETE.value, status_code=status.HTTP_400_BAD_REQUEST) 
            subscription = subscription_service.get_subscription_by_id(data)
            
            subscription_service.delete_subscription(subscription) # delete
            
            return NotifyMeException.handle_success(
                message=SuccessCodeMessages.HTTP_128_SUBSCRIPTION_DELETED_SUCCESSFULLY.value,
                status_code=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA.value, status_code=status.HTTP_400_BAD_REQUEST) 
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error occured while deleting subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_DELETING_SUBSCRIPTION_DATA.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

             

class SubscriptionPlanAPI(APIView):
    def get(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = subscription_plan_service.get_all_subscription_plans(request)
            serializer = SubscriptionPlanSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=SuccessCodeMessages.HTTP_130_SUBSCRIPTION_PLAN_FETCHED_SUCCESSFULLY.value,
                data=serializer.data,
                status_code=status.HTTP_200_OK)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.info(f"Unexpected error occured while fetching fetching Subscription Plans. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_PLANS.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             

    def post(self, request):
        try:
            logger.info("Creating new Subscription-Plan")
            data = request.data
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=SuccessCodeMessages.HTTP_133_SUBSCRIPTION_PLAN_CREATED_SUCCESSFULLY.value,
                    status_code=status.HTTP_201_CREATED)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_168_SUBSCRIPTION_PLAN_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)  
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_136_INTEGRITY_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN.value, status_code=status.HTTP_409_CONFLICT, e=e)     
        except Exception as e:
            logger.error(f"Unexpected error occured while creating New Subscription-Plan. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             

    def delete(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            data = request.data
            if not data:
                 return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_168_SUBSCRIPTION_PLAN_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
            subscriptionPlan = subscription_plan_service.get_subscription_plan_by_id(data)
            
            subscription_plan_service.delete_subscription_plan(subscriptionPlan) # delete
            
            return NotifyMeException.handle_success(
                message=SuccessCodeMessages.HTTP_137_SUBSCRIPTION_PLAN_DELETED_SUCCESSFULLY.value, status_code=status.HTTP_204_NO_CONTENT)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error while deleting Subscription Plan. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_DELETING_SUBSCRIPTION_PLAN.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             
class AnnouncementAPI(APIView):
    def get(self, request):
        announcements_service = AnnouncementsService()
        try:
            objects = announcements_service.get_all_announcements()
            serializer = NotificationSerializer(objects, many=True)
            return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_170_ANNOUNCEMETS_FETCHED_SUCCESSFULY.value, data=serializer.data, status_code=status.HTTP_100_CONTINUE)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while fetching announcements from the database. ERROR: {e}")
            return Response(f"An unexpected error occured while fetching announcements from the database.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            notification_manager = NotificationManager()
            data = request.data
            announcement_message = data.get("message")
            if announcement_message is None:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_174_NOTIFICATION_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
            
            announcement_object = {
                "message": announcement_message,
                "title": NotificationTypeId.ANNOUNCEMENTS.name,
                "notification_type": NotificationTypeId.ANNOUNCEMENTS.value
            }
            
            serializer = NotificationSerializer(data=announcement_object)
            if serializer.is_valid():
                serializer.save()
                notification_manager.announcement_notification("Our_clients", announcement_message, NotificationTypeId.ANNOUNCEMENTS.value) 
                return NotifyMeException.handle_success(
                    message=SuccessCodeMessages.HTTP_173_NOTIFICATION_CREATED_SUCCESSFULLY.value,
                    status_code=status.HTTP_201_CREATED)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_181_NOTIFICATION_DATA_NOT_GIVEN.value,
                status_code=status.HTTP_400_BAD_REQUEST)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unepected errpr occured while creating new notification. ERROR: {e}")
            return Response(f"UNEXPECTED ERROR OCCURED WHILE CREATING NEW NOTIFICATION.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request):
        announcements_service = AnnouncementsService()
        try:
            data = request.data
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_174_NOTIFICATION_DELETE.value, status_code=status.HTTP_200_OK)
            object = announcements_service.get_announcement_by_id(data)
            
            announcements_service.delete_announcement(object) # delete
            
            return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_178_NOTIFICATION_DELETED_SUCCESSFULLY.value, status_code=SuccessCodes.HTTP_178_NOTIFICATION_DELETED_SUCCESSFULLY.value)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while deleting announcement. ERROR: {e}")
            return Response(f"UNEXPECTED ERROR OCCUED WHILE DELETING ANNOUNCEMENT.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class MaintenanceAPI(APIView):
    def get(self, request):
        maintenance_service = MaintenanceService()
        try:
            objects = maintenance_service.get_all_maintenance_notifications()
            serializer = NotificationSerializer(objects, many=True)
            return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_180_MAINTENANCE_NOTIFICATION_FETCHED_SUCCESSFULY.value, data=serializer.data,  status_code=status.HTTP_100_CONTINUE)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while fetching maintenance notifications from the database. ERROR: {e}")
            return Response(f"An unexpected error occured while fetching maintenance notifications from the database.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        notification_manager = NotificationManager()
        try:
            data = request.data 
            maintenance_message = data.get('message')
            if maintenance_message is None:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_174_NOTIFICATION_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
            
            maintenance_object = {
                "message":maintenance_message,
                "title": NotificationTypeId.MAINTENANCE_ALERT.name,
                "notification_type": NotificationTypeId.MAINTENANCE_ALERT.value
            }
            
            serializer = NotificationSerializer(data=maintenance_object)
            if serializer.is_valid():
                serializer.save()
                notification_manager.maintenance_alert("Our_clients", maintenance_message, NotificationTypeId.MAINTENANCE_ALERT.value)
                return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_173_NOTIFICATION_CREATED_SUCCESSFULLY.value, status_code=status.HTTP_201_CREATED)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_181_NOTIFICATION_DATA_NOT_GIVEN.value, status_code=status.HTTP_400_BAD_REQUEST)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while creating new maintenance alert. ERROR: {e}")
            return Response(f"AN UNEXPECTED ERROR OCCURED WHILE CREATING A NEW MAINTENANCE-ALERT", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def delete(self, request):
        maintenance_service = MaintenanceService()
        try:
            data = request.data 
            if not data:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_174_NOTIFICATION_DELETE.value, status_code=status.HTTP_200_OK)
            object = maintenance_service.get_maintenance_notification_by_id(data)
            object.delete()
            return NotifyMeException.handle_success(message=SuccessCodeMessages.HTTP_178_NOTIFICATION_DELETED_SUCCESSFULLY.value, status_code=status.HTTP_200_OK)
        except NotifyMeException as e:
            return NotifyMeException.handle_exception(message=e.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occured while deleting maintenance-alert. ERROR: {e}")
            return Response(f"AN UNEXPECTED ERROR OCCURED WHILE DELETING MAINTENANCE-ALERT.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
                
        
        
        
        

