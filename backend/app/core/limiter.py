from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings


def get_client_ip(request):
    # Behind Nginx/Render the socket address is the proxy, not the user
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
        if client_ip:
            return client_ip
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_ip,
    enabled=settings.RATE_LIMIT_ENABLED,
)
