from django.contrib import admin
from .models import ChatQuery


@admin.register(ChatQuery)
class ChatQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "symbol", "intent", "recommendation", "confidence", "created_at")
    list_filter = ("intent", "recommendation", "created_at")
    search_fields = ("query", "symbol", "user__username")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
