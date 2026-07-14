import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from core.models import TimestampedModel


class SubscriptionTier(models.TextChoices):
    FREE = "free", "Free"
    PROFESSIONAL = "professional", "Professional"
    PRO_PLUS = "pro_plus", "Pro+"
    FIRM = "firm", "Firm"


class Discipline(models.TextChoices):
    ARCHITECT = "architect", "Architect"
    CIVIL_ENGINEER = "civil_engineer", "Civil Engineer"
    STRUCTURAL_ENGINEER = "structural_engineer", "Structural Engineer"
    QS = "qs", "Quantity Surveyor"
    CONTRACTOR = "contractor", "Contractor"
    SITE_SUPERVISOR = "site_supervisor", "Site Supervisor"
    PROJECT_MANAGER = "project_manager", "Project Manager"
    INTERIOR_DESIGNER = "interior_designer", "Interior Designer"
    MEP_ENGINEER = "mep_engineer", "MEP Engineer"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # NOTE: AbstractBaseUser provides `password` (bcrypt hash via Django's
    # password hashers) — this is the password_hash column from the schema.

    display_name = models.CharField(max_length=100)
    headline = models.CharField(max_length=200, null=True, blank=True)
    # bio / location_text / location_lat / location_lng / avatar_url used to
    # live here, but they duplicated the same data on apps.profiles.Profile
    # (one-to-one with User). Profile is now the single source of truth for
    # all of that — see apps/profiles/models.py. Existing values were
    # migrated over in authentication/migrations/0003 before these columns
    # were dropped in 0004.
    is_verified = models.BooleanField(default=False)
    # Distinct from is_verified (admin-approved professional credential
    # badge, FR-PROF-04) and is_active (account ban/deactivation). Gates
    # login — see LoginView / VerifyEmailView.
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    subscription_tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.FREE,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["subscription_tier", "is_verified"]),
        ]

    def __str__(self):
        return self.email


# UserDiscipline (a `user` + `discipline` join table) used to live here.
# It duplicated exactly what apps.profiles.Profile.disciplines (a Postgres
# ArrayField over the same Discipline taxonomy) already models, with no
# distinguishing feature of its own (no ordering, no "primary discipline"
# flag) — so it was retired the same way as the other duplicated fields.
# Existing rows were migrated into Profile.disciplines in
# authentication/migrations/0005 before the table was dropped in 0006.


class AuthToken(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    token_hash = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_tokens"
        indexes = [
            models.Index(fields=["user", "revoked_at"]),
        ]

    @property
    def is_revoked(self):
        return self.revoked_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def revoke(self):
        self.revoked_at = timezone.now()
        self.save(update_fields=["revoked_at"])

    def __str__(self):
        return f"AuthToken({self.user.email})"


class EmailVerificationToken(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token_hash = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "email_verification_tokens"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    def __str__(self):
        return f"EmailVerificationToken({self.user.email})"


class PasswordResetToken(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "password_reset_tokens"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    def __str__(self):
        return f"PasswordResetToken({self.user.email})"


class AuthAuditLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILED = "login_failed", "Login Failed"
        LOGOUT = "logout", "Logout"
        REGISTER = "register", "Register"
        EMAIL_VERIFIED = "email_verified", "Email Verified"
        PASSWORD_CHANGED = "password_changed", "Password Changed"
        PASSWORD_RESET_REQUESTED = "password_reset_requested", "Password Reset Requested"
        TOKEN_REFRESHED = "token_refreshed", "Token Refreshed"
        TOKEN_REVOKED = "token_revoked", "Token Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_log_entries",
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "auth_audit_log"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} — {self.user_id} @ {self.created_at}"
