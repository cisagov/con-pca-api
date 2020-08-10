"""Subscription Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings

# Third-Party Libraries
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.utils import db_utils as db
from notifications.views import SubscriptionNotificationEmailSender


def get_subscription(subscription_uuid: str):
    """Returns a subscription from database."""
    return db.get_single(
        subscription_uuid, "subscription", SubscriptionModel, validate_subscription
    )


def get_subscriptions(sub_filter=None):
    """Returns list of subscriptions from database."""
    return db.get_list(
        sub_filter, "subscription", SubscriptionModel, validate_subscription
    )


def create_subscription_name(customer: dict):
    """Returns a subscription name."""
    subscription_list = get_subscriptions({"customer_uuid": customer["customer_uuid"]})

    if not subscription_list:
        base_name = f"{customer['identifier']}_1.1"
    else:
        names = [x["name"] for x in subscription_list]
        list_tupe = []
        for name in names:
            int_ind, sub_id = name.rsplit(".", 1)
            _, sub = int_ind.rsplit("_", 1)
            list_tupe.append((sub, sub_id))
        # now sort tuple list by second element
        list_tupe.sort(key=lambda tup: tup[1])
        # get last run inc values
        last_ran_x, last_ran_y = list_tupe[-1]

        # now check to see there are any others running during.
        active_subscriptions = [x for x in subscription_list if x["active"]]
        if len(active_subscriptions) <= 0:
            # if none are active, check last running number and create new name
            next_run_x, next_run_y = "1", str(int(last_ran_y) + 1)
        else:
            next_run_x, next_run_y = str(int(last_ran_x) + 1), last_ran_y

        base_name = f"{customer['identifier']}_{next_run_x}.{next_run_y}"

    return base_name


def calculate_subscription_start_end_date(start_date):
    """Calculates the start and end date for subscription from given start date."""
    date = start_date
    now = datetime.now()

    if not date:
        date = now.strftime("%Y-%m-%dT%H:%M:%S")

    if not isinstance(date, datetime):
        start_date = datetime.strptime(date.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        if start_date < now:
            start_date = now
    else:
        start_date = now

    end_date = start_date + timedelta(days=90)
    start_date = start_date + timedelta(minutes=1)

    return start_date, end_date


def get_subscription_status(start_date):
    """Returns status for subscription based upon start date."""
    if start_date <= datetime.now():
        return "In Progress"
    else:
        return "Queued"


def get_subscription_cycles(campaigns, start_date, end_date, new_uuid):
    """Returns cycle data for a subscription."""
    campaigns_in_cycle = [c["campaign_id"] for c in campaigns]
    return [
        {
            "cycle_uuid": new_uuid,
            "start_date": start_date,
            "end_date": end_date,
            "active": True,
            "campaigns_in_cycle": campaigns_in_cycle,
            "phish_results": {
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "submitted": 0,
                "reported": 0,
            },
        }
    ]


def send_start_notification(subscription):
    """Send Start Notification.

    Args:
        subscription (dict): subscription data
        start_date (datetime): start_date of subscription
    """
    add_email_report_history(subscription, "Cycle Start Notification")
    sender = SubscriptionNotificationEmailSender(subscription, "subscription_started")
    sender.send()


def add_email_report_history(subscription, report_type):
    dhs_contact = db.get_single(
        subscription.get("dhs_contact_uuid"),
        "dhs_contact",
        DHSContactModel,
        validate_dhs_contact,
    )

    data = {
        "report_type": report_type,
        "sent": datetime.now(),
        "email_to": subscription.get("primary_contact").get("email"),
        "email_from": settings.SERVER_EMAIL,
        "bbc": dhs_contact.get("email") if dhs_contact else None,
    }

    return db.push_nested_item(
        uuid=subscription["subscription_uuid"],
        field="email_report_history",
        put_data=data,
        collection="subscription",
        model=SubscriptionModel,
        validation_model=validate_subscription,
    )


def send_stop_notification(subscription):
    """Send Stop Notification.

    Args:
        subscription (dict): subscription data
    """
    sender = SubscriptionNotificationEmailSender(subscription, "subscription_stopped")
    sender.send()


def create_scheduled_email_tasks(start_date):
    """Create Scheduled Email Tasks.

    Returns:
        list: list of tasks and message types
    """
    message_types = {
        "start_subscription_email": start_date - timedelta(minutes=5),
        "monthly_report": start_date + timedelta(days=30),
        "cycle_report": start_date + timedelta(days=90),
        "yearly_report": start_date + timedelta(days=365),
    }

    context = []
    for message_type, send_date in message_types.items():
        context.append(
            {
                "task_uuid": uuid4(),
                "message_type": message_type,
                "scheduled_date": send_date,
                "executed": False,
            }
        )

    return context


def create_scheduled_cycle_tasks(start_date):
    send_date = start_date + timedelta(days=90)

    return {
        "task_uuid": uuid4(),
        "message_type": "start_new_cycle",
        "scheduled_date": send_date,
        "executed": False,
    }
