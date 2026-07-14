from django_ratelimit.core import is_ratelimited
from rest_framework.exceptions import Throttled


def enforce_auth_rate_limit(request, group: str, rate: str = "10/m"):
    limited = is_ratelimited(
        request,
        group=group,
        key="ip",
        rate=rate,
        method="POST",
        increment=True,
    )
    if limited:
        raise Throttled(detail="Too many requests. Please try again shortly.")
