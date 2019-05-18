from django.contrib import admin

from .models import Activation, Exchange, TokenLog


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    # list_display = ('id', 'phone', 'email', 'fb_id', 'vk_id', 'insta_id', 'code', 'used', 'avatar')
    list_display = ('id', 'phone', 'email', 'code', 'used', 'avatar',)

    list_filter = ('used',)


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'sending', 'receiving', 'data_and_time', 'timestamp',)

    list_filter = ('data_and_time',)

    ordering = ('-timestamp',)


@admin.register(TokenLog)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'user', 'active',)


