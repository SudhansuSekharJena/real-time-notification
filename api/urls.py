from NotifyMe.views.views import UserAPI, SubscriptionAPI, NotifySubscriptionEndAPI, MaintenanceNotificationAPI
from django.contrib import admin
from django.urls import path

# url patterns are list of urls
urlpatterns = [
  path("user", UserAPI.as_view()),
  path("subscription", SubscriptionAPI.as_view()),
  path("notify-subscription-end", NotifySubscriptionEndAPI.as_view()),
  path("maintenance-alert", MaintenanceNotificationAPI.as_view())
]