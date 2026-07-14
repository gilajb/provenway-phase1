from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile
from .search import update_search_vector


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Auto-create a blank Profile the moment a User row is created.

    Registration must never require a separate "create your profile" step —
    get_or_create is used (rather than a plain create) so this stays safe
    to call even if a Profile already exists (e.g. re-saves, admin edits,
    fixtures) instead of raising an IntegrityError on the one-to-one.
    """
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def refresh_search_vector_on_user_save(sender, instance, created, **kwargs):
    """Directory search (§5.2 GET /users/) indexes User.display_name and
    User.headline alongside Profile's own fields. When those change on an
    existing user, the linked profile's search_vector needs to be
    recomputed too — the create_profile_for_new_user branch above already
    covers brand-new users (Profile.save() there fires
    refresh_search_vector_on_profile_save below).
    """
    if created:
        return
    profile = Profile.objects.filter(user_id=instance.pk).only("id").first()
    if profile is not None:
        update_search_vector(profile.id)


@receiver(post_save, sender=Profile)
def refresh_search_vector_on_profile_save(sender, instance, **kwargs):
    """Keep search_vector current whenever a Profile itself is created or
    edited (bio, disciplines, firm_name, location, avatar, etc).

    Safe against recursion: update_search_vector uses a queryset .update()
    rather than instance.save(), and .update() doesn't re-fire post_save.
    """
    update_search_vector(instance.pk)
