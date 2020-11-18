"""Sending Profile Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class HeaderSerializer(serializers.Serializer):
    """HeaderSerializer."""

    key = serializers.CharField()
    value = serializers.CharField()


class SendingProfileSerializer(serializers.Serializer):
    """SendingProfileSerializer."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    host = serializers.CharField()
    interface_type = serializers.CharField()
    from_address = serializers.CharField()
    ignore_cert_errors = serializers.BooleanField()
    modified_date = serializers.CharField()
    headers = HeaderSerializer(many=True)


class SendingProfilePatchSerializer(serializers.Serializer):
    """SendingProfilePatchSerializer."""

    name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    host = serializers.CharField(max_length=255, required=False)
    interface_type = serializers.CharField(required=False)
    from_address = serializers.CharField(required=False)
    ignore_cert_errors = serializers.BooleanField(required=False)
    modified_date = serializers.CharField(required=False)
    headers = HeaderSerializer(many=True)


class SendingProfilePatchResponseSerializer(serializers.Serializer):
    """SendingProfilePatchResponseSerializer."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    host = serializers.CharField(max_length=255)
    interface_type = serializers.CharField()
    from_address = serializers.CharField()
    ignore_cert_errors = serializers.BooleanField()
    modified_date = serializers.CharField()
    headers = HeaderSerializer(many=True)


class SendingProfileDeleteSerializer(serializers.Serializer):
    """SendingProfileDeleteSerializer."""

    id = serializers.IntegerField()


class SendingProfileDeleteResponseSerializer(serializers.Serializer):
    """SendingProfileDeleteResponseSerializer."""

    id = serializers.IntegerField()
