from api.utils import db_utils as db

from api.models.subscription_models import SubscriptionModel, validate_subscription


def push_webhook(subscription_uuid, campaign_id, email, message, time, details):
    data = {"email": email, "message": message, "time": time, "details": details}
    return db.push_nested_item(
        uuid=subscription_uuid,
        field="gophish_campaign_list.$.timeline",
        put_data=data,
        collection="subscription",
        model=SubscriptionModel,
        validation_model=validate_subscription,
        params={"gophish_campaign_list.campaign_id": campaign_id},
    )


def check_opened_event(timeline, email):
    opened = list(
        filter(
            lambda x: x["email"] == email and x["message"] == "Email Opened", timeline
        )
    )
    return bool(opened)
