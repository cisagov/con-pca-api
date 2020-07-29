"""
Recommendation Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from rest_framework import serializers

from api.serializers.template_serializers import (
    TemplateAppearanceSerializer,
    TemplateSenderSerializer,
    TemplateRelevancySerializer,
    TemplateBehaviorSerializer,
)


class RecommendationsGetSerializer(serializers.Serializer):
    """
    This is the Recommendation GET Serializer.

    This is a formats the data coming out of the Db.
    """

    recommendations_uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    deception_level = serializers.IntegerField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    complexity = serializers.IntegerField()
    # db tracking data added below
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class RecommendationsPostSerializer(serializers.Serializer):
    """
    This is the Recommendation POST Serializer.

    This is a formats the data coming out of the Db.
    """

    name = serializers.CharField()
    description = serializers.CharField()
    deception_level = serializers.IntegerField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    complexity = serializers.IntegerField()


class RecommendationsPostResponseSerializer(serializers.Serializer):
    """
    This is the Recommendation Post Response Serializer.

    This is a formats the data coming out of the Db.
    """

    recommendations_uuid = serializers.UUIDField()


class RecommendationsPatchSerializer(serializers.Serializer):
    """
    This is the Recommendations PATCH Serializer.

    This is a formats the data coming out of the Db.
    """

    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    deception_level = serializers.IntegerField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer(required=False)
    sender = TemplateSenderSerializer(required=False)
    relevancy = TemplateRelevancySerializer(required=False)
    behavior = TemplateBehaviorSerializer(required=False)
    complexity = serializers.IntegerField(required=False)


class RecommendationsPatchResponseSerializer(serializers.Serializer):
    """
    This is the Recommendations PATCH Response Serializer.

    This is a formats the data coming out of the Db.
    """

    recommendations_uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    deception_level = serializers.IntegerField(required=False)
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    complexity = serializers.IntegerField()
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class RecommendationsQuerySerializer(serializers.Serializer):
    """
    Serializes Recommendations Query.

    This is sets queries we can run on db collection.
    """

    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    deception_level = serializers.IntegerField(required=False)
    complexity = serializers.IntegerField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)


class RecommendationsDeleteResponseSerializer(serializers.Serializer):
    """
    This is the Recommendations DELETE Response Serializer.

    This is a formats the data coming out of the Db.
    """

    recommendations_uuid = serializers.UUIDField()
