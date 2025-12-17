from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullname = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Tự động tạo profile khi user mới được tạo
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)

