
# proper response format-> { status code, a message, an actual data, status code, 
import logging
from rest_framework.response import Response
import json
from rest_framework import status

logger = logging.getLogger(__name__)


class NotifyMeException(Exception):  # CUSTOM EXCEPTION
    def __init__(self, message, exc_param, status_code):
        self.message = message
        self.exc_param = exc_param
        self.status_code = status_code
        super().__init__(self.message)

        self.return_message = {
            "message": self.message,
            "exc_param": self.exc_param,
            "status": self.status_code
        }
        
        logger.error(self.return_message)

    def __str__(self):
        return json.dumps(self.return_message)

    @staticmethod
    def handle_exception(message, status_code=500,exc_param=None):
        """
        For normal error handling in service and serializer.
        """
        response_data = {
            "message": message,
            "status": status_code
        }
        if exc_param:
            response_data["exc_param"] = exc_param
            
        logger.error(f"RESPONSE_DATA: {response_data}")
        return Response(response_data)

    @staticmethod
    def handle_api_exception(message, status_code=500,exc_param=None):
        """ 
        To handle exception handling in views
        """
        logger.error(f"API Exception: {message} (status: {status_code})")
        response_data = {
            "message": message,
            "status": status_code
        }
        if exc_param:
            response_data["exc_param"] = exc_param
            
        logger.error(f"RESPONSE_DATA: {response_data}")
        return Response(response_data)

    @staticmethod
    def handle_success(message, status_code=200, exc_param=None):
        """
        For sending success message...
        """
        logger.info(f"Success: {message} (status: {status_code})")
        response_data = {
            "message": message,
            "status": status_code
        }
        if exc_param:
            response_data["exc_param"] = exc_param
            
        logger.info(f"RESPONSE_DATA: {response_data}")
        return Response(response_data)

