"""Template Serializers."""
# Third-Party Libraries
from rest_framework import serializers

# cisagov Libraries
from api.serializers.subscriptions_serializers import SubscriptionSerializer


class TemplateAppearanceSerializer(serializers.Serializer):
    """TemplateAppearanceSerializer."""

    grammar = serializers.IntegerField()
    link_domain = serializers.IntegerField()
    logo_graphics = serializers.IntegerField()


class TemplateSenderSerializer(serializers.Serializer):
    """TemplateSenderSerializer."""

    external = serializers.IntegerField()
    internal = serializers.IntegerField()
    authoritative = serializers.IntegerField()


class TemplateRelevancySerializer(serializers.Serializer):
    """TemplateRelevancySerializer."""

    organization = serializers.IntegerField()
    public_news = serializers.IntegerField()


class TemplateBehaviorSerializer(serializers.Serializer):
    """TemplateBehaviorSerializer."""

    fear = serializers.IntegerField()
    duty_obligation = serializers.IntegerField()
    curiosity = serializers.IntegerField()
    greed = serializers.IntegerField()


class TemplateSerializer(serializers.Serializer):
    """TemplateSerializer."""

    template_uuid = serializers.UUIDField()
    name = serializers.CharField()
    landing_page_uuid = serializers.CharField(default=None, allow_null=True)
    sending_profile_id = serializers.IntegerField(default=None, allow_null=True)
    deception_score = serializers.IntegerField()
    descriptive_words = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(allow_null=True)
    from_address = serializers.CharField()
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(
        default="", allow_blank=True, allow_null=True
    )
    subject = serializers.CharField(max_length=200)
    text = serializers.CharField()
    html = serializers.CharField()
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


class TemplatePostSerializer(serializers.Serializer):
    """TemplatePostSerializer."""

    name = serializers.CharField()
    landing_page_uuid = serializers.CharField(required=False, allow_null=True)
    sending_profile_id = serializers.IntegerField(required=False, allow_null=True)
    deception_score = serializers.IntegerField()
    descriptive_words = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    from_address = serializers.CharField()
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(
        default="", allow_blank=True, allow_null=True
    )
    subject = serializers.CharField(max_length=200)
    text = serializers.CharField()
    html = serializers.CharField()
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()


class TemplatePatchSerializer(serializers.Serializer):
    """TemplatePatchSerializer."""

    name = serializers.CharField(required=False)
    landing_page_uuid = serializers.CharField(required=False, allow_null=True)
    sending_profile_id = serializers.IntegerField(required=False, allow_null=True)
    deception_score = serializers.IntegerField(required=False)
    descriptive_words = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    from_address = serializers.CharField(required=False)
    retired = serializers.BooleanField(default=False, required=False)
    retired_description = serializers.CharField(
        default="", required=False, allow_blank=True, allow_null=True
    )
    subject = serializers.CharField(max_length=200, required=False)
    text = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer(required=False)
    sender = TemplateSenderSerializer(required=False)
    relevancy = TemplateRelevancySerializer(required=False)
    behavior = TemplateBehaviorSerializer(required=False)


class TemplateResponseSerializer(serializers.Serializer):
    """TemplateResponseSerializer."""

    template_uuid = serializers.UUIDField()


class TemplateStopResponseSerializer(serializers.Serializer):
    """TemplateStopResponseSerializer."""

    template = TemplateSerializer()
    subscriptions = SubscriptionSerializer(many=True)


class TemplateQuerySerializer(serializers.Serializer):
    """TemplateQuerySerializer."""

    name = serializers.CharField(required=False)
    deception_score = serializers.IntegerField(required=False)
    descriptive_words = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    from_address = serializers.CharField(required=False)
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    landing_page_uuid = serializers.CharField(required=False)
    sending_profile_id = serializers.IntegerField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)
