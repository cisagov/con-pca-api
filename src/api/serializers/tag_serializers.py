"""Tag Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class TagSerializer(serializers.Serializer):
    """Tag Serializer."""

    tag_definition_uuid = serializers.UUIDField()
    tag = serializers.CharField()
    description = serializers.CharField()
    data_source = serializers.CharField()
    tag_type = serializers.CharField()
    # db tracking data added below
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class TagPostSerializer(serializers.Serializer):
    """TagPost Serializer."""

    tag = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    data_source = serializers.CharField(required=True)
    tag_type = serializers.CharField(required=True)


class TagResponseSerializer(serializers.Serializer):
    """TagResponse Serializer."""

    tag_definition_uuid = serializers.UUIDField()


class TagPatchSerializer(serializers.Serializer):
    """TagPatch Serializer."""

    tag = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    data_source = serializers.CharField(required=False)
    tag_type = serializers.CharField(required=False)


class TagQuerySerializer(serializers.Serializer):
    """TagQuery Serializer."""

    tag = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    data_source = serializers.CharField(required=False)
    tag_type = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
