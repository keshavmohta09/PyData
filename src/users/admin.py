"""
This file contains all the admins for users module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from users.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")
