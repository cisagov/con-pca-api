# Third-Party Libraries
"""TargetHistory Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class TemplateStatusSerializer(serializers.Serializer):
    """TemplateStatusSerializer."""

    template_uuid = serializers.CharField()
    sent_timestamp = serializers.DateTimeField(required=False)


class TargetHistorySerializer(serializers.Serializer):
    """TargetHistorySerializer."""

    # created by mongodb
    target_uuid = serializers.UUIDField()
    # User Defined
    email = serializers.EmailField(required=True)
    history_list = TemplateStatusSerializer(many=True)
    # db tracking data added below
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)


class TargetHistoryPostSerializer(serializers.Serializer):
    """TargetHistoryPostSerializer."""

    # User Defined
    email = serializers.EmailField(required=True)
    history_list = TemplateStatusSerializer(many=True)


class TargetHistoryPatchSerializer(serializers.Serializer):
    """TargetHistoryPatchSerializer."""

    # User Defined
    history_list = TemplateStatusSerializer(many=True)


class TargetHistoryResponseSerializer(serializers.Serializer):
    """TargetHistoryResponseSerializer."""

    target_uuid = serializers.UUIDField()
