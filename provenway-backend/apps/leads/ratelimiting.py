from django_ratelimit.core import is_ratelimited
from rest_framework.exceptions import Throttled


def enforce_leads_rate_limit(request, group: str, rate: str = "5/m"):
    """IP-keyed, same shape as apps.authentication.ratelimiting.
    enforce_auth_rate_limit — this is a public, unauthenticated write with
    no existing volume expectation, so the default is deliberately tight.
    """
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
