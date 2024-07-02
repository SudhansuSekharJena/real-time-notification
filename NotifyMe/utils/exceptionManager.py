
# proper response format-> { status code, a message, an actual data, status code, 
import logging
from rest_framework.response import Response
import json

logger = logging.getLogger(__name__)


class NotifyMeException(Exception):  # CUSTOM EXCEPTION
    def __init__(self, message, exc_param, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

        self.return_message = {
            "message": self.message,
            "status": self.status_code
        }

    def __str__(self):
        return str(self.return_message)

    @staticmethod
    def handle_exception(message, exc_param=None, status_code=500):
        """
        For normal error handling in service and serializer.
        """
        logger.error(f"Exception: {message} (status: {status_code})")
        response_data = {
            "message": message,
            "exception_parameter": exc_param,
            "status": status_code
        }
        return Response(response_data)

    @staticmethod
    def handle_api_exception(message, exc_param=None, status_code=500):
        """ 
        To handle exception handling in views
        """
        logger.error(f"API Exception: {message} (status: {status_code})")
        response_data = {
            "message": message,
            "exception_parameter": exc_param,
            "status": status_code
        }
        return Response(response_data)

    @staticmethod
    def handle_success(message, exc_param=None, status_code=200):
        """
        For sending success message...
        """
        logger.info(f"Success: {message} (status: {status_code})")
        response_data = {
            "message": message,
            "exception_parameter": exc_param,
            "status": status_code
        }
        return Response(response_data)

# class NotifyMeException:
  
#   @staticmethod
#   def handle_success(message, exc_param=None, status_code=200):
#     """
#     For sending success message...
#     """
#     logger.info(f"Success: {message} (status: {status_code})") 
    
#     response_data = {
#       "message":message,
#       "exception_parameter":exc_param,
#       "status":status_code
#     }
#     return response_data

# class NotifyMeException:
    
#     @staticmethod
#     def handle_exception(message, exc_param=None, status_code=500):
#       """
#       for normal error handling in service and serializer.
    
#       """
#       logger.error(f"Exception: {message} (status: {status_code})")
#       response_data = {
#         "message":message,
#         "exception_parameter":exc_param,
#         "status":status_code
#       }
#       return response_data
#       # raise NotifyMeException(message, exc_param, status_code)
    
    
#     @staticmethod
#     def handle_api_exception(message, exc_param=None, status_code=500):
      
#       """ 
#       To handle exception handling in views
    
#       """
#       logger.error(f"API Exception: {message} (status: {status_code})")
#       response_data = {
#         "message":message,
#         "exception_parameter":exc_param,
#         "status":status_code
#       }
#       return response_data
#       # raise NotifyMeException(message, exc_param, status_code)