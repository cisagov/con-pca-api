from api.services import CampaignService

campaign_service = CampaignService()


def push_webhook(campaign_uuid, email, message, time, details):
    data = {"email": email, "message": message, "time": time, "details": details}

    return campaign_service.push_nested(
        uuid=campaign_uuid,
        field="timeline",
        data=data,
        options={hint: {campaign_uuid: 1}, upsert: False},
    )


def check_opened_event(timeline, email):
    opened = list(
        filter(
            lambda x: x["email"] == email and x["message"] == "Email Opened", timeline
        )
    )
    return bool(opened)
