import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from NotifyMe.routing import websocket_urlpatterns
from channels.sessions import SessionMiddlewareStack

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NotificationModule.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
})