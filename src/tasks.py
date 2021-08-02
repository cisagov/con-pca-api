"""Scripts for running tasks."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser

# cisagov Libraries
from api.notifications import EmailSender
from api.services import CampaignService, SubscriptionService
from api.utils.subscription import actions
from api.utils.subscription.cycles import get_last_run_cycle
from api.utils.subscription.subscriptions import get_yearly_minutes

subscription_service = SubscriptionService()
campaign_service = CampaignService()


def main():
    """Start."""
    subscription_found = True
    while subscription_found:
        subscription = get_tasks()
        if subscription:
            logging.info(f"Processing subscription {subscription['subscription_uuid']}")
            process_tasks(subscription)
            subscription_service.update(
                subscription["subscription_uuid"],
                {"tasks_processing": False},
            )
        else:
            logging.info("No more subscriptions found to process.")
            subscription_found = False


def process_tasks(subscription):
    """Process all tasks that need executed on a subscription."""
    stopping = bool(
        list(
            filter(
                lambda x: x["message_type"] == "stop_subscription",
                subscription["tasks"],
            )
        )
    )
    for task in subscription["tasks"]:
        logging.info(f"Processing task - {task}")
        try:
            execute_task(subscription, task["message_type"])
            task["executed"] = True
            task["error"] = ""
            task["executed_date"] = datetime.now()
            if not stopping:
                update_task(subscription["subscription_uuid"], task)
                add_new_task(
                    subscription["subscription_uuid"],
                    task["scheduled_date"],
                    task["message_type"],
                    subscription.get("cycle_length_minutes", 129600),
                    subscription.get("cooldown_minutes", 2880),
                    subscription.get("report_frequency_minutes", 43200),
                )
            logging.info(f"Successfully executed task {task}")
        except Exception as e:
            logging.exception(e)
            task["executed"] = False
            task["error"] = str(e)
            task["scheduled_date"] = datetime.now() + timedelta(minutes=10)
            update_task(subscription["subscription_uuid"], task)


def get_tasks():
    """Return a subscription with just the tasks that need processing."""
    subscription = subscription_service.find_one_and_update(
        parameters={
            "tasks": {
                "$elemMatch": {
                    "scheduled_date": {"$lt": datetime.utcnow()},
                    "executed": {"$in": [False, None]},
                }
            },
            "tasks_processing": {"$in": [False, None]},
        },
        data={"tasks_processing": True},
    )
    if not subscription:
        return None
    tasks = []
    for task in subscription.get("tasks", []):
        scheduled_date = task.get("scheduled_date")
        if type(scheduled_date) is str:
            scheduled_date = dateutil.parser.parse(scheduled_date)
        executed = task.get("executed")
        if scheduled_date.replace(tzinfo=None) < datetime.utcnow() and not executed:
            tasks.append(task)
    if not tasks:
        return None
    subscription["tasks"] = tasks
    subscription["campaigns"] = campaign_service.get_list(
        parameters={"subscription_uuid": subscription["subscription_uuid"]}
    )
    return subscription


def update_task(subscription_uuid, task):
    """Update task in database."""
    """Update Subscription Task."""
    return subscription_service.update_nested(
        uuid=subscription_uuid,
        field="tasks.$",
        data=task,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(
    subscription_uuid,
    scheduled_date,
    message_type,
    cycle_length_minutes,
    cooldown_minutes,
    report_frequency_minutes,
):
    """Add new task."""
    logging.info("checking for new task to add")

    new_date = {
        "monthly_report": scheduled_date + timedelta(minutes=report_frequency_minutes),
        "cycle_report": scheduled_date
        + timedelta(minutes=(cycle_length_minutes + cooldown_minutes)),
        "yearly_report": scheduled_date + timedelta(minutes=get_yearly_minutes()),
        "start_new_cycle": scheduled_date
        + timedelta(minutes=(cycle_length_minutes + cooldown_minutes)),
    }.get(message_type)

    if new_date:
        task = {
            "task_uuid": str(uuid4()),
            "message_type": message_type,
            "scheduled_date": new_date,
            "executed": False,
            "queued": False,
        }

        logging.info(f"Adding new task {task}")

        return subscription_service.push_nested(
            uuid=subscription_uuid, field="tasks", data=task
        )

    return None


def execute_task(subscription, message_type):
    """Execute Task."""
    task = {
        "start_subscription": start_subscription,
        "start_subscription_email": start_subscription_email,
        "monthly_report": email_subscription_monthly,
        "cycle_report": email_subscription_cycle,
        "yearly_report": email_subscription_yearly,
        "start_new_cycle": start_subscription_cycle,
        "stop_subscription": stop_subscription,
    }
    task[message_type](subscription)


def start_subscription(subscription):
    """Start Subscription Task."""
    actions.start_subscription(subscription["subscription_uuid"])


def start_subscription_email(subscription):
    """Start Subscription Email Task."""
    sender = EmailSender(subscription, "subscription_started", None)
    sender.send()
    subscription_service.update(
        subscription["subscription_uuid"], {"status": "In Progress"}
    )


def start_subscription_cycle(subscription):
    """Start Subscription Cycle Task."""
    actions.start_subscription(subscription["subscription_uuid"], new_cycle=True)


def stop_subscription(subscription):
    """Stop Subscription Task."""
    actions.stop_subscription(subscription)


def email_subscription_monthly(subscription):
    """Email Monthly Report Task."""
    # Send email
    sender = EmailSender(
        subscription,
        "monthly_report",
        subscription["cycles"][-1]["cycle_uuid"],
    )
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_cycle(subscription):
    """Email Cycle Report Task."""
    # Send email
    selected_cycle = get_last_run_cycle(subscription["cycles"][-2:])

    sender = EmailSender(subscription, "cycle_report", selected_cycle["cycle_uuid"])
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_yearly(subscription):
    """Email Yearly Report Task."""
    # Send email
    cycle = subscription["cycles"][-1]["start_date"].isoformat()
    sender = EmailSender(subscription, "yearly_report", cycle["cycle_uuid"])
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context
