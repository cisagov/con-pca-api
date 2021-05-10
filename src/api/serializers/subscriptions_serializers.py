"""Subscription Serializers."""

# Third-Party Libraries
from rest_framework import serializers

# cisagov Libraries
from api.serializers.campaign_serializers import GoPhishCampaignsSerializer
from api.serializers.customer_serializers import CustomerContactSerializer
from api.serializers.phishing_serializers import (
    PhishingResultsSerializer,
    SubscriptionTargetSerializer,
)


class SubscriptionEmailHistorySerializer(serializers.Serializer):
    """SubscriptionEmailHistorySerializer."""

    report_type = serializers.CharField(max_length=255)
    sent = serializers.DateTimeField()
    email_to = serializers.EmailField()
    email_from = serializers.CharField(max_length=255)
    bcc = serializers.EmailField(default=None)
    manual = serializers.BooleanField(default=False)


class SubscriptionClicksSerializer(serializers.Serializer):
    """SubscriptionClicksSerializer."""

    source_ip = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()
    target_uuid = serializers.UUIDField()


class CycleSerializer(serializers.Serializer):
    """CycleSerializer."""

    cycle_uuid = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    active = serializers.BooleanField()
    campaigns_in_cycle = serializers.ListField()
    phish_results = PhishingResultsSerializer()
    phish_results_dirty = serializers.BooleanField(required=False, default=False)
    override_total_reported = serializers.IntegerField(default=-1)
    total_targets = serializers.IntegerField(default=0)


class SubscriptionTasksSerializer(serializers.Serializer):
    """SubscriptionTasksSerializer."""

    task_uuid = serializers.CharField()
    message_type = serializers.CharField()
    scheduled_date = serializers.DateTimeField()
    queued = serializers.BooleanField(default=False, allow_null=True)
    executed = serializers.BooleanField(default=False)
    executed_date = serializers.DateTimeField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SubscriptionTemplatesSelectedSerializer(serializers.Serializer):
    """SubscriptionTemplatesSelectedSerializer."""

    low = serializers.ListField(required=True)
    moderate = serializers.ListField(required=True)
    high = serializers.ListField(required=True)


class SubscriptionSerializer(serializers.Serializer):
    """SubscriptionSerializer."""

    # created by mongodb
    subscription_uuid = serializers.UUIDField(required=False)
    # values being passed in.
    customer_uuid = serializers.CharField(required=False)
    name = serializers.CharField(required=False, max_length=100)
    url = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        allow_null=True,
    )
    target_domain = serializers.CharField(required=False)
    keywords = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False, allow_null=True)
    campaigns = GoPhishCampaignsSerializer(many=True, required=False)
    primary_contact = CustomerContactSerializer(required=False)
    dhs_contact_uuid = serializers.CharField(required=False)
    status = serializers.CharField(required=False, max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=False, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        many=True, required=False, allow_null=True
    )
    templates_selected_uuid_list = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_null=True
    )
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(required=False)
    manually_stopped = serializers.BooleanField(required=False)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    cycles = CycleSerializer(required=False, many=True, allow_null=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)
    stagger_emails = serializers.BooleanField(required=False)
    continuous_subscription = serializers.BooleanField(default=True)
    cycle_length_minutes = serializers.IntegerField(required=False)
    # db data tracking added below
    created_by = serializers.CharField(required=False, max_length=100)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False, max_length=100)
    lub_timestamp = serializers.DateTimeField(required=False)


class SubscriptionPostSerializer(serializers.Serializer):
    """SubscriptionPostSerializer."""

    customer_uuid = serializers.CharField()
    name = serializers.CharField(max_length=100)
    target_domain = serializers.CharField(required=False)
    url = serializers.CharField(
        required=False, max_length=100, allow_null=True, allow_blank=True
    )
    keywords = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    start_date = serializers.DateTimeField()
    primary_contact = CustomerContactSerializer()
    dhs_contact_uuid = serializers.CharField()
    status = serializers.CharField(max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=True, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        required=True, many=True
    )
    tasks = SubscriptionTasksSerializer(many=True, required=True)
    templates_selected = SubscriptionTemplatesSelectedSerializer(required=True)
    sending_profile_name = serializers.CharField()
    active = serializers.BooleanField()
    stagger_emails = serializers.BooleanField(default=True)
    continuous_subscription = serializers.BooleanField(default=True)
    cycle_length_minutes = serializers.IntegerField(
        default=129600, max_value=518400, min_value=15
    )  # max of 360 days, min of 15 minutes


class SubscriptionPatchSerializer(serializers.Serializer):
    """SubscriptionPatchSerializer."""

    customer_uuid = serializers.CharField(required=False)
    name = serializers.CharField(required=False, max_length=100)
    target_domain = serializers.CharField(required=False)
    url = serializers.CharField(
        required=False, max_length=100, allow_null=True, allow_blank=True
    )
    keywords = serializers.CharField(
        required=False, max_length=100, allow_blank=True, allow_null=True
    )
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    primary_contact = CustomerContactSerializer(required=False)
    dhs_contact_uuid = serializers.CharField(required=False)
    status = serializers.CharField(required=False, max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=False, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        required=False, many=True
    )
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    templates_selected = SubscriptionTemplatesSelectedSerializer(required=False)
    templates_selected_uuid_list = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(required=False, default=False)
    manually_stopped = serializers.BooleanField(required=False, default=False)
    cycles = CycleSerializer(required=False, many=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)
    stagger_emails = serializers.BooleanField(required=False)
    continuous_subscription = serializers.BooleanField(required=False)
    cycle_length_minutes = serializers.IntegerField(
        required=False, max_value=518400, min_value=15
    )  # max of 360 days, min of 15 minutes


class SubscriptionResponseSerializer(serializers.Serializer):
    """SubscriptionResponseSerializer."""

    subscription_uuid = serializers.UUIDField()


class SubscriptionQuerySerializer(serializers.Serializer):
    """SubscriptionQuerySerializer."""

    customer_uuid = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    url = serializers.CharField(required=False)
    target_domain = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    status = serializers.CharField(required=False)
    templates_selected = SubscriptionTemplatesSelectedSerializer(required=False)
    templates_selected_uuid_list = serializers.ListField(required=False)
    dhs_contact_uuid = serializers.CharField(required=False)
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(default=False, required=False)
    manually_stopped = serializers.BooleanField(required=False)
    stagger_emails = serializers.BooleanField(required=False)
