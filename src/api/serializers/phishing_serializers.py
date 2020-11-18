"""Phish Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class SubscriptionTargetSerializer(serializers.Serializer):
    """SubscriptionTargetSerializer."""

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    position = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class PhishingResultsSerializer(serializers.Serializer):
    """PhishingResultsSerializer."""

    sent = serializers.IntegerField(default=0)
    opened = serializers.IntegerField(default=0)
    clicked = serializers.IntegerField(default=0)
    submitted = serializers.IntegerField(default=0)
    reported = serializers.IntegerField(default=0)
