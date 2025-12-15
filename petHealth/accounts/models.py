from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullname = models.CharField("Họ và tên", max_length=100, blank=True)
    birthday = models.DateField("Ngày sinh", null=True, blank=True)
    phone = models.CharField("Số điện thoại", max_length=15, blank=True)

    def __str__(self):
        return self.user.username


# Tự động tạo profile khi user mới được tạo
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
