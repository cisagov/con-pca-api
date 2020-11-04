"""Subscription Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
from uuid import uuid4
import dateutil.parser

# Third-Party Libraries
from api.notifications import EmailSender
from api.utils.subscription.static import (
    CYCLE_MINUTES,
    MONTHLY_MINUTES,
    YEARLY_MINUTES,
    DELAY_MINUTES,
)
from api.services import SubscriptionService

subscription_service = SubscriptionService()


def create_subscription_name(customer: dict):
    """Returns a subscription name."""
    subscriptions = subscription_service.get_list(
        {"customer_uuid": str(customer["customer_uuid"])}
    )

    if not subscriptions:
        return f"{customer['identifier']}_1"
    else:
        ids = [int(float(x["name"].split("_")[-1])) for x in subscriptions]
        return f"{customer['identifier']}_{max(ids) + 1}"


def calculate_subscription_start_end_date(start_date):
    """Calculates the start and end date for subscription from given start date."""
    now = datetime.now()

    if not start_date:
        start_date = now.strftime("%Y-%m-%dT%H:%M:%S")

    if not isinstance(start_date, datetime):
        start_date = dateutil.parser.parse(start_date)

    start_date = start_date.replace(tzinfo=None)

    if start_date < now:
        start_date = now

    start_date = start_date + timedelta(minutes=DELAY_MINUTES)
    end_date = start_date + timedelta(minutes=CYCLE_MINUTES)

    return start_date, end_date


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
    sender = EmailSender(subscription, "subscription_started")
    sender.send()


def send_stop_notification(subscription):
    """Send Stop Notification.

    Args:
        subscription (dict): subscription data
    """
    sender = EmailSender(subscription, "subscription_stopped")
    sender.send()


def init_subscription_tasks(start_date):
    message_types = {
        "start_subscription_email": start_date - timedelta(minutes=5),
        "monthly_report": start_date + timedelta(minutes=MONTHLY_MINUTES),
        "cycle_report": start_date + timedelta(minutes=CYCLE_MINUTES),
        "yearly_report": start_date + timedelta(minutes=YEARLY_MINUTES),
        "start_new_cycle": start_date + timedelta(minutes=CYCLE_MINUTES),
    }

    tasks = []
    for message_type, send_date in message_types.items():
        tasks.append(
            {
                "task_uuid": str(uuid4()),
                "message_type": message_type,
                "scheduled_date": send_date,
                "executed": False,
            }
        )

    return tasks


def get_staggered_dates_in_range(start, intv):
    """Get Staggered Dates

    Takes range of dates and gets N dates within them, returns a list of dates.

    Args:
        start (datetime): starting date of subscription
        intv (int): number of inteval dates

    Returns:
        list[datetime]: list of N dates where N=intv
    """
    date_list = []
    for i in range(intv):
        date_list.append(start + timedelta(hours=i))
    return date_list
