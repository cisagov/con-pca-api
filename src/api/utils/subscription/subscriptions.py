"""Subscription Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser

# cisagov Libraries
from api.notifications import EmailSender
from api.services import SubscriptionService
from api.utils.subscription.static import (
    CYCLE_MINUTES,
    DELAY_MINUTES,
    MONTHLY_MINUTES,
    YEARLY_MINUTES,
)

subscription_service = SubscriptionService()


def create_subscription_name(customer: dict):
    """Create subscription name."""
    subscriptions = subscription_service.get_list(
        {"customer_uuid": str(customer["customer_uuid"])}, fields=["name", "identifier"]
    )

    if not subscriptions:
        return f"{customer['identifier']}_1"
    else:
        ids = [int(float(x["name"].split("_")[-1])) for x in subscriptions]
        return f"{customer['identifier']}_{max(ids) + 1}"


def calculate_subscription_start_end_date(start_date):
    """Calculate Subscription Start and End Date."""
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


def get_subscription_cycles(
    campaigns, start_date, end_date, new_uuid, total_targets_in_cycle
):
    """Get Initial Subscription Cycles."""
    campaigns_in_cycle = [c["campaign_id"] for c in campaigns]
    return [
        {
            "cycle_uuid": new_uuid,
            "start_date": start_date,
            "end_date": end_date,
            "active": True,
            "campaigns_in_cycle": campaigns_in_cycle,
            "total_targets": total_targets_in_cycle,
            "phish_results": {
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "submitted": 0,
                "reported": 0,
            },
        }
    ]


def send_stop_notification(subscription):
    """Send Stop Notification."""
    sender = EmailSender(subscription, "subscription_stopped")
    sender.send()


def init_subscription_tasks(start_date, continuous_subscription):
    """Create Initial Subscription Tasks."""
    message_types = {
        "start_subscription_email": start_date - timedelta(minutes=5),
        "monthly_report": start_date + timedelta(minutes=MONTHLY_MINUTES),
        "cycle_report": start_date + timedelta(minutes=CYCLE_MINUTES),
        "yearly_report": start_date + timedelta(minutes=YEARLY_MINUTES),
    }

    if continuous_subscription:
        message_types["start_new_cycle"] = start_date + timedelta(minutes=CYCLE_MINUTES)
    else:
        message_types["stop_subscription"] = start_date + timedelta(
            minutes=CYCLE_MINUTES
        )

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
    """
    Get Staggered Dates.

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


def add_remove_continuous_subscription_task(
    subscription_uuid, tasks, continuous_subscription
):
    """Change Continuous Subscription Task."""
    # If continuous subscription, change stop_subscription task to start_new_cycle
    if continuous_subscription:
        stop_task = next(
            filter(
                lambda x: x["message_type"] == "stop_subscription"
                and not x.get("executed"),
                tasks,
            ),
            None,
        )
        if stop_task:
            stop_task["message_type"] = "start_new_cycle"
            subscription_service.update_nested(
                uuid=subscription_uuid,
                field="tasks.$",
                data=stop_task,
                params={"tasks.task_uuid": stop_task["task_uuid"]},
            )
    # If not continuous subscription, change start_new_cycle task to stop_subscription
    else:
        new_cycle_task = next(
            filter(
                lambda x: x["message_type"] == "start_new_cycle"
                and not x.get("executed"),
                tasks,
            ),
            None,
        )
        if new_cycle_task:
            new_cycle_task["message_type"] = "stop_subscription"
            subscription_service.update_nested(
                uuid=subscription_uuid,
                field="tasks.$",
                data=new_cycle_task,
                params={"tasks.task_uuid": new_cycle_task["task_uuid"]},
            )
