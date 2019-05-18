from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import MainUserChangeForm, MainUserCreationForm

# from .models import MainUser, GameSetting
from .models import MainUser, TokenLog


@admin.register(MainUser)
class MainUserAdmin(UserAdmin):
    form = MainUserChangeForm
    add_form = MainUserCreationForm

    list_display = (
        'id',
        'phone',
        'email',
        # 'fb_id',
        # 'insta_id',
        # 'vk_id',
        'name',
        'last_login',
        # 'country',
        'is_active',
        'is_admin',
        'timestamp',
        'player_ids',
    )

    list_filter = ('is_admin', 'is_active',)

    search_fields = ('phone', 'email', 'name',)

    ordering = ('-timestamp',)

    fieldsets = (
        (None, {'fields': (
                    'phone',
                    'email',
                    'name',
                    'avatar',
            )}),
        ('Password', {'fields': ('password', )}),  # we can change password in admin-site
        ('Permissions', {'fields': ('is_active', 'is_admin')}),
        ('Info', {'fields': ('language', 'player_ids',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('phone', 'name', 'password1', 'password2',)}),
        ('Permissions', {'fields': ('is_active', 'is_admin', )}),
    )


@admin.register(TokenLog)
class TokenLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'user', 'active',)

# @admin.register(GameSetting)
# class ActivationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'owner', 'on_save', 'on_full', 'ace_allowed', 'on_eggs', 'timestamp',)
#
#     list_filter = ('on_save', 'on_full', 'ace_allowed', 'on_eggs',)

