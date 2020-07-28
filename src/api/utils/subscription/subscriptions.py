"""Subscription Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging
from uuid import uuid4

# Third-Party Libraries
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.utils import db_utils as db
from notifications.views import SubscriptionNotificationEmailSender

logger = logging.getLogger()


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
            int_ind, sub_id = name.split(".")
            _, sub = int_ind.split("_")
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

    return start_date, end_date


def get_subscription_status(start_date):
    """Returns status for subscription based upon start date."""
    if start_date <= datetime.now():
        return "In Progress"
    else:
        return "Queued"


def get_subscription_cycles(campaigns, start_date, end_date):
    """Returns cycle data for a subscription."""
    campaigns_in_cycle = [c["campaign_id"] for c in campaigns]
    return [
        {
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


def send_start_notification(subscription, start_date):
    """Send Start Notification.

    Args:
        subscription (dict): subscription data
        start_date (datetime): start_date of subscription
    """
    if start_date <= datetime.now():
        sender = SubscriptionNotificationEmailSender(
            subscription, "subscription_started"
        )
        sender.send()


def send_stop_notification(subscription):
    """Send Stop Notification.

    Args:
        subscription (dict): subscription data
    """
    sender = SubscriptionNotificationEmailSender(subscription, "subscription_stopped")
    sender.send()


def create_scheduled_email_tasks():
    """Create Scheduled Email Tasks.

    Returns:
        list: list of tasks and message types
    """
    message_types = {
        "monthly_report": datetime.utcnow() + timedelta(days=30),
        "cycle_report": datetime.utcnow() + timedelta(days=90),
        "yearly_report": datetime.utcnow() + timedelta(days=365),
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


def create_scheduled_cycle_tasks():
    send_date = datetime.utcnow() + timedelta(days=90)

    return {
        "task_uuid": uuid4(),
        "message_type": "start_new_cycle",
        "scheduled_date": send_date,
        "executed": False,
    }
