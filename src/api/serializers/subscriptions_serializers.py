"""
Subscription Serializers.

These are Django Rest Framework Serializers. These are used for
serializing data coming from the db into a request response.
"""
# Third-Party Libraries
from api.serializers.customer_serializers import CustomerContactSerializer
from rest_framework import serializers


class SubscriptionEmailHistorySerializer(serializers.Serializer):
    """
    This is the Target Serializer.

    This formats the data coming out of the Db.
    """

    report_type = serializers.CharField(max_length=255)
    sent = serializers.DateTimeField()
    email_to = serializers.EmailField()
    email_from = serializers.CharField(max_length=255)
    bcc = serializers.EmailField(default=None)
    manual = serializers.BooleanField(default=False)


class SubscriptionTargetSerializer(serializers.Serializer):
    """
    This is the Target Serializer.

    This formats the data coming out of the Db.
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    position = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class SubscriptionClicksSerializer(serializers.Serializer):
    """
    This is the SubscriptionClicks Serializer.

    This formats the data coming out of the Db.
    """

    source_ip = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()
    target_uuid = serializers.UUIDField()


class GoPhishResultSerializer(serializers.Serializer):
    """
    This is the GoPhishResult Serializer.

    This formats the data coming out of the Db.
    """

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


class GoPhishGroupSerializer(serializers.Serializer):
    """
    This is the GoPhishGroup Serializer.

    This formats the data coming out of the Db.
    """

    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255)
    targets = SubscriptionTargetSerializer(many=True)
    modified_date = serializers.DateTimeField()


class GoPhishTimelineSerializer(serializers.Serializer):
    """
    This is the GoPhishTimeline Serializer.

    This formats the data coming out of the Db.
    """

    email = serializers.EmailField(required=False)
    time = serializers.DateTimeField()
    message = serializers.CharField(max_length=255)
    details = serializers.CharField(required=False)
    duplicate = serializers.BooleanField(required=False)


class PhishingResultsSerializer(serializers.Serializer):
    """
    This is the Phishing Results Serializer.

    This hold the results for each campaign. Filled by webhook response data
    """

    sent = serializers.IntegerField(default=0)
    opened = serializers.IntegerField(default=0)
    clicked = serializers.IntegerField(default=0)
    submitted = serializers.IntegerField(default=0)
    reported = serializers.IntegerField(default=0)


class GoPhishCampaignsSerializer(serializers.Serializer):
    """
    This is the GoPhishCampaigns Serializer.

    This formats the data coming out of the Db.
    """

    campaign_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=100)
    created_date = serializers.DateTimeField()
    launch_date = serializers.DateTimeField()
    send_by_date = serializers.DateTimeField(required=False)
    completed_date = serializers.DateTimeField(required=False)
    email_template = serializers.CharField(required=False)
    email_template_id = serializers.IntegerField(required=False)
    template_uuid = serializers.UUIDField()
    deception_level = serializers.IntegerField(required=False)
    landing_page_template = serializers.CharField(required=False)
    status = serializers.CharField(max_length=255)
    results = GoPhishResultSerializer(many=True)
    phish_results = PhishingResultsSerializer()
    groups = GoPhishGroupSerializer(many=True)
    timeline = GoPhishTimelineSerializer(many=True)
    target_email_list = SubscriptionTargetSerializer(many=True, required=False)


class CycleSerializer(serializers.Serializer):
    """Cycle Serializer.

    This is the Cycle serializer used for general reporting.
    """

    cycle_uuid = serializers.CharField(required=False)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    active = serializers.BooleanField()
    campaigns_in_cycle = serializers.ListField()
    phish_results = PhishingResultsSerializer()
    override_total_reported = serializers.IntegerField(default=-1)


class SubscriptionTasksSerializer(serializers.Serializer):
    """
    This is the SubscriptionTasks Serializer.

    This formats the data coming out of the Db.
    """

    task_uuid = serializers.CharField(required=False)
    message_type = serializers.CharField(required=False)
    scheduled_date = serializers.DateTimeField(required=False)
    executed = serializers.BooleanField(required=False)
    executed_date = serializers.DateTimeField(required=False)
    error = serializers.CharField(required=False)


# class GoPhishTemplateSerializer(serializers.Serializer):
#     """
#     This is the GoPhish Temaplates Serializer.

#     This is a formats the data coming out of the Db.
#     """
#     template_id = serializers.IntegerField(required=False)


class SubscriptionGetSerializer(serializers.Serializer):
    """
    This is the Subscription Serializer.

    This is a formats the data coming out of the Db.
    """

    # created by mongodb
    subscription_uuid = serializers.UUIDField()
    # values being passed in.
    customer_uuid = serializers.UUIDField()
    name = serializers.CharField(required=True, max_length=100)
    url = serializers.CharField(required=True, max_length=100)
    keywords = serializers.CharField(max_length=100)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField(required=False)
    gophish_campaign_list = GoPhishCampaignsSerializer(many=True)
    primary_contact = CustomerContactSerializer()
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(max_length=100)
    target_email_list = SubscriptionTargetSerializer(many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        many=True, required=False
    )
    templates_selected_uuid_list = serializers.ListField(required=False)
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField()
    archived = serializers.BooleanField(default=False)
    manually_stopped = serializers.BooleanField(default=False)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    cycles = CycleSerializer(many=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)
    # db data tracking added below
    created_by = serializers.CharField(max_length=100)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=100)
    lub_timestamp = serializers.DateTimeField()


