import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chatbot import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "instafin_backend.settings")

print("ASGI Configuration Loading")
print(f"WebSocket patterns: {routing.websocket_urlpatterns}")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

print("ASGI Configuration Loaded with WebSocket routes")
