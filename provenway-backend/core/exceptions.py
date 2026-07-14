from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

PROBLEM_BASE_URI = "https://provenway.com/problems/"

_TITLES = {
    400: "Validation Error",
    401: "Authentication Required",
    403: "Permission Denied",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
}

_SLUGS = {
    400: "validation-error",
    401: "authentication-required",
    403: "permission-denied",
    404: "not-found",
    405: "method-not-allowed",
    409: "conflict",
    422: "unprocessable-entity",
    429: "rate-limited",
    500: "internal-error",
}


def _problem_response(status_code, detail, errors=None):
    slug = _SLUGS.get(status_code, "error")
    title = _TITLES.get(status_code, "Error")
    body = {
        "type": f"{PROBLEM_BASE_URI}{slug}",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if errors:
        body["errors"] = errors
    return Response(body, status=status_code, content_type="application/problem+json")


def problem_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()

    response = drf_exception_handler(exc, context)

    if response is None:
        return _problem_response(500, "An unexpected error occurred.")

    detail = response.data
    errors = None

    if isinstance(detail, dict):
        non_field = detail.pop("non_field_errors", None) or detail.pop("detail", None)
        if detail:
            errors = detail
        human_detail = non_field if non_field else "One or more fields failed validation."
        if isinstance(human_detail, list):
            human_detail = " ".join(str(m) for m in human_detail)
    elif isinstance(detail, list):
        errors = {"non_field_errors": detail}
        human_detail = " ".join(str(m) for m in detail)
    else:
        human_detail = str(detail)

    return _problem_response(response.status_code, human_detail, errors)
