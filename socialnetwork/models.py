from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# User class for built-in authentication module
from django.contrib.auth.models import User

# Signals to link User account with Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

# Data model for a todo-list item
class Post(models.Model):
    text = models.CharField(max_length=160)
    user = models.ForeignKey(User, default=None)
    datetime = models.DateTimeField(auto_now=True)
    parent = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return 'id=' + str(self.id) + ',text="' + self.text + '"'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=430, blank=True)
    dob = models.DateField(null=True, blank=True)
    following = models.ManyToManyField('self', blank=True,
    					related_name='followers', symmetrical=False)
    photo = models.FileField(upload_to="images", null=True, blank=True)
    photo_content_type = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return 'id=' + str(self.id) + ',user="' + self.user.username + '"'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()