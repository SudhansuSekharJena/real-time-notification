from NotifyMe.views.views import UserAPI, SubscriptionAPI, MaintenanceAlertAPI
from django.contrib import admin
from django.urls import path

# url patterns are list of urls
urlpatterns = [
  path("user", UserAPI.as_view()),
  path("subscription", SubscriptionAPI.as_view()),
  path("maintenance", MaintenanceAlertAPI.as_view())
]