from rest_framework import serializers
from api.serializers.phishing_serializers import (
    SubscriptionTargetSerializer,
    PhishingResultsSerializer,
)


class SendingHeaderSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)


class GoPhishSmtpSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=0)
    name = serializers.CharField(max_length=255)
    host = serializers.CharField(max_length=255)
    interface_type = serializers.CharField(max_length=255)
    from_address = serializers.CharField(max_length=255)
    ignore_cert_errors = serializers.BooleanField()
    modified_date = serializers.DateTimeField()
    headers = SendingHeaderSerializer(many=True, required=False)


class GoPhishTimelineSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    time = serializers.DateTimeField()
    message = serializers.CharField(max_length=255)
    details = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duplicate = serializers.BooleanField(required=False, allow_null=True)


class GoPhishGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255)
    targets = SubscriptionTargetSerializer(many=True)
    modified_date = serializers.DateTimeField()


class GoPhishResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    position = serializers.CharField()
    status = serializers.CharField(max_length=255)
    ip = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    send_date = serializers.DateTimeField(required=False)
    reported = serializers.BooleanField(required=False)


class GoPhishCampaignsSerializer(serializers.Serializer):
    campaign_uuid = serializers.UUIDField()
    campaign_id = serializers.IntegerField(required=False)
    subscription_uuid = serializers.UUIDField()
    cycle_uuid = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    created_date = serializers.DateTimeField()
    launch_date = serializers.DateTimeField()
    send_by_date = serializers.DateTimeField(required=False)
    completed_date = serializers.DateTimeField(required=False, allow_null=True)
    email_template = serializers.CharField(required=False)
    email_template_id = serializers.IntegerField(required=False)
    template_uuid = serializers.UUIDField()
    deception_level = serializers.IntegerField(required=False)
    landing_page_template = serializers.CharField(required=False)
    status = serializers.CharField(max_length=255)
    results = GoPhishResultSerializer(many=True)
    phish_results = PhishingResultsSerializer()
    phish_results_dirty = serializers.BooleanField(required=False)
    groups = GoPhishGroupSerializer(many=True)
    timeline = GoPhishTimelineSerializer(many=True)
    target_email_list = SubscriptionTargetSerializer(many=True, required=False)
    smtp = GoPhishSmtpSerializer(required=False)
    created_by = serializers.CharField(max_length=200)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=200)
    lub_timestamp = serializers.DateTimeField()


class GoPhishCampaignsPostSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    subscription_uuid = serializers.UUIDField()
    cycle_uuid = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    created_date = serializers.DateTimeField()
    launch_date = serializers.DateTimeField()
    send_by_date = serializers.DateTimeField(required=False)
    completed_date = serializers.DateTimeField(required=False, allow_null=True)
    email_template = serializers.CharField(required=False)
    email_template_id = serializers.IntegerField(required=False)
    template_uuid = serializers.UUIDField()
    deception_level = serializers.IntegerField(required=False)
    landing_page_template = serializers.CharField(required=False)
    status = serializers.CharField(max_length=255)
    results = GoPhishResultSerializer(many=True)
    phish_results = PhishingResultsSerializer()
    phish_results_dirty = serializers.BooleanField(required=False)
    groups = GoPhishGroupSerializer(many=True)
    timeline = GoPhishTimelineSerializer(many=True)
    target_email_list = SubscriptionTargetSerializer(many=True, required=False)
    smtp = GoPhishSmtpSerializer(required=False)


class GoPhishCampaignsPatchSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(required=False)
    subscription_uuid = serializers.UUIDField(required=False)
    cycle_uuid = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=100, required=False)
    created_date = serializers.DateTimeField(required=False)
    launch_date = serializers.DateTimeField(required=False)
    send_by_date = serializers.DateTimeField(required=False)
    completed_date = serializers.DateTimeField(required=False, allow_null=True)
    email_template = serializers.CharField(required=False)
    email_template_id = serializers.IntegerField(required=False)
    template_uuid = serializers.UUIDField(required=False)
    deception_level = serializers.IntegerField(required=False)
    landing_page_template = serializers.CharField(required=False)
    status = serializers.CharField(max_length=255, required=False)
    results = GoPhishResultSerializer(many=True, required=False)
    phish_results = PhishingResultsSerializer(required=False)
    phish_results_dirty = serializers.BooleanField(required=False)
    groups = GoPhishGroupSerializer(many=True, required=False)
    timeline = GoPhishTimelineSerializer(many=True, required=False)
    target_email_list = SubscriptionTargetSerializer(many=True, required=False)
    smtp = GoPhishSmtpSerializer(required=False)


class GoPhishCampaignsResponseSerializer(serializers.Serializer):
    campaign_uuid = serializers.UUIDField()
