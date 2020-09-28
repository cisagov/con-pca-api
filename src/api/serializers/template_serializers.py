"""
Template Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from api.serializers.subscriptions_serializers import (
    SubscriptionPatchResponseSerializer,
)
from rest_framework import serializers

TEMPLATE_TYPE_CHOICES = (
    ("Email", "Email"),
    ("Landing", "Landing Page"),
)


class TemplateAppearanceSerializer(serializers.Serializer):
    """
    This is the Template Serializer.

    This holds values for template Appearance Score.
    """

    grammar = serializers.IntegerField()
    link_domain = serializers.IntegerField()
    logo_graphics = serializers.IntegerField()


class TemplateSenderSerializer(serializers.Serializer):
    """
    This is the Template Sender Serializer.

    This holds values for template Sender Score.
    """

    external = serializers.IntegerField()
    internal = serializers.IntegerField()
    authoritative = serializers.IntegerField()


class TemplateRelevancySerializer(serializers.Serializer):
    """
    This is the Template Relevancy Serializer.

    This holds values for template Relevancy Score.
    """

    organization = serializers.IntegerField()
    public_news = serializers.IntegerField()


class TemplateBehaviorSerializer(serializers.Serializer):
    """
    This is the Template Behavior Model.

    This holds values for template Behavior Score.
    """

    fear = serializers.IntegerField()
    duty_obligation = serializers.IntegerField()
    curiosity = serializers.IntegerField()
    greed = serializers.IntegerField()


class TemplateImageSerializer(serializers.Serializer):
    """
    This is the Template Image Model.

    This holds values for template Image data.
    """

    file_name = serializers.CharField()
    file_url = serializers.CharField()


class TemplateGetSerializer(serializers.Serializer):
    """
    This is the Template GET Serializer.

    This is a formats the data coming out of the Db.
    """

    template_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    landing_page_uuid = serializers.UUIDField(default=None)
    deception_score = serializers.IntegerField()
    descriptive_words = serializers.CharField()
    description = serializers.CharField()
    image_list = TemplateImageSerializer(many=True)
    from_address = serializers.EmailField()
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    subject = serializers.CharField(max_length=200)
    text = serializers.CharField()
    html = serializers.CharField()
    topic_list = serializers.ListField()
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


class TemplatePostSerializer(serializers.Serializer):
    """
    This is the Template POST Serializer.

    This is a formats the data coming out of the Db.
    """

    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    landing_page_uuid = serializers.UUIDField(required=False)
    deception_score = serializers.IntegerField()
    descriptive_words = serializers.CharField()
    description = serializers.CharField()
    image_list = TemplateImageSerializer(many=True)
    from_address = serializers.EmailField()
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    subject = serializers.CharField(max_length=200)
    text = serializers.CharField()
    html = serializers.CharField()
    topic_list = serializers.ListField()
    # Score data
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    complexity = serializers.IntegerField()


class TemplatePostResponseSerializer(serializers.Serializer):
    """
    This is the Template Post Response Serializer.

    This is a formats the data coming out of the Db.
    """

    template_uuid = serializers.UUIDField()


class TemplatePatchSerializer(serializers.Serializer):
    """
    This is the Template PATCH Serializer.

    This is a formats the data coming out of the Db.
    """

    name = serializers.CharField(required=False)
    template_type = serializers.ChoiceField(
        choices=TEMPLATE_TYPE_CHOICES, required=False
    )
    landing_page_uuid = serializers.UUIDField(required=False)
    deception_score = serializers.IntegerField(required=False)
    descriptive_words = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    image_list = TemplateImageSerializer(many=True, required=False)
    from_address = serializers.EmailField(required=False)
    retired = serializers.BooleanField(default=False, required=False)
    retired_description = serializers.CharField(default="", required=False)
    subject = serializers.CharField(max_length=200, required=False)
    text = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    topic_list = serializers.ListField(required=False)
    # Score data
    appearance = TemplateAppearanceSerializer(required=False)
    sender = TemplateSenderSerializer(required=False)
    relevancy = TemplateRelevancySerializer(required=False)
    behavior = TemplateBehaviorSerializer(required=False)
    complexity = serializers.IntegerField(required=False)


class TemplatePatchResponseSerializer(serializers.Serializer):
    """
    This is the Template PATCH Response Serializer.

    This is a formats the data coming out of the Db.
    """

    template_uuid = serializers.UUIDField()
    gophish_template_id = serializers.IntegerField()
    name = serializers.CharField()
    template_type = serializers.ChoiceField(choices=TEMPLATE_TYPE_CHOICES)
    landing_page_uuid = serializers.UUIDField()
    deception_score = serializers.IntegerField()
    descriptive_words = serializers.CharField()
    description = serializers.CharField()
    image_list = TemplateImageSerializer(many=True)
    from_address = serializers.EmailField()
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(default="")
    subject = serializers.CharField(max_length=200)
    text = serializers.CharField()
    html = serializers.CharField()
    topic_list = serializers.ListField()
    appearance = TemplateAppearanceSerializer()
    sender = TemplateSenderSerializer()
    relevancy = TemplateRelevancySerializer()
    behavior = TemplateBehaviorSerializer()
    complexity = serializers.IntegerField()
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class TemplateDeleteResponseSerializer(serializers.Serializer):
    """
    This is the Template DELETE Response Serializer.

    This is a formats the data coming out of the Db.
    """

    template_uuid = serializers.UUIDField()


class TemplateStopResponseSerializer(serializers.Serializer):
    """This is the Template STOP Response Serializer."""

    template = TemplatePatchResponseSerializer()
    subscriptions = SubscriptionPatchResponseSerializer(many=True)


class TagGetSerializer(serializers.Serializer):
    """Serializes a Tag (replaceable token in a template)."""

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
    """Serializes a Tag (replaceable token in a template)."""

    tag = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    data_source = serializers.CharField(required=True)
    tag_type = serializers.CharField(required=True)


class TagResponseSerializer(serializers.Serializer):
    """
    Serializes the response for a Tag (replaceable token in a template).

    This is a formats the data coming out of the Db.
    """

    tag_definition_uuid = serializers.UUIDField()


class TagPatchSerializer(serializers.Serializer):
    """Serializes a Tag (replaceable token in a template)."""

    tag = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    data_source = serializers.CharField(required=False)
    tag_type = serializers.CharField(required=False)


class TagDeleteSerializer(serializers.Serializer):
    """Serializes a Tag (replaceable token in a template)."""

    tag_definition_uuid = serializers.UUIDField()


class TemplateQuerySerializer(serializers.Serializer):
    """
    Serializes templete Query.

    This is sets queries we can run on db collection.
    """

    gophish_template_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    template_type = serializers.ChoiceField(
        choices=TEMPLATE_TYPE_CHOICES, required=False
    )
    deception_score = serializers.IntegerField(required=False)
    descriptive_words = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    from_address = serializers.EmailField(required=False)
    retired = serializers.BooleanField(default=False)
    retired_description = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    landing_page_uuid = serializers.UUIDField(required=False)
    topic_list = serializers.ListField(required=False)
    complexity = serializers.IntegerField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)


class TagQuerySerializer(serializers.Serializer):
    """
    Serializes Tag Query.

    This is sets queries we can run on db collection.
    """

    tag = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    data_source = serializers.CharField(required=False)
    tag_type = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False)
    lub_timestamp = serializers.DateTimeField(required=False)


class TemplateStatusSerializer(serializers.Serializer):
    """
    Serializes Template Status.

    This handles nested data for Tempalte history
    """

    template_uuid = serializers.UUIDField()
    sent_timestamp = serializers.DateTimeField(required=False)


class TargetHistoryGetSerializer(serializers.Serializer):
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
