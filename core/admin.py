from django.contrib import admin

from .models import Activation, Exchange


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    # list_display = ('id', 'phone', 'email', 'fb_id', 'vk_id', 'insta_id', 'code', 'used', 'avatar')
    list_display = ('id', 'phone', 'email', 'code', 'used', 'avatar',)

    list_filter = ('used',)
