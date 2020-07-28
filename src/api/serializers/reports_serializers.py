"""
Reports Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from rest_framework import serializers


class StatLevelSerializer(serializers.Serializer):
    level = serializers.CharField()
    level_number = serializers.IntegerField()
    sent = serializers.IntegerField(required=False)
    opened = serializers.IntegerField(required=False)
    clicked = serializers.IntegerField(required=False)


class ReportsGetSerializer(serializers.Serializer):
    """
    This is the Reports Serializer.

    This formats the data returned
    from the reports api call
    """

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
    """
    This is an Emailed Reports Serializer.

    Thsi formats the data returned
    from the reports api call
    """

    subscription_uuid = serializers.CharField()
