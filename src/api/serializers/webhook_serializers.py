"""
WebHook Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from rest_framework import serializers


class InboundWebhookSerializer(serializers.Serializer):
    """
    This is the Inbound Webhook Post data Serializer.

    This is a formats the data coming out of the Db.
    """

    campaign_id = serializers.IntegerField()
    email = serializers.EmailField()
    time = serializers.DateTimeField()
    message = serializers.CharField()
    details = serializers.CharField()
