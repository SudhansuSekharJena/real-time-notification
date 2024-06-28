from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationManager:
  
  def maintenance_alert(self, group_name, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
      group_name,
      {
        "type":"send_maintenance_alert",
        "message":message,
        "notification_type":"maintenance_alert"
      }
    )
    
class CustomException(Exception):
  
  @staticmethod
  def handle_exception(error): 
    """
    for normal error handling in service and serializer.
    
    """
    response_data = {
      "status":"error",
      "message":str(error)
    }
    
    return response_data
    
    # response_data = {
    #   "success":False,
    # }
    # if message:
    #   response_data["message"] = message
      
    # if data is not None:
    #   response_data["data"] = data
      
    # return response_data
    
    
    
    
    
    pass
  
  
  @staticmethod
  def handle_api_exception(message=None, data=None): 
    
    """ 
    To handle exception handling in views
    
    """
    response_data = {
      "success":False,
    }
    
    if message:
      response_data["message"] = message
    if data is not None:
      response_data["data"] = data
      
    return response_data
  
  
  @staticmethod
  def handle_success(message=None, data=None): 
    """ 
    for sending success message related message
    """
    response_data = {
      "success":True,
    }
    
    if message:
      response_data["message"]=message
    if data is not None:
      response_data["data"] = data
      
    return response_data
    
    
    