"""Tasks."""
# Standard Python Libraries
from datetime import datetime, timedelta
import os
from uuid import uuid4

# Third-Party Libraries
import pytz  # type: ignore

# cisagov Libraries
from api.app import app
from api.manager import (
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TemplateManager,
)
from utils.logging import setLogger
from utils.mailgun import get_failed_email_events
from utils.notifications import Notification
from utils.safelist import generate_safelist_file
from utils.subscriptions import start_subscription, stop_subscription
from utils.templates import get_random_templates

# from utils.time import get_yearly_minutes

logger = setLogger(__name__)


cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
template_manager = TemplateManager()


def tasks_job():
    """Run subscription tasks."""
    with app.app_context():
        while True:
            subscription = get_subscription()
            if not subscription:
                logger.info("No more subscription tasks to process.")
                break
            process_subscription(subscription)


def failed_emails_job():
    """Job to gather failed emails every hour."""
    with app.app_context():
        get_failed_email_events()


def get_subscription():
    """Get and update cycle for processing."""
    return subscription_manager.find_one_and_update(
        params={
            "tasks": {
                "$elemMatch": {
                    "scheduled_date": {"$lt": datetime.utcnow()},
                    "executed": {"$in": [False, None]},
                }
            },
            "processing": {"$in": [False, None]},
        },
        data={"processing": True},
    )


def process_subscription(subscription):
    """Process subscription tasks."""
    cycle = cycle_manager.get(
        filter_data={
            "subscription_id": str(subscription["_id"]),
            "active": True,
        }
    )
    tasks = list(
        filter(
            lambda x: x["scheduled_date"].timestamp() < datetime.utcnow().timestamp()
            and not x.get("executed"),
            subscription.get("tasks", []),
        )
    )

    end_cycle_task = next(filter(lambda x: x["task_type"] == "end_cycle", tasks), None)
    for task in tasks:
        task["executed"] = True
        task["executed_date"] = datetime.utcnow()
        try:
            process_task(task, subscription, cycle) if task["scheduled_date"] > (
                datetime.now(pytz.utc) - timedelta(days=1)
            ) else None
        except Exception as e:
            logger.exception(
                f"An exception occurred performing {task['task_type']} task for {subscription['name']} subscription: {e}",
                extra={"source_type": "subscription", "source": subscription["_id"]},
            )
            task["error"] = str(e)
            subscription_manager.update(
                document_id=subscription["_id"],
                data={"processing": False},
                update=False,
            )

        if not end_cycle_task:
            update_task(subscription["_id"], task)
            add_new_task(subscription, cycle, task)
        logger.info(
            f"Executed task {task['task_type']} with subscription: {subscription['name']}"
        )

    subscription_manager.update(
        document_id=subscription["_id"], data={"processing": False}, update=False
    )

    cycle = cycle_manager.get(
        filter_data={
            "subscription_id": str(subscription["_id"]),
            "active": True,
        }
    )
    if cycle:
        cycle_manager.update(
            document_id=cycle["_id"],
            data={
                "tasks": subscription.get("tasks"),
            },
        )


def update_task(subscription_id, task):
    """Update subscription task."""
    subscription_manager.update_in_list(
        document_id=subscription_id,
        field="tasks.$",
        data=task,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(subscription, cycle, task):
    """Add new subscription task."""
    scheduled = task["scheduled_date"]
    # report_minutes = subscription["report_frequency_minutes"]
    cycle_minutes = (
        subscription["cycle_length_minutes"] + subscription["cooldown_minutes"]
    )
    # yearly_minutes = get_yearly_minutes()
    new_date = {
        # "status_report": scheduled + timedelta(minutes=report_minutes),
        # "yearly_report": scheduled + timedelta(minutes=yearly_minutes),
        "end_cycle": scheduled
        + timedelta(minutes=cycle_minutes),
    }.get(task["task_type"])
    if new_date:
        task = {
            "task_uuid": str(uuid4()),
            "task_type": task["task_type"],
            "scheduled_date": new_date,
            "executed": False,
        }
        logger.info(f"Adding new task {task}")

        return subscription_manager.add_to_list(
            document_id=subscription["_id"],
            field="tasks",
            data=task,
        )
    return None


def process_task(task, subscription, cycle):
    """Process subscription task."""
    task_types = {
        "start_subscription_email": start_subscription_email,
        "status_report": status_report,
        "cycle_report": cycle_report,
        # "yearly_report": yearly_report,
        "end_cycle": end_cycle,
        "start_next_cycle": end_cycle,
        "thirty_day_reminder": thirty_day_reminder,
        "fifteen_day_reminder": fifteen_day_reminder,
        "five_day_reminder": five_day_reminder,
        "safelisting_reminder": safelisting_reminder,
    }
    return task_types[task["task_type"]](subscription, cycle)


def start_subscription_email(subscription, cycle):
    """Send start subscription email."""
    Notification("subscription_started", subscription, cycle).send()


def status_report(subscription, cycle):
    """Send status report."""
    Notification("status_report", subscription, cycle).send()


def cycle_report(subscription, cycle):
    """Send cycle report."""
    Notification("cycle_report", subscription, cycle).send()


# def yearly_report(subscription, cycle):
#     """Send yearly report."""
#     # Notification("yearly_report", subscription, cycle).send()
#     return


def thirty_day_reminder(subscription, cycle):
    """Send thirty day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("thirty_day_reminder", subscription, cycle).send()


def fifteen_day_reminder(subscription, cycle):
    """Send fifteen day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("fifteen_day_reminder", subscription, cycle).send()


def five_day_reminder(subscription, cycle):
    """Send five day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("five_day_reminder", subscription, cycle).send()


def end_cycle(subscription, cycle):
    """End cycle by stopping or continuing new cycle."""
    if subscription.get("continuous_subscription"):
        stop_subscription(str(subscription["_id"]))
        # randomize templates between cycles
        if subscription.get("next_templates"):
            start_subscription(
                str(subscription["_id"]),
                templates_selected=subscription["next_templates"],
            )

        else:
            start_subscription(
                str(subscription["_id"]),
                templates_selected=get_random_templates(subscription),
            )
    else:
        stop_subscription(str(subscription["_id"]))
        Notification("subscription_stopped", subscription, cycle).send()


def safelisting_reminder(subscription, cycle):
    """Send safelisting reminder email."""
    sending_profiles = sending_profile_manager.all()

    templates = template_manager.all(
        params={"_id": {"$in": subscription["templates_selected"]}},
        fields=["subject", "deception_score"],
    )

    if not subscription.get("next_templates"):
        subscription["next_templates"] = get_random_templates(subscription)

    next_templates = template_manager.all(
        params={"_id": {"$in": subscription["next_templates"]}},
        fields=["subject", "deception_score"],
    )

    filepath = generate_safelist_file(
        subscription_id=subscription["_id"],
        phish_header=cycle["phish_header"],
        domains=[sp["from_address"].split("@")[1] for sp in sending_profiles],
        ips=[sp["sending_ips"] for sp in sending_profiles],
        templates=templates,
        next_templates=next_templates,
        reporting_password=subscription["reporting_password"],
        simulation_url=subscription.get("landing_domain", ""),  # simulated phishing url
    )

    if not os.path.exists(filepath):
        logger.error("Safelist file does not exist: " + filepath)
        return

    with app.app_context():
        Notification("safelisting_reminder", subscription, cycle).send(
            attachments=[filepath]
        )
