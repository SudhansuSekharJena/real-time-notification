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
from NotifyMe.utils.exceptionManager import NotifyMeException, NotifyMeException, NotifyMeException
from NotifyMe.utils.error_codes import ErrorCodes, ErrorCodeMessages


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
                message=ErrorCodeMessages.HTTP_100_USER_FETCHED_SUCCESSFULLY,
                exc_param=serializer.data,
                status_code=ErrorCodes.HTTP_100_USER_FETCHED_SUCCESSFULLY
            )
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(
                message=e.message,
                status_code=e.status_code,
                exc_param=e.exc_param
            )
        except Exception as e:
            logger.error(f"An Unexpected error occured while fetching users. Error: {e}")
            return Response(f"A Unexpected error occured while fetching users from database. Error: {e}")
        
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return NotifyMeException.handle_success(message=ErrorCodeMessages.HTTP_104_USER_CREATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_104_USER_CREATED_SUCCESSFULLY)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_103_VALIDATION_ERROR_WHILE_CREATING_USER, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_103_VALIDATION_ERROR_WHILE_CREATING_USER)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_106_USER_ALREADY_EXISTS, status_code=ErrorCodes.HTTP_106_USER_ALREADY_EXISTS, exc_param=str(e)) 
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_103_VALIDATION_ERROR_WHILE_CREATING_USER, exc_param=str(e), status_code=ErrorCodes.HTTP_103_VALIDATION_ERROR_WHILE_CREATING_USER) 
        except Exception as e:
            logger.error(f"An Unexpected error occured while posting new user in the database. Error: {e}")
            return Response(f"AN UNEXPECTED ERROR OCCURED WHILE POSTING NEW USER IN THE DATABASE. ERROR:{e}")
    
    def put(self, request):
        user_service = UserService()
        try:
            logger.info("Updating a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=ErrorCodeMessages.HTTP_107_USER_UPDATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_107_USER_UPDATED_SUCCESSFULLY)
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER) 
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except PermissionDenied as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_109_PERMISSION_DENIED_WHILE_UPDATING_USER_DATA, status_code=ErrorCodes.HTTP_109_PERMISSION_DENIED_WHILE_UPDATING_USER_DATA, exc_param=str(e))
        except KeyError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, exc_param=str(e))
        except Exception as e:
            logger.error(f"An unexpected error occured while updating user. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER. ERROR: {e}")
    
    def patch(self, request):
        user_service = UserService()
        try:
            logger.info("Patching a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=ErrorCodeMessages.HTTP_107_USER_UPDATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_107_USER_UPDATED_SUCCESSFULLY)
                 
            else:
                logger.error(f"Validation error occurred while patching a user")
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER, exc_param=serializer.errors, status=ErrorCodes.HTTP_140_VALIDATION_ERROR_WHILE_UPDATING_USER) 
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except PermissionDenied as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_109_PERMISSION_DENIED_WHILE_UPDATING_USER_DATA, status_code=ErrorCodes.HTTP_109_PERMISSION_DENIED_WHILE_UPDATING_USER_DATA, exc_param=str(e))    
        except KeyError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, exc_param=str(e))
        except Exception as e:
            logger.error(f"Un-expected error occured while updating user. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER. ERROR: {e}")
             
    
    def delete(self, request):
        user_service = UserService()
        try:
            logger.info("Deleting a user")
            data = request.data
            user = user_service.get_user_by_id(data)
            user.delete()
            return NotifyMeException.handle_success(message=ErrorCodeMessages.HTTP_113_USER_DELETED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_113_USER_DELETED_SUCCESSFULLY)      
        except PermissionDenied as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_112_PERMISSION_DENIED_WHILE_DELETING_USER_DATA,  status=ErrorCodes.HTTP_112_PERMISSION_DENIED_WHILE_DELETING_USER_DATA, exc_param=str(e))
        except KeyError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages.HTTP_115_MISSING_ID_IN_REQUEST_FOR_USER_DELETION, status_code=ErrorCodes.HTTP_115_MISSING_ID_IN_REQUEST_FOR_USER_DELETION, exc_param=str(e))
        except Exception as e:
            logger.error(f"Unexpected error occured while deleting user. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_OCCURED_WHILE_DELETING_USER. ERROR: {e}")
             
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):
    def get(self, request):
        subscription_service = SubscriptionService()
        try:
            objects = subscription_service.get_all_subscriptions(request)
            serializer = SubscriptionSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages.HTTP_116_SUBSCRIPTION_DATA_FETCHED_SUCCESSFULLY, exc_param=serializer.data, status_code=ErrorCodes.HTTP_116_SUBSCRIPTION_DATA_FETCHED_SUCCESSFULLY)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except Exception as e:
            logger.error(f"An unexpected error occured while fetching Subscription. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_DATA. ERROR: {e}")
             

    def post(self, request):
        try:
            data = request.data
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages.HTTP_119_SUBSCRIPTION_DATA_CREATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_119_SUBSCRIPTION_DATA_CREATED_SUCCESSFULLY)
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA)       
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_120_SUBSCRIPTION_DATA_ALREADY_EXISTS, status_code=ErrorCodes.HTTP_120_SUBSCRIPTION_DATA_ALREADY_EXISTS, exc_param=str(e))
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA, exc_param=str(e), status_code=ErrorCodes.HTTP_121_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA)
        except Exception as e:
            logger.error(f"Unexpected error while creating Subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA. ERROR: {e}")
             

    def put(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY)
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages.HTTP_125_VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_125_VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except Exception as e:
            logger.error(f"Unexpected Error occured while updating Subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA. ERROR: {e}")

    def patch(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_123_SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY)
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages.HTTP_125_VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_125_VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except Exception as e:
            logger.error(f"Unexpected error occured while updating Subscription data. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA. ERROR: {e}")
             

    def delete(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            subscription = subscription_service.get_subscription_by_id(data)
            subscription.delete()
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages.HTTP_128_SUBSCRIPTION_DELETED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_128_SUBSCRIPTION_DELETED_SUCCESSFULLY) 
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except Exception as e:
            logger.error(f"Unexpected error occured")
            return Response(f"UNEXPECTED_ERROR_WHILE_DELETING_SUBSCRIPTION_DATA. ERROR: {e}")

             

