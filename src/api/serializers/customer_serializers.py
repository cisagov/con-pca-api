"""Customer Serializers."""
# Third-Party Libraries
from rest_framework import serializers


class CustomerContactSerializer(serializers.Serializer):
    """CustomerContact Serializer."""

    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    title = serializers.CharField(
        required=False, max_length=250, allow_blank=True, allow_null=True
    )
    office_phone = serializers.CharField(
        max_length=100, allow_blank=True, allow_null=True
    )
    mobile_phone = serializers.CharField(
        max_length=100, allow_blank=True, allow_null=True
    )
    email = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
    notes = serializers.CharField(
        required=False,
        max_length=None,
        min_length=None,
        allow_blank=True,
        allow_null=True,
    )
    active = serializers.BooleanField(default=True, allow_null=False)


class CustomerSerializer(serializers.Serializer):
    """Customer Serializer."""

    # created by mongodb
    customer_uuid = serializers.UUIDField()
    # user created fields
    name = serializers.CharField(max_length=250)
    identifier = serializers.CharField(max_length=250)
    address_1 = serializers.CharField(max_length=250)
    address_2 = serializers.CharField(
        max_length=250, required=False, allow_blank=True, allow_null=True
    )
    city = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=250)
    zip_code = serializers.CharField(max_length=250)
    customer_type = serializers.CharField(max_length=250, required=False)
    contact_list = CustomerContactSerializer(many=True)
    industry = serializers.CharField(
        required=False, max_length=250, allow_blank=True, allow_null=True
    )
    sector = serializers.CharField(
        required=False, max_length=250, allow_blank=True, allow_null=True
    )
    # db data tracking added below
    created_by = serializers.CharField(max_length=100)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=100)
    lub_timestamp = serializers.DateTimeField()


class CustomerPostSerializer(serializers.Serializer):
    """CustomerPost Serializer."""

    # user created fields
    name = serializers.CharField(max_length=250)
    identifier = serializers.CharField(max_length=250)
    address_1 = serializers.CharField(max_length=250)
    address_2 = serializers.CharField(
        max_length=250, required=False, allow_blank=True, allow_null=True
    )
    city = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=250)
    zip_code = serializers.CharField(max_length=250)
    customer_type = serializers.CharField(max_length=250)
    contact_list = CustomerContactSerializer(many=True)
    industry = serializers.CharField(max_length=250, allow_blank=True, allow_null=True)
    sector = serializers.CharField(max_length=250, allow_blank=True, allow_null=True)


class CustomerPatchSerializer(serializers.Serializer):
    """CustomerPatch Serializer."""

    name = serializers.CharField(max_length=250, required=False)
    identifier = serializers.CharField(max_length=250, required=False)
    address_1 = serializers.CharField(max_length=250, required=False)
    address_2 = serializers.CharField(
        max_length=250, required=False, allow_blank=True, allow_null=True
    )
    city = serializers.CharField(max_length=250, required=False)
    state = serializers.CharField(max_length=250, required=False)
    zip_code = serializers.CharField(max_length=250, required=False)
    customer_type = serializers.CharField(max_length=250, required=False)
    contact_list = CustomerContactSerializer(many=True, required=False)
    industry = serializers.CharField(
        max_length=250, required=False, allow_blank=True, allow_null=True
    )
    sector = serializers.CharField(
        max_length=250, required=False, allow_blank=True, allow_null=True
    )


class CustomerResponseSerializer(serializers.Serializer):
    """Customer Response Serializer."""

    customer_uuid = serializers.UUIDField()


class SectorIndustry(serializers.Serializer):
    """SectorIndustry Serializer."""

    name = serializers.CharField(max_length=250)


class SectorGetSerializer(serializers.Serializer):
    """SectorIndustryGet Serializer."""

    name = serializers.CharField(max_length=250)
    industries = SectorIndustry(many=True)


class CustomerQuerySerializer(serializers.Serializer):
    """Customer Query Serializer."""

    # user created fields
    name = serializers.CharField(required=False)
    identifier = serializers.CharField(required=False)
    address_1 = serializers.CharField(required=False)
    address_2 = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    customer_type = serializers.CharField(max_length=250, required=False)
    industry = serializers.CharField(required=False, max_length=250)
    sector = serializers.CharField(required=False, max_length=250)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