class SubscriptionPostSerializer(serializers.Serializer):
    """
    This is the Subscription Post Request Serializer.

    This is a formats the data coming out of the Db.
    """

    customer_uuid = serializers.UUIDField()
    name = serializers.CharField(required=True, max_length=100)
    url = serializers.CharField(required=True, max_length=100)
    keywords = serializers.CharField(max_length=100)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField(required=False)
    gophish_campaign_list = GoPhishCampaignsSerializer(many=True)
    primary_contact = CustomerContactSerializer()
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(max_length=100)
    target_email_list = SubscriptionTargetSerializer(many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(many=True)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    templates_selected_uuid_list = serializers.ListField()
    sending_profile_name = serializers.CharField()
    active = serializers.BooleanField()
    archived = serializers.BooleanField(default=False)
    manually_stopped = serializers.BooleanField(default=False)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)


class SubscriptionPostResponseSerializer(serializers.Serializer):
    """
    This is the Subscription Post Response Serializer.

    This is a formats the data coming out of the Db.
    """

    subscription_uuid = serializers.UUIDField()
    name = serializers.CharField()


class SubscriptionPatchSerializer(serializers.Serializer):
    """
    This is the Subscription PATCH Request Serializer.

    This is a formats the data coming out of the Db.
    """

    customer_uuid = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False, max_length=100)
    url = serializers.CharField(required=False, max_length=100)
    keywords = serializers.CharField(required=False, max_length=100)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    gophish_campaign_list = GoPhishCampaignsSerializer(required=False, many=True)
    primary_contact = CustomerContactSerializer(required=False)
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(required=False, max_length=100)
    target_email_list = SubscriptionTargetSerializer(required=False, many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(
        required=False, many=True
    )
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    templates_selected_uuid_list = serializers.ListField(required=False)
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    archived = serializers.BooleanField(required=False, default=False)
    manually_stopped = serializers.BooleanField(required=False, default=False)
    cycles = CycleSerializer(required=False, many=True)
    email_report_history = SubscriptionEmailHistorySerializer(required=False, many=True)


class SubscriptionPatchResponseSerializer(serializers.Serializer):
    """
    This is the Subscription PATCH Response Serializer.

    This is a formats the data coming out of the Db.
    """

    subscription_uuid = serializers.UUIDField()
    customer_uuid = serializers.UUIDField()
    name = serializers.CharField(required=True, max_length=100)
    url = serializers.CharField(required=False, max_length=100)
    keywords = serializers.CharField(max_length=100)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    gophish_campaign_list = GoPhishCampaignsSerializer(many=True)
    primary_contact = CustomerContactSerializer()
    dhs_contact_uuid = serializers.UUIDField(required=False)
    status = serializers.CharField(max_length=100)
    target_email_list = SubscriptionTargetSerializer(many=True)
    target_email_list_cached_copy = SubscriptionTargetSerializer(many=True)
    tasks = SubscriptionTasksSerializer(many=True, required=False)
    templates_selected_uuid_list = serializers.ListField(required=False)
    sending_profile_name = serializers.CharField(required=False)
    active = serializers.BooleanField()
    archived = serializers.BooleanField(default=False)
    manually_stopped = serializers.BooleanField(default=False)
    created_by = serializers.CharField(max_length=100)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=100)
    lub_timestamp = serializers.DateTimeField()


class SubscriptionDeleteResponseSerializer(serializers.Serializer):
    """
    This is the Subscription DELETE Response Serializer.

    This is a formats the data coming out of the Db.
    """

    subscription_uuid = serializers.UUIDField()


class SubscriptionQuerySerializer(serializers.Serializer):
    """
    This is the Subscription Query Serializer.

    This is a formats query coming into for searching db.
    """

    customer_uuid = serializers.UUIDField()
    name = serializers.CharField(required=True, max_length=100)
    url = serializers.CharField(required=True, max_length=100)
    keywords = serializers.CharField(max_length=100)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField(required=False)
    status = serializers.CharField(max_length=100)
    templates_selected_uuid_list = serializers.ListField(required=False)
    dhs_contact_uuid = serializers.UUIDField(required=False)
    sending_profile_name = serializers.CharField()
    active = serializers.BooleanField()
    archived = serializers.BooleanField(default=False)
    manually_stopped = serializers.BooleanField(default=False)
    created_by = serializers.CharField(max_length=100)
    cb_timestamp = serializers.DateTimeField()
    last_updated_by = serializers.CharField(max_length=100)
    lub_timestamp = serializers.DateTimeField()
