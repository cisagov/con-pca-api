from api.services import SubscriptionService

subscription_service = SubscriptionService()


def push_webhook(subscription_uuid, campaign_id, email, message, time, details):
    data = {"email": email, "message": message, "time": time, "details": details}
    return subscription_service.push_nested(
        uuid=subscription_uuid,
        field="gophish_campaign_list.$.timeline",
        data=data,
        params={"gophish_campaign_list.campaign_id": campaign_id},
    )


def check_opened_event(timeline, email):
    opened = list(
        filter(
            lambda x: x["email"] == email and x["message"] == "Email Opened", timeline
        )
    )
    return bool(opened)
