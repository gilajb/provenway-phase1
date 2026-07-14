from django_ratelimit.core import is_ratelimited
from rest_framework.exceptions import Throttled


def enforce_rate_limit(request, group: str, rate: str, method="POST", key: str = "user"):
    """Generic request-rate limiter for authenticated write endpoints that
    accept real abuse potential (upload flooding, spam-following) but
    live outside apps.authentication.

    Session 16 permission audit, item 5: apps.authentication.ratelimiting
    .enforce_auth_rate_limit already covers register/login/etc, but
    AvatarUploadView, UpdatePhotoUploadView, and FollowToggleView had no
    rate limiting at all. Rather than importing the auth app's helper
    into unrelated apps (or duplicating is_ratelimited() call sites),
    this is the same pattern generalised into core/.

    Deliberately keyed on `user` (not `ip`, the auth helper's key):
    these endpoints require authentication already, and IP-keying would
    let multiple accounts behind one NAT/office IP throttle each other
    while doing nothing to stop a single attacker with one account
    flooding a write endpoint from many rotating IPs — the threat here
    is one account hammering one endpoint, not one IP.
    """
    limited = is_ratelimited(
        request,
        group=group,
        key=key,
        rate=rate,
        method=method,
        increment=True,
    )
    if limited:
        raise Throttled(detail="Too many requests. Please try again shortly.")
