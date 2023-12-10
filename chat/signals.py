from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import ChatUser


@receiver(post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)
        instance.profile.save()
    else:
        instance.profile.save()
