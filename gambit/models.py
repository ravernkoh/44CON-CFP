from uuid import uuid4
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    country = models.CharField(max_length=48)
    affiliation = models.CharField(max_length=32)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    submitted_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    abstract = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/submissions/%Y/%m/%d/', blank=True)

    def __str__(self):
        return '{0!s}'.format(self.title)
