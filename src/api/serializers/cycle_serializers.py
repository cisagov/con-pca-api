"""
Cycle Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from rest_framework import serializers


class CycleEmailReportedSerializer(serializers.Serializer):
    """
    This is the Cycle Email Report data Serializer.

    This is a formats the list of Cycle Email Reports.
    """

    campaign_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    date = serializers.DateTimeField(required=True)


class CycleEmailReportedListSerializer(serializers.Serializer):
    """
    This is the Cycle Email Report data Serializer.

    This is a formats the list of Cycle Email Reports.
    """
    cycle_uuid = serializers.CharField()
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    email_list = CycleEmailReportedSerializer(many=True)
    override_total_reported = serializers.IntegerField(required=False)


class CycleEmailReportedListPostSerializer(serializers.Serializer):
    """
    This is the Cycle Email Report data Serializer.

    This is a formats the list of Cycle Email Reports.
    """

    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    update_list = CycleEmailReportedSerializer(many=True)
    delete_list = CycleEmailReportedSerializer(many=True)
    override_total_reported = serializers.IntegerField(required=False)
