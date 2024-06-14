from NotifyMe.models.notification import Notification
from NotifyMe.models.notificationType import NotificationType
from NotifyMe.models.subscription import Subscription
from NotifyMe.models.subscriptionPlan import SubscriptionPlan
from NotifyMe.models.user import User

class UserService:
  def get_user_data(self, request):
    try:
      users = User.objects.all()
      return users
    except Exception as e:
      print(f"error:{e}")
      return None
    
class SubscriptionService:
  def get_subscription_data(self, request):
    try:
      subscriptions = Subscription.objects.all()
      return subscriptions
    except Exception as e:
      print(f"error:{e}")
      return None
      
class NotificationService:
  def get_notification_data(self, request):
    try:
      notifications = Notification.objects.all()
      return notifications
    except Exception as e:
      print(f"error:{e}")

