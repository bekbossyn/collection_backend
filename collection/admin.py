from django.contrib import admin

# Register your models here.
from .models import Collection, Word


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user',)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'collection', 'user', 'users')
