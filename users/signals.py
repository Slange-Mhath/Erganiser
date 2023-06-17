from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Member


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # How can I create a different PK for the profile if created?
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs):
    # How can I create a different PK for the member if created?
    if created:
        Member.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_member(sender, instance, **kwargs):
    instance.profile.save()
