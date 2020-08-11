"""
Landing Page Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from api.serializers.subscriptions_serializers import (
    SubscriptionPatchResponseSerializer,
)
from api.serializers.template_serializers import TemplateImageSerializer
from rest_framework import serializers

TEMPLATE_TYPE_CHOICES = (("Landing", "Landing Page"),)


class LandingPageGetSerializer(serializers.Serializer):
    """
    This is the LandingPage GET Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    image_list = TemplateImageSerializer(many=True)
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    html = serializers.CharField()
    # db tracking data added below
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class LandingPagePostSerializer(serializers.Serializer):
    """
    This is the LandingPage POST Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    image_list = TemplateImageSerializer(many=True)
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    subject = serializers.CharField(max_length=200)

    html = serializers.CharField()
    topic_list = serializers.ListField()
    # Score data


class LandingPagePostResponseSerializer(serializers.Serializer):
    """
    This is the LandingPage Post Response Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()


class LandingPagePatchSerializer(serializers.Serializer):
    """
    This is the LandingPage PATCH Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()
    name = serializers.CharField(required=False)
    template_type = serializers.ChoiceField(
        choices=TEMPLATE_TYPE_CHOICES, required=False
    )
    image_list = TemplateImageSerializer(many=True, required=False)
    retired = serializers.BooleanField(default=False, required=False)
    retired_description = serializers.CharField(default="", required=False)
    html = serializers.CharField(required=False)


class LandingPagePatchResponseSerializer(serializers.Serializer):
    """
    This is the LandingPage PATCH Response Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    image_list = TemplateImageSerializer(many=True)
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    html = serializers.CharField()
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class LandingPageDeleteResponseSerializer(serializers.Serializer):
    """
    This is the LandingPage DELETE Response Serializer.

    This is a formats the data coming out of the Db.
    """

    landing_page_uuid = serializers.UUIDField()


class LandingPageStopResponseSerializer(serializers.Serializer):
    """This is the LandingPage STOP Response Serializer."""

    template = LandingPagePatchResponseSerializer()
    subscriptions = SubscriptionPatchResponseSerializer(many=True)


class LandingPageQuerySerializer(serializers.Serializer):
    """
    Serializes templete Query.

    This is sets queries we can run on db collection.
    """

    gophish_template_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    template_type = serializers.ChoiceField(
        choices=TEMPLATE_TYPE_CHOICES, required=False
    )
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
