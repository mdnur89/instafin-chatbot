from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ChatPlatform, PlatformCredential, MessageTemplate

@admin.register(ChatPlatform)
class ChatPlatformAdmin(ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    compressed_fields = []

@admin.register(PlatformCredential)
class PlatformCredentialAdmin(ModelAdmin):
    list_display = ('platform', 'created_at')
    list_filter = ('platform',)
    exclude = ('api_key', 'api_secret')
    compressed_fields = []

@admin.register(MessageTemplate)
class MessageTemplateAdmin(ModelAdmin):
    list_display = ('name', 'platform', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('name', 'content')
    compressed_fields = []
