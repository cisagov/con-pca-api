"""
Landing Page Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from api.serializers.subscriptions_serializers import (
    SubscriptionSerializer,
)
from rest_framework import serializers


class LandingPageSerializer(serializers.Serializer):
    landing_page_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    is_default_template = serializers.BooleanField(default=False)
    html = serializers.CharField()
    # db tracking data added below
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class LandingPagePostSerializer(serializers.Serializer):
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    is_default_template = serializers.BooleanField(default=False)
    html = serializers.CharField()


class LandingPagePatchSerializer(serializers.Serializer):
    gophish_template_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    is_default_template = serializers.BooleanField(default=False, required=False)
    html = serializers.CharField(required=False)


class LandingPageResponseSerializer(serializers.Serializer):
    landing_page_uuid = serializers.UUIDField()


class LandingPageQuerySerializer(serializers.Serializer):
    gophish_template_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    is_default_template = serializers.BooleanField(default=False)
    html = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
