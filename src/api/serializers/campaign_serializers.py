"""
GoPhish Campaign Serializers.

These are Django Rest Framework Serializers.
These are used for serializing data coming in from gophish.
API Docs:
https://docs.getgophish.com/api-documentation/campaigns
"""
# Third-Party Libraries
from rest_framework import serializers


class CampaignResultSerializer(serializers.Serializer):
    """
    Campaign Results Serializer.

    This is the data returned from Gophish's Campaigns API

    id                   : string
    first_name           : string
    last_name            : string
    position             : string
    status               : string
    ip                   : string
    latitude             : float
    longitude            : float
    send_date            : string(datetime)
    reported             : boolean
    """

    id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    position = serializers.CharField()
    status = serializers.CharField()
    ip = serializers.CharField()
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    send_date = serializers.DateTimeField(required=False)
    reported = serializers.BooleanField(required=False)


class CampaignGroupTargetSerializer(serializers.Serializer):
    """
    Campaign Group Target Serializer.

    This is the data returned from Gophish's Campaigns API

    email           : string
    first_name      : string
    last_name       : string
    position        : string
    """

    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    position = serializers.CharField()


class CampaignGroupSerializer(serializers.Serializer):
    """
    Campaign Groups Serializer.

    This is the data returned from Gophish's Campaigns API

    id              : int64
    name            : string
    targets         : array(Target)
    modified_date   : string(datetime)
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)
    targets = CampaignGroupTargetSerializer(many=True)
    modified_date = serializers.DateTimeField()


class CampaignEventSerializer(serializers.Serializer):
    """
    Campaign Events Serializer.

    This is the data returned from Gophish's Campaigns API

    email                : string
    time                 : string(datetime)
    message              : string
    details              : string(JSON)
    """

    email = serializers.EmailField()
    time = serializers.DateTimeField()
    message = serializers.CharField()
    details = serializers.CharField()


class CampaignSerializer(serializers.Serializer):
    """
    Campaign Serializer.

    This is the data returned from Gophish's Campaigns API

    id                  : int64
    name                : string
    created_date        : string(datetime)
    launch_date         : string(datetime)
    send_by_date        : string(datetime)
    completed_date      : string(datetime)
    template            : Template
    page                : Page
    status              : string
    results             : []Result
    groups              : []Group
    timeline            : []Event
    smtp                : SMTP
    url                 : string
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=250)
    created_date = serializers.DateTimeField()
    launch_date = serializers.DateTimeField()
    send_by_date = serializers.DateTimeField()
    completed_date = serializers.DateTimeField()
    status = serializers.CharField(max_length=50)
    url = serializers.CharField()
    results = CampaignResultSerializer(many=True)
    groups = CampaignGroupSerializer(many=True)
    timeline = CampaignEventSerializer(many=True)
