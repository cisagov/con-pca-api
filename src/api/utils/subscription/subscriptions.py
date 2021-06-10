"""Subscription Utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import math
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser
from django.core.handlers.base import logger

# cisagov Libraries
from api.notifications import EmailSender
from api.services import SubscriptionService
from config import settings

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


def calculate_subscription_start_end_date(start_date, cycle_length_minutes):
    """Calculate Subscription Start and End Date."""
    now = datetime.now()

    if not start_date:
        start_date = now.strftime("%Y-%m-%dT%H:%M:%S")

    if not isinstance(start_date, datetime):
        start_date = dateutil.parser.parse(start_date)

    start_date = start_date.replace(tzinfo=None)

    if start_date < now:
        start_date = now

    start_date = start_date + timedelta(minutes=settings.DELAY_MINUTES)
    end_date = start_date + timedelta(minutes=cycle_length_minutes)

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
    sender = EmailSender(subscription, "subscription_stopped", None)
    sender.send()


def init_subscription_tasks(start_date, continuous_subscription, cycle_length_minutes, report_length_minutes=0):
    """Create Initial Subscription Tasks."""
    if report_length_minutes == 0:
        report_length_minutes = cycle_length_minutes
    
    message_types = {
        "start_subscription_email": start_date - timedelta(minutes=5),
        "monthly_report": start_date
        + timedelta(minutes=get_monthly_minutes(cycle_length_minutes)),
        "cycle_report": start_date + timedelta(minutes=report_length_minutes),
        "yearly_report": start_date
        + timedelta(minutes=get_yearly_minutes(cycle_length_minutes)),
    }

    if continuous_subscription:
        message_types["start_new_cycle"] = start_date + timedelta(
            minutes=cycle_length_minutes
        )
    else:
        message_types["stop_subscription"] = start_date + timedelta(
            minutes=cycle_length_minutes
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


def get_monthly_minutes(cycle_minutes: int) -> int:
    """
    Get minutes for how often to send status reports.

    This is asking for cycle minutes, as there may be additional
    logic put in later that requires shorter intervals to send
    status reports based on cycle length.
    """
    return 43200  # month in minutes

def get_yearly_minutes(cycle_minutes: int) -> int:
    """
    Get minutes for how often to send yearly reports.

    This is asking for cycle minutes, as there may be additional
    logic put in later that requires shorter intervals to send
    yearly reports based on cycle length.
    """
    return 525600  # year in minutes


def get_campaign_minutes(cycle_minutes: int, reverse: bool = False) -> int:
    """
    Get minutes for a gophish campaign.

    A campaign should run 2/3 of the length of the cycle
    for reporting purposes and giving targets time to click links.

    If reverse is provided, you call function with campaign_minutes,
    and cycle minutes are instead returned.

    cycle_minutes * (2/3) = campaign_minutes
    campaign_minutes / (2/3) = cycle_minutes
    """
    if reverse:
        return math.ceil(cycle_minutes / (2 / 3))
    return int(cycle_minutes * 2 / 3)
