"""Admin pages of the accounts module."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from server.apps.accounts.models import User

admin.site.register(User, UserAdmin)
