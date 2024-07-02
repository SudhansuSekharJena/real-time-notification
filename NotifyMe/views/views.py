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
            if not objects:
                raise NotifyMeException(message = ErrorCodeMessages[149], status_code=ErrorCodes["USER_INSTANCES_NOT_FOUND"])
            serializer = UserSerializer(objects, many=True)
            return NotifyMeException.handle_success(message=ErrorCodeMessages[100], exc_param=serializer.data, status_code=ErrorCodes["USER_FETCHED_SUCCESSFULLY"])
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except User.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[101], status_code=ErrorCodes["USER_NOT_FOUND"])
        except Exception as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[102], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_FETCHING_USER"])

    
    def post(self, request):
        try:
            logger.info("Creating a new user")
            data = request.data.copy()
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("User created successfully")
                return NotifyMeException.handle_success(message=ErrorCodeMessages[104], status_code=ErrorCodes["USER_CREATED_SUCCESSFULLY"])
            else:
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[103], exc_param=serializer.errors, status_code=ErrorCodes["VALIDATION_ERROR_WHILE_CREATING_USER"])
        except NotifyMeException as e:
            return Response(e.return_message, status = e.status_code)
        except SubscriptionPlan.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[105], status_code=ErrorCodes["INVALID_SUBSCRIPTION_ID_PROVIDED"])
        except IntegrityError:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[106], status_code=ErrorCodes["USER_ALREADY_EXISTS"]) 
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[103], exc_param=str(e), status_code=ErrorCodes["VALIDATION_ERROR_WHILE_CREATING_USER"])
            
        except Exception as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[102], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_FETCHING_USER"])
    
    def put(self, request):
        user_service = UserService()
        try:
            logger.info("Updating a user")
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=ErrorCodeMessages[107], status_code=ErrorCodes["USER_UPDATED_SUCCESSFULLY"])
            else:
                return NotifyMeException.handle_success(message=ErrorCodeMessages[140], status_code=ErrorCodes["VALIDATION_ERROR_WHILE_UPDATING_USER"]) 
        except NotifyMeException as e:
            return Response(e.return_message, status = e.status_code)
        except User.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[101], status_code=ErrorCodes["USER_NOT_FOUND"])
        except PermissionDenied:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[109], status_code=ErrorCodes["PERMISSION_DENIED_WHILE_UPDATING_USER_DATA"])
        except KeyError:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[110], status_code=ErrorCodes["MISSING_ID_WHILE_REQUESTING_FOR_UPDATE"])
        except Exception as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[111], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER"])
    
    def patch(self, request):
        user_service = UserService()
        try:
            logger.info("Patching a user")
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            user = user_service.get_user_by_id(data)
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(message=ErrorCodeMessages[107], status_code=ErrorCodes["USER_UPDATED_SUCCESSFULLY"])
                 
            else:
                logger.error(f"Validation error occurred while patching a user")
                return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[140], exc_param=serializer.errors, status=ErrorCodes["VALIDATION_ERROR_WHILE_UPDATING_USER"]) 
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except User.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[101], status_code=ErrorCodes["USER_NOT_FOUND"])
             
        except PermissionDenied:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[109], status_code=ErrorCodes["PERMISSION_DENIED_WHILE_UPDATING_USER_DATA"])
             
        except KeyError:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[110], status_code=ErrorCodes["MISSING_ID_WHILE_REQUESTING_FOR_UPDATE"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[111], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER"])
             
    
    def delete(self, request):
        user_service = UserService()
        try:
            logger.info("Deleting a user")
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            user = user_service.get_user_by_id(data)
            user.delete()
            return Response("User deleted successfully")
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except User.DoesNotExist:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[101], status_code=ErrorCodes["USER_NOT_FOUND"])
             
        except PermissionDenied:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[112],  status=ErrorCodes["PERMISSION_DENIED_WHILE_DELETING_USER_DATA"])
             
        except KeyError:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[115], status_code=ErrorCodes["MISSING_ID_IN_REQUEST_FOR_USER_DELETION"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(message=ErrorCodeMessages[114], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_OCCURED_WHILE_DELETING_USER"])
             
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView):
    def get(self, request):
        subscription_service = SubscriptionService()
        try:
            objects = subscription_service.get_all_subscriptions(request)
            if not objects:
                raise NotifyMeException(message = ErrorCodeMessages[151], status_code=ErrorCodes["SUBSCRIPTION_INSTANCES_NOT_FOUND"])
            serializer = SubscriptionSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages[116], exc_param=serializer.data, status_code=ErrorCodes["SUBSCRIPTION_DATA_FETCHED_SUCCESSFULLY"])
             
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except Subscription.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[117], status_code=ErrorCodes["SUBSCRIPTION_DATA_NOT_FOUND"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[118], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_DATA"])
             

    def post(self, request):
        try:
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages[119], status_code=ErrorCodes["SUBSCRIPTION_DATA_CREATED_SUCCESSFULLY"])
                 
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages[121], exc_param=serializer.errors, status_code=ErrorCodes["VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA"])
                 
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except IntegrityError:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[120], status_code=ErrorCodes["SUBSCRIPTION_DATA_ALREADY_EXISTS"])
            
        except ValidationError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[121], exc_param=str(e), status_code=ErrorCodes["VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA"])
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[122], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_DATA"])
             

    def put(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages[123], status_code=ErrorCodes["SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY"])
                 
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages[125], exc_param=serializer.errors, status_code=ErrorCodes["VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA"])
                 
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except Subscription.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[124], status_code=ErrorCodes["INVALID_SUBSCRIPTION_DATA_ID_PROVIDED"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[126], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA"])
             

    def patch(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            subscription = subscription_service.get_subscription_by_id(data)
            serializer = SubscriptionSerializer(subscription, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages[123], status_code=ErrorCodes["SUBSCRIPTION_DATA_UPDATED_SUCCESSFULLY"])
                 
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages[125], exc_param=serializer.errors, status_code=ErrorCodes["VALIDATION_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA"])
                 
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except Subscription.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[124], status_code=ErrorCodes["INVALID_SUBSCRIPTION_DATA_ID_PROVIDED"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[126], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_UPDATING_SUBSCRIPTION_DATA"])
             

    def delete(self, request):
        subscription_service = SubscriptionService()
        try:
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            subscription = subscription_service.get_subscription_by_id(data)
            subscription.delete()
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages[128], status_code=ErrorCodes["SUBSCRIPTION_DELETED_SUCCESSFULLY"])
             
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except Subscription.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[124], status_code=ErrorCodes["INVALID_SUBSCRIPTION_DATA_ID_PROVIDED"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[129], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_DELETING_SUBSCRIPTION_DATA"])
             

class SubscriptionPlanAPI(APIView):
    def get(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            logger.info("Fetching Subscription-Plan data")
            objects = subscription_plan_service.get_all_subscription_plans(request)
            if not objects:
                raise NotifyMeException(message = ErrorCodeMessages[152], status_code=ErrorCodes["SUBSCRIPTION_PLAN_INSTANCES_NOT_FOUND"])
            serializer = SubscriptionPlanSerializer(objects, many=True)
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages[130], exc_param=serializer.data, status_code=ErrorCodes["SUBSCRIPTION_PLAN_FETCHED_SUCCESSFULLY"])
             
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except SubscriptionPlan.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[131], status_code=ErrorCodes["SUBSCRIPTION_PLANS_NOT_FOUND"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[132], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_FETCHING_SUBSCRIPTION_PLANS"])
             

    def post(self, request):
        try:
            logger.info("Creating new Subscription-Plan")
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            serializer = SubscriptionPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return NotifyMeException.handle_success(
                    message=ErrorCodeMessages[133], status_code=ErrorCodes["SUBSCRIPTION_PLAN_CREATED_SUCCESSFULLY"])
                 
            else:
                return NotifyMeException.handle_api_exception(
                    message=ErrorCodeMessages[134], exc_param=serializer.errors, status_code=ErrorCodes["VALIDATION_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN"])
                 
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except IntegrityError as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[136], exc_param=str(e), status_code=ErrorCodes["INTEGRITY_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[135], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_WHILE_CREATING_SUBSCRIPTION_PLAN"])
             

    def delete(self, request):
        subscription_plan_service = SubscriptionPlanService()
        try:
            data = request.data
            if not data:
                raise NotifyMeException(message=ErrorCodeMessages[150], status_code=ErrorCodes["NO_DATA_IN_THE_REQUEST_GIVE_SOME_DATA"])
            subscriptionPlan = subscription_plan_service.get_subscription_plan_by_id(data)
            subscriptionPlan.delete()
            return NotifyMeException.handle_success(
                message=ErrorCodeMessages[137], status_code=ErrorCodes["SUBSCRIPTION_PLAN_DELETED_SUCCESSFULLY"])
             
        except NotifyMeException as e:
            return Response(e.return_message, status=e.status_code)
        except SubscriptionPlan.DoesNotExist:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[131], status_code=ErrorCodes["SUBSCRIPTION_PLANS_NOT_FOUND"])
             
        except PermissionDenied:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[139], status_code=ErrorCodes["PERMISSION_DENIED_WHILE_DELETING_SUBSCRIPTION_PLAN_DATA"])
             
        except KeyError:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[110], status_code=ErrorCodes["MISSING_ID_WHILE_REQUESTING_FOR_UPDATE"])
             
        except Exception as e:
            return NotifyMeException.handle_api_exception(
                message=ErrorCodeMessages[111], exc_param=str(e), status_code=ErrorCodes["UNEXPECTED_ERROR_OCCURED_WHILE_UPDATING_USER"])
             


    

