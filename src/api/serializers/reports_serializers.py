"""Reports Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class StatLevelSerializer(serializers.Serializer):
    """StatLevelSerializer."""

    level = serializers.CharField()
    level_number = serializers.IntegerField()
    sent = serializers.IntegerField(required=False)
    opened = serializers.IntegerField(required=False)
    clicked = serializers.IntegerField(required=False)


class ReportsGetSerializer(serializers.Serializer):
    """ReportsGetSerializer."""

    customer_name = serializers.CharField()
    templates = serializers.DictField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    levels = StatLevelSerializer(many=True)
    sent = serializers.IntegerField()
    target_count = serializers.IntegerField()
    metrics = serializers.DictField()
    recommendations = serializers.ListField()


class EmailReportsGetSerializer(serializers.Serializer):
    """EmailReportsGetSerializer."""

    subscription_uuid = serializers.CharField()
