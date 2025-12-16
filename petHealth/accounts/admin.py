from django.contrib import admin
from .models import UserProfile

# Hiển thị UserProfile trong admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "fullname", "birthday", "phone")
    search_fields = ("user__username", "fullname", "phone")
    list_filter = ("birthday",)
