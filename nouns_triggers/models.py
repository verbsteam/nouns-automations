import uuid
from django.db import models


AUCTION_SETTLED_EVENT = 'auction_settled'


class RegisteredWebhook(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    webhook_url = models.CharField(max_length=500)
    event = models.CharField(max_length=100)
    hours_before = models.IntegerField()
    minutes_before = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class LastSeenAuction(models.Model):
    noun_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
