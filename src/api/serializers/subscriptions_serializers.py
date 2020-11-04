from api.serializers.customer_serializers import CustomerContactSerializer
from api.serializers.campaign_serializers import GoPhishCampaignsSerializer
from api.serializers.phishing_serializers import (
    SubscriptionTargetSerializer,
    PhishingResultsSerializer,
)

from rest_framework import serializers


class SubscriptionEmailHistorySerializer(serializers.Serializer):
    report_type = serializers.CharField(max_length=255)
    sent = serializers.DateTimeField()
    email_to = serializers.EmailField()
    email_from = serializers.CharField(max_length=255)
    bcc = serializers.EmailField(default=None)
    manual = serializers.BooleanField(default=False)


class SubscriptionClicksSerializer(serializers.Serializer):
    source_ip = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()
    target_uuid = serializers.UUIDField()


class CycleSerializer(serializers.Serializer):
    cycle_uuid = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    active = serializers.BooleanField()
    campaigns_in_cycle = serializers.ListField()
    phish_results = PhishingResultsSerializer()
    phish_results_dirty = serializers.BooleanField(required=False)
    override_total_reported = serializers.IntegerField(default=-1)


class SubscriptionTasksSerializer(serializers.Serializer):
    task_uuid = serializers.CharField()
    message_type = serializers.CharField()
    scheduled_date = serializers.DateTimeField()
    executed = serializers.BooleanField(required=False)
    executed_date = serializers.DateTimeField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SubscriptionSerializer(serializers.Serializer):
    # created by mongodb
    subscription_uuid = serializers.UUIDField(required=False)
    # values being passed in.
    customer_uuid = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False, max_length=100)
    url = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
    )
    target_domain = serializers.CharField(required=False)
    keywords = serializers.CharField(max_length=100, required=False, allow_blank=True)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    campaigns = GoPhishCampaignsSerializer(many=True, required=False)
    primary_contact = CustomerContactSerializer(required=False)
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(required=False, max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=False, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        many=True, required=False
    )
    templates_selected_uuid_list = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(required=False)
    manually_stopped = serializers.BooleanField(required=False)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    cycles = CycleSerializer(required=False, many=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)
    stagger_emails = serializers.BooleanField(required=False)
    # db data tracking added below
    created_by = serializers.CharField(required=False, max_length=100)
    cb_timestamp = serializers.DateTimeField(required=False)
    last_updated_by = serializers.CharField(required=False, max_length=100)
    lub_timestamp = serializers.DateTimeField(required=False)


class SubscriptionPostSerializer(serializers.Serializer):
    customer_uuid = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    target_domain = serializers.CharField(required=False)
    url = serializers.CharField(
        required=False, max_length=100, allow_null=True, allow_blank=True
    )
    keywords = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField(required=False)
    primary_contact = CustomerContactSerializer()
    dhs_contact_uuid = serializers.UUIDField()
    status = serializers.CharField(max_length=100)
    target_email_list = SubscriptionTargetSerializer(many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(many=True)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    templates_selected_uuid_list = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    sending_profile_name = serializers.CharField()
    active = serializers.BooleanField()
    archived = serializers.BooleanField(default=False)
    manually_stopped = serializers.BooleanField(default=False)
    cycles = CycleSerializer(required=False, many=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)
    stagger_emails = serializers.BooleanField(default=True)


class SubscriptionPatchSerializer(serializers.Serializer):
    customer_uuid = serializers.UUIDField(required=False)
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
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(required=False, max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=False, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        required=False, many=True
    )
    tasks = SubscriptionTasksSerializer(many=True, required=False)
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


class SubscriptionResponseSerializer(serializers.Serializer):
    subscription_uuid = serializers.UUIDField()


class SubscriptionQuerySerializer(serializers.Serializer):
    customer_uuid = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False)
    url = serializers.CharField(required=False)
    target_domain = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    status = serializers.CharField(required=False)
    templates_selected_uuid_list = serializers.ListField(required=False)
    dhs_contact_uuid = serializers.UUIDField(required=False)
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(default=False, required=False)
    manually_stopped = serializers.BooleanField(required=False)
    stagger_emails = serializers.BooleanField(required=False)
