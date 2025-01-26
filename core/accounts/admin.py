from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User, Profile

from image_cropping import ImageCroppingMixin


class ProfileInline(ImageCroppingMixin, admin.StackedInline):
    model = Profile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                        'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    list_display = ['email', 'username', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ('email', 'username', 'profile__first_name', 'profile__last_name')
    ordering = ('email', 'username')
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('user__email', 'user__username', 'first_name', 'last_name')
    ordering = ('first_name', 'last_name')
    autocomplete_fields = ('user',)
