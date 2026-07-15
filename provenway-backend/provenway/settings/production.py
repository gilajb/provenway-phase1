import os

from cryptography.hazmat.primitives import serialization

from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# RS256 needs real key material, not just a non-empty string — a blank or
# malformed value here would otherwise surface as a generic 500 on the
# first login attempt instead of at boot, where it's actually diagnosable.
_jwt_signing_key = os.environ.get("JWT_SIGNING_KEY", "")
_jwt_verifying_key = os.environ.get("JWT_VERIFYING_KEY", "")

try:
    serialization.load_pem_private_key(_jwt_signing_key.encode(), password=None)
except ValueError as exc:
    raise RuntimeError(
        "JWT_SIGNING_KEY is missing or not a valid PEM-encoded RSA private "
        "key. Generate one with `openssl genrsa -out jwt_private.pem 2048` "
        "and set the full PEM contents (including header/footer lines) as "
        "the JWT_SIGNING_KEY env var."
    ) from exc

try:
    serialization.load_pem_public_key(_jwt_verifying_key.encode())
except ValueError as exc:
    raise RuntimeError(
        "JWT_VERIFYING_KEY is missing or not a valid PEM-encoded RSA public "
        "key. Generate one with `openssl rsa -in jwt_private.pem -pubout "
        "-out jwt_public.pem` and set the full PEM contents as the "
        "JWT_VERIFYING_KEY env var."
    ) from exc

SIMPLE_JWT["ALGORITHM"] = "RS256"  # noqa: F405
SIMPLE_JWT["SIGNING_KEY"] = _jwt_signing_key  # noqa: F405
SIMPLE_JWT["VERIFYING_KEY"] = _jwt_verifying_key  # noqa: F405

LOGGING["root"]["level"] = "WARNING"  # noqa: F405
