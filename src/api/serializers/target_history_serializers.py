from rest_framework import serializers


class TemplateStatusSerializer(serializers.Serializer):
    """
    Serializes Template Status.

    This handles nested data for Tempalte history
    """

    template_uuid = serializers.UUIDField()
    sent_timestamp = serializers.DateTimeField(required=False)


class TargetHistorySerializer(serializers.Serializer):
    """
    Serializes Template History.

    This handles the history of a targets tempaltes.
    """

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
    """
    Serializes Template History.

    This handles the history of a targets tempaltes.
    """

    # User Defined
    email = serializers.EmailField(required=True)
    history_list = TemplateStatusSerializer(many=True)


class TargetHistoryPatchSerializer(serializers.Serializer):
    """
    Serializes Template History.

    This handles the history of a targets tempaltes.
    """

    # User Defined
    history_list = TemplateStatusSerializer(many=True)


class TargetHistoryResponseSerializer(serializers.Serializer):
    """
    Serializes the response for a Tag (replaceable token in a template).

    This is a formats the data coming out of the Db.
    """

    target_uuid = serializers.UUIDField()
