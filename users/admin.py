from django.contrib import admin
from users.models import User, UserSignupCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name']


@admin.register(UserSignupCode)
class UserSignupCodeAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'created']
