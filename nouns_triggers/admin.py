from django.contrib import admin

from nouns_triggers.models import RegisteredWebhook, LastSeenAuction


class RegisteredWebhookAdmin(admin.ModelAdmin):
    list_display = ['id', 'webhook_url', 'uuid', 'hours_before', 'minutes_before', 'created_at']


class LastSeenAuctionAdmin(admin.ModelAdmin):
    list_display = ['noun_id', 'updated_at', 'created_at']


admin.site.register(RegisteredWebhook, RegisteredWebhookAdmin)
admin.site.register(LastSeenAuction, LastSeenAuctionAdmin)