class SubscriptionPlanAPI(APIView):
    def get(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = subscription_plan_service.get_all_subscription_plans(request)
            serializer = SubscriptionPlanSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages.HTTP_130_SUBSCRIPTION_PLAN_FETCHED_SUCCESSFULLY, exc_param=serializer.data, status_code=ErrorCodes.HTTP_130_SUBSCRIPTION_PLAN_FETCHED_SUCCESSFULLY)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except Exception as e:
            logger.info(f"Unexpected error occured while fetching fetching Subscription Plans. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_PLANS. ERROR:{e}")
             

    def post(self, request):
        try:
            logger.info("Creating new Subscription-Plan")
            data = request.data
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages.HTTP_133_SUBSCRIPTION_PLAN_CREATED_SUCCESSFULLY, status_code=ErrorCodes["SUBSCRIPTION_PLAN_CREATED_SUCCESSFULLY"])
                 
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages.HTTP_134_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN, exc_param=serializer.errors, status_code=ErrorCodes.HTTP_134_VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN)       
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_136_INTEGRITY_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN, exc_param=str(e), status_code=ErrorCodes.HTTP_136_INTEGRITY_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN)     
        except Exception as e:
            logger.error(f"Unexpected error occured while creating New Subscription-Plan. ERROR: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN. ERROR: {e}")
             

    def delete(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            data = request.data
            subscriptionPlan = subscription_plan_service.get_subscription_plan_by_id(data)
            subscriptionPlan.delete()
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages.HTTP_137_SUBSCRIPTION_PLAN_DELETED_SUCCESSFULLY, status_code=ErrorCodes.HTTP_137_SUBSCRIPTION_PLAN_DELETED_SUCCESSFULLY)
        except NotifyMeException as e:
            return NotifyMeException.handle_api_exception(message=e.message, status_code=e.status_code, exc_param=e.exc_param)
        except PermissionDenied as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_139_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_PLAN_DATA, status_code=ErrorCodes.HTTP_139_PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_PLAN_DATA, exc_param=str(e))
        except KeyError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, status_code=ErrorCodes.HTTP_110_MISSING_ID_WHILE_REQUESTING_FOR_UPDATE, exc_param=str(e))
             
        except Exception as e:
            logger.error(f"Unexpected error while deleting Subscription Plan. Error: {e}")
            return Response(f"UNEXPECTED_ERROR_WHILE_DELETING_SUBSCRIPTION_PLAN. ERROR: {e}")
             


    

