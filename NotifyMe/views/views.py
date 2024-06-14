from django.shortcuts import render
from rest_framework.decorators import api_view
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


# ---------USER-API---------------- 
# DONOT CALL MODEL INSIDE VIEW---> ONLY CALL SERVICE AND SERIALIZER

class UserAPI(APIView, UserService):
  
  def get(self, request):
    try:
      objects = self.get_user_data(request)
      serializer = UserSerializer(objects, many=True)
      return Response(serializer.data)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def post(self, request):
    try:
      data = request.data.copy() # dictionary of key and value sent by client.
      # sid  = data['subscription_plan']
      # s = SubscriptionPlan.objects.get(id=sid)
      # data['subscription_plan']=s
      #-------------------------------------------------
      # user = User()
      # user.email_id = data['email_id']
      # user.first_name = data['first_name']
      # user.last_name = data['last_name']  
      # user.subscription_plan = data['subscription_plan']
      #--------------------------------------------------
      
      try:
        if 'subscription_plan' in data: # means if client have send any data for subscription field.
          SubscriptionPlan.objects.get(id=data['subscription_plan'])
          
      except SubscriptionPlan.DoesNotExist:
          return Response({"error": "Invalid subscription plan ID"}, status=status.HTTP_400_BAD_REQUEST)
      
           
      serializer = UserSerializer(data=data) # deserialization occured
      # user.save()
      if serializer.is_valid(): # if valid
        serializer.save() # create, serializer converts the data into 'User' instance and saves it to the database
        return Response({"message":"User added successfully"}, status=status.HTTP_201_CREATED)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  def put(self, request):
    try:
      data = request.data 
      serializer = UserSerializer(data=data)
      if serializer.is_valid():
        serializer.save()
        return Response({"message":"Updated Successfully"}, status=status.HTTP_202_ACCEPTED)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  def patch(self, request):
    try:
      data = request.data  
      obj = User.objects.get(id=data['id'])
      serializer = UserSerializer(obj, data=data, partial=True)
      if serializer.is_valid():
        serializer.save()
        return Response({"message":"Patched Successfully"}, status=status.HTTP_202_ACCEPTED)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
      return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  def delete(self, request):
    try:
      data = request.data 
      obj = User.objects.get(id=data['id'])
      obj.delete()
      return Response({"message":"Deleted Successfully"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
      return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    
 
 
#----------SUBSCRIPTION-API----------------      
    
class SubscriptionAPI(APIView, SubscriptionService):
  
  def get(self, request):
    try:
      objects = self.get_subscription_data(request)
      serializer = SubscriptionSerializer(objects, many=True)
      return Response(serializer.data)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # provide the data as GET method
  
  def post(self, request):
    data = request.data 
    serializer = SubscriptionSerializer(data=data)
    if serializer.is_valid():
      serializer.save()
      
      return Response({"message":"User added successfully"}, status = status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def put(self, request):
    data = request.data 
    # obj = Subscription.objects.get(id=data['id'])
    serializer = SubscriptionSerializer(data=data)
    if serializer.is_valid():
      serializer.save()
      return Response({"message":"Updated Successfully"}, status=status.HTTP_202_ACCEPTED) 
    
  def patch(self, request):
    data = request.data 
    obj = Subscription.objects.get(id=data['id'])
    serializer = SubscriptionSerializer(obj, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response({"message":"Patched Successfully"}, status=status.HTTP_202_ACCEPTED)
    
  def delete(self, request):
    try:
      data = request.data 
      obj = Subscription.objects.get(id=data['id'])
      obj.delete()
      return Response({"message":"Deleted Successfully"}, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
      return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      print(f"Error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

#---------------NOTIFICATION-API---------------------

class NotificationAPI(APIView, NotificationService):
  
  def get(self, request):
    objects = self.get_notification_data(request)
    serializer = NotificationSerializer(objects, many=True)
    return Response(serializer.data) # provide the data as GET method
  
  def post(self, request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User added successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def put(self, request):
    data = request.data 
    # obj = Notification.objects.get(id=data['id'])
    serializer = NotificationSerializer(data=data)
    if serializer.is_valid():
      serializer.save()
      return Response({"message":"Updated Successfully"}, status=status.HTTP_202_ACCEPTED) 
    
  def patch(self, request):
    data = request.data 
    obj = Notification.objects.get(id=data['id'])
    serializer = NotificationSerializer(obj, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response({"message":"Patched Successfully"}, status=status.HTTP_202_ACCEPTED)
    
  def delete(self, request):
    data = request.data 
    obj = Notification.objects.get(id=data['id'])
    obj.delete()
    return Response({"message":"Deleted Successfully"}, status=status.HTTP_200_OK)
  
  

# class UserAPI(APIView):
  
#   def get(self, request):
#     objects = User.objects.all()
#     serializer = UserSerializer(objects, many=True)
#     return Response(serializer.data) # provide the data as GET method
  
#   def post(self, request):
#     data = request.data 
#     serializer = UserSerializer(data=data)
#     if serializer.is_valid():
#       serializer.save()
      
#       return Response({"message":"User added successfully"}, status = status.HTTP_201_CREATED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
#   def put(self, request):
#     data = request.data 
#     # obj = User.objects.get(id=data['id'])
#     serializer = UserSerializer(data=data)
#     if serializer.is_valid():
#       serializer.save()
#       return Response({"message":"Updated Successfully"}, status=status.HTTP_202_ACCEPTED) 
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#   def patch(self, request):
#     data = request.data  
#     obj = User.objects.get(id=data['id'])
#     serializer = UserSerializer(obj, data=data, partial=True)
#     if serializer.is_valid():
#       serializer.save()
#       return Response({"message":"Patched Successfully"}, status=status.HTTP_202_ACCEPTED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#   def delete(self, request):
#     data = request.data 
#     obj = User.objects.get(id=data['id'])
#     obj.delete()
#     return Response({"message":"Deleted"})
  
  

       