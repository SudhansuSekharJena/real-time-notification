
# proper response format-> { status code, a message, an actual data, status code, 
import logging

logger = logging.getLogger(__name__)



class CustomException(Exception): # CUSTOM EXCEPTION
  def __init__(self, message, data, status_code):
    self.message = message
    self.data = str(data)
    self.status_code = status_code
    super.__init__(self.message)
    
    self.return_message = {
      "message":self.message,
      "data":str(self.data),
      "status":self.status_code
    }
      
    
    def __str__(self):
      return self.return_message
    
  
class SuccessHandler:
  
  @staticmethod
  def handle_success(message, data=None, status_code=200):
    """
    For sending success message...
    """
    logger.info(f"Success: {message} (status: {status_code})") 
    
    response_data = {
      "message":message,
      "data":data,
      "status":status_code
    }
    return response_data
    
    
class ExceptionHandler:
    
    @staticmethod
    def handle_exception(message, data=None, status_code=500):
      """
      for normal error handling in service and serializer.
    
      """
      logger.error(f"Exception: {message} (status: {status_code})")
      raise CustomException(message, data, status_code)
    
    
    @staticmethod
    def handle_api_exception(message, data=None, status_code=500):
      
      """ 
      To handle exception handling in views
    
      """
      logger.error(f"API Exception: {message} (status: {status_code})")
      raise CustomException(message, data, status_code)
  
  
  
    