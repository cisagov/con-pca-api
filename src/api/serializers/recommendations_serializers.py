"""Recommendation Serializers."""
# Third-Party Libraries
from rest_framework import serializers

# cisagov Libraries
from api.serializers.template_serializers import (
    TemplateAppearanceSerializer,
    TemplateBehaviorSerializer,
    TemplateRelevancySerializer,
    TemplateSenderSerializer,
)


class RecommendationsSerializer(serializers.Serializer):
    """RecommendationsSerializer."""

    recommendations_uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    # db tracking data added below
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class RecommendationsPostSerializer(serializers.Serializer):
    """RecommendationsPostSerializer."""

    name = serializers.CharField()
    description = serializers.CharField()
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()


class RecommendationsResponseSerializer(serializers.Serializer):
    """RecommendationsResponseSerializer."""

    recommendations_uuid = serializers.UUIDField()


class RecommendationsPatchSerializer(serializers.Serializer):
    """RecommendationsPatchSerializer."""

    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer(required=False)
    sender = TemplateSenderSerializer(required=False)
    relevancy = TemplateRelevancySerializer(required=False)
    behavior = TemplateBehaviorSerializer(required=False)


class RecommendationsQuerySerializer(serializers.Serializer):
    """RecommendationsQuerySerializer."""

    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
