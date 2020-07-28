# Third-Party Libraries
from rest_framework import serializers


class DHSContactGetSerializer(serializers.Serializer):
    """
    This is the CustomerContact Serializer.

    This is a formats the data coming out of the Db.
    """

    dhs_contact_uuid = serializers.UUIDField()
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    title = serializers.CharField(required=False, max_length=250)
    office_phone = serializers.CharField(required=False, max_length=100)
    mobile_phone = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
    notes = serializers.CharField(
        required=False, max_length=None, min_length=None, allow_blank=True
    )
    active = serializers.BooleanField(default=True, allow_null=False)

    # db data
    created_by = serializers.CharField(max_length=100)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=100)
    lub_timestamp = serializers.DateTimeField()


class DHSContactPostSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    title = serializers.CharField(max_length=250)
    office_phone = serializers.CharField(required=False, max_length=100)
    mobile_phone = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
    notes = serializers.CharField(
        required=False, max_length=None, min_length=None, allow_blank=True
    )
    active = serializers.BooleanField(required=False, default=True, allow_null=False)


class DHSContactPostResponseSerializer(serializers.Serializer):
    dhs_contact_uuid = serializers.UUIDField()


class DHSContactDeleteResponseSerializer(serializers.Serializer):
    dhs_contact_uuid = serializers.UUIDField()


class DHSContactPatchSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=250)
    last_name = serializers.CharField(required=False, max_length=250)
    title = serializers.CharField(required=False, max_length=250)
    office_phone = serializers.CharField(required=False, max_length=100)
    mobile_phone = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(
        required=False, max_length=None, min_length=None, allow_blank=False
    )
    notes = serializers.CharField(
        required=False, max_length=None, min_length=None, allow_blank=True
    )
    active = serializers.BooleanField(required=False, default=True, allow_null=False)


class DHSContactQuerySerializer(serializers.Serializer):
    dhs_contact_uuid = serializers.UUIDField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    office_phone = serializers.CharField(required=False)
    mobile_phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    notes = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)

    # db data
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
