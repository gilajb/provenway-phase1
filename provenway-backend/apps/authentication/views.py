from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import generate_token, get_client_ip, hash_token

from .models import AuthAuditLog, AuthToken, EmailVerificationToken, PasswordResetToken, User
from .ratelimiting import enforce_auth_rate_limit
from .serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    TokenRefreshRequestSerializer,
    VerifyEmailSerializer,
)
from .tasks import send_password_reset_email_task, send_verification_email_task

EMAIL_VERIFICATION_TTL = timedelta(hours=24)
PASSWORD_RESET_TTL = timedelta(hours=1)


def _log_event(request, user, event_type, metadata=None):
    AuthAuditLog.objects.create(
        user=user,
        event_type=event_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        metadata=metadata,
    )


def _issue_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    raw_refresh = str(refresh)
    AuthToken.objects.create(
        user=user,
        token_hash=hash_token(raw_refresh),
        expires_at=timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )
    return {"access": str(refresh.access_token), "refresh": raw_refresh}


def _build_frontend_url(path_template, token):
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    return f"{base}{path_template.format(token=token)}"


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_register")
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        raw_token = generate_token()
        EmailVerificationToken.objects.create(
            user=user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() + EMAIL_VERIFICATION_TTL,
        )
        verification_url = _build_frontend_url("/verify-email?token={token}", raw_token)
        send_verification_email_task.delay(
            str(user.id), user.display_name, user.email, verification_url
        )
        _log_event(request, user, AuthAuditLog.EventType.REGISTER)
        return Response(
            {"detail": "Registration successful. Check your email to verify your account.",
             "user": CurrentUserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_verify_email")
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_hash = hash_token(serializer.validated_data["token"])

        try:
            token_obj = EmailVerificationToken.objects.select_related("user").get(token_hash=token_hash)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or unknown verification token."}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_used:
            return Response({"detail": "This verification link has already been used."}, status=status.HTTP_400_BAD_REQUEST)
        if token_obj.is_expired:
            return Response({"detail": "This verification link has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        token_obj.mark_used()
        user = token_obj.user
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        _log_event(request, user, AuthAuditLog.EventType.EMAIL_VERIFIED)
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_login")
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            _log_event(request, None, AuthAuditLog.EventType.LOGIN_FAILED,
                       metadata={"email": request.data.get("email", "")})
            raise ValidationError(serializer.errors)

        user = serializer.validated_data["user"]

        tokens = _issue_tokens_for_user(user)
        _log_event(request, user, AuthAuditLog.EventType.LOGIN_SUCCESS)
        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": CurrentUserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_refresh = serializer.validated_data["refresh"]

        try:
            RefreshToken(raw_refresh).blacklist()
        except TokenError:
            pass

        AuthToken.objects.filter(
            user=request.user, token_hash=hash_token(raw_refresh), revoked_at__isnull=True
        ).update(revoked_at=timezone.now())

        _log_event(request, request.user, AuthAuditLog.EventType.LOGOUT)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_token_refresh", rate="30/m")
        serializer = TokenRefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_refresh = serializer.validated_data["refresh"]

        try:
            old_token = RefreshToken(raw_refresh)
            user = User.objects.get(id=old_token["user_id"])
        except (TokenError, User.DoesNotExist):
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        old_hash = hash_token(raw_refresh)
        old_record = AuthToken.objects.filter(token_hash=old_hash).first()
        if old_record and old_record.is_revoked:
            AuthToken.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())
            return Response({"detail": "This session has been revoked. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            old_token.blacklist()
        except TokenError:
            pass
        if old_record:
            old_record.revoke()

        tokens = _issue_tokens_for_user(user)
        _log_event(request, user, AuthAuditLog.EventType.TOKEN_REFRESHED)
        return Response({"access": tokens["access"], "refresh": tokens["refresh"]})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_password_reset_request")
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower().strip()

        user = User.objects.filter(email=email, is_active=True).first()
        if user:
            raw_token = generate_token()
            PasswordResetToken.objects.create(
                user=user,
                token_hash=hash_token(raw_token),
                expires_at=timezone.now() + PASSWORD_RESET_TTL,
            )
            reset_url = _build_frontend_url("/reset-password?token={token}", raw_token)
            send_password_reset_email_task.delay(str(user.id), user.display_name, user.email, reset_url)
            _log_event(request, user, AuthAuditLog.EventType.PASSWORD_RESET_REQUESTED)

        return Response(
            {"detail": "If an account exists for that email, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_auth_rate_limit(request, group="auth_password_reset_confirm")
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        token_hash = hash_token(raw_token)

        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(token_hash=token_hash)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid or unknown reset token."}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_used:
            return Response({"detail": "This reset link has already been used."}, status=status.HTTP_400_BAD_REQUEST)
        if token_obj.is_expired:
            return Response({"detail": "This reset link has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.set_password(new_password)
        user.save(update_fields=["password"])
        token_obj.mark_used()
        AuthToken.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())
        _log_event(request, user, AuthAuditLog.EventType.PASSWORD_CHANGED)
        return Response({"detail": "Password reset successfully. Please log in again."}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)
