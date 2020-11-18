"""Webhook Utils."""
# cisagov Libraries
from api.services import CampaignService

campaign_service = CampaignService()


def push_webhook(campaign_uuid, email, message, time, details):
    """Push Webhook."""
    data = {"email": email, "message": message, "time": time, "details": details}

    return campaign_service.push_nested(
        uuid=campaign_uuid,
        field="timeline",
        data=data,
    )


def check_opened_event(timeline, email):
    """Check Email Opened Event."""
    opened = list(
        filter(
            lambda x: x["email"] == email and x["message"] == "Email Opened", timeline
        )
    )
    return bool(opened)
