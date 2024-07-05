
# proper response format-> { status code, a message, an actual data, status code, 
import logging
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class NotifyMeException(Exception):  # CUSTOM EXCEPTION
    def __init__(self, message, status_code, e):
        self.message = message
        self.e = e
        self.status_code = status_code
        super().__init__(self.message)

        self.return_message = {
            "message": self.message,
            "e": self.e,
            "status": self.status_code
        }
        
        logger.error(self.return_message)

    def __str__(self):
        return self.return_message

    @staticmethod
    def handle_api_exception(message, status_code, e=None):
        """ 
        To handle exception handling in views
        """
        logger.error(f"MESSAGE: {message}, STATUS: {status_code}, ERROR: {e}")
        
        response_data = {
            "message": message,
            "status": status_code
        }  
        return Response(response_data)
    
    def handle_exception(mesage, status_code):
        """
        To handle exception handling in serializers and servies
        """
        
        response_data = {
            "message": mesage,
            "status": status_code
        }
        
        return Response(response_data)

    @staticmethod
    def handle_success(message, status_code, data=None):
        """
        For sending success message...
        """
        response_data = {
            "message": message,
            "status": status_code
        }
        
        if data:
            response_data["data"] = data
            
        logger.info(response_data)
        return Response(response_data)

