import base64
import binascii
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


def _load_b64_pem_env(var_name):
    # Multi-line PEM text pasted through a dashboard's env var UI is prone
    # to mangled whitespace/line breaks, which silently corrupts the key.
    # Env vars hold the *base64* of the PEM instead — a single token with
    # no internal structure to corrupt. b64decode() with validate=False
    # (the default) also discards any stray whitespace that sneaks into
    # the base64 itself, so the decode step doesn't reintroduce the
    # problem it exists to avoid.
    raw = os.environ.get(var_name, "")
    try:
        return base64.b64decode(raw).decode()
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise RuntimeError(
            f"{var_name} is not valid base64. Set it to the base64-encoded "
            f"PEM key (e.g. `openssl base64 -A -in jwt_private.pem`), not "
            f"the raw PEM text."
        ) from exc


_jwt_signing_key = _load_b64_pem_env("JWT_SIGNING_KEY")
_jwt_verifying_key = _load_b64_pem_env("JWT_VERIFYING_KEY")

try:
    serialization.load_pem_private_key(_jwt_signing_key.encode(), password=None)
except ValueError as exc:
    raise RuntimeError(
        "JWT_SIGNING_KEY decoded to something that isn't a valid PEM RSA "
        "private key. Generate one with `openssl genrsa -out "
        "jwt_private.pem 2048`, then base64-encode it with `openssl "
        "base64 -A -in jwt_private.pem` and set that as JWT_SIGNING_KEY."
    ) from exc

try:
    serialization.load_pem_public_key(_jwt_verifying_key.encode())
except ValueError as exc:
    raise RuntimeError(
        "JWT_VERIFYING_KEY decoded to something that isn't a valid PEM RSA "
        "public key. Generate one with `openssl rsa -in jwt_private.pem "
        "-pubout -out jwt_public.pem`, then base64-encode it with "
        "`openssl base64 -A -in jwt_public.pem` and set that as "
        "JWT_VERIFYING_KEY."
    ) from exc

SIMPLE_JWT["ALGORITHM"] = "RS256"  # noqa: F405
SIMPLE_JWT["SIGNING_KEY"] = _jwt_signing_key  # noqa: F405
SIMPLE_JWT["VERIFYING_KEY"] = _jwt_verifying_key  # noqa: F405

LOGGING["root"]["level"] = "WARNING"  # noqa: F405
